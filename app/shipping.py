import os
from typing import Annotated

import requests
from dotenv import load_dotenv
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, HTTPException, Request, Header

from .models.abandoned_cart import YampiEvent
from .models.shipping_info import ShippingInfo
from .models.quote_response import QuoteResponse
from .models.quotation_result import QuotationResult
from .models.shipping_quotation import RequestShippingQuotation
from .models.article import PostWrapper, AutomarticlesCheck
from .integration.yampi import Yampi
from .integration.mailchimp import MailChimp
from .integration.shopify import ShopifyIntegration
from .utils.error_kangu import basic_quotation_error
from .utils.cep import CEP


load_dotenv()
KANGU_API_URL = str(os.getenv("KANGU_API_URL"))
KANGU_API_KEY = os.getenv("KANGU_API_KEY")
SECRET_CODE = os.getenv("SECRET_CODE")
YAMPI_WEBHOOK_SIGNATURE = str(os.getenv("YAMPI_WEBHOOK_SIGNATURE"))
YAMPI_SHIPPING_SIGNATURE = str(os.getenv("YAMPI_SHIPPING_SIGNATURE"))
AUTOMARTICLES_TOKEN = os.getenv("AUTOMARTICLES_TOKEN")

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # print(f"\nValidation error: {exc}\n")
    raise HTTPException(status_code=422, detail=exc.errors())

@app.post("/shipping/")
async def shipping(shipping_info: ShippingInfo, request: Request, secret_code: Annotated[str | None, Header()] = None, x_yampi_hmac_sha256: Annotated[str | None, Header()] = None):
    body = await request.body()
    await Yampi.validate_webhook_signature(body,
                                        x_yampi_hmac_sha256,
                                        YAMPI_SHIPPING_SIGNATURE)

    if not secret_code == SECRET_CODE:
        raise HTTPException(status_code=404, detail="Secret Code not found")

    address = await CEP.get_address_from_cep(shipping_info.zipcode)
    request_shipping = RequestShippingQuotation.load_from_shipping_info(shipping_info)

    try:
        header = {"token": KANGU_API_KEY}
        response = requests.get(KANGU_API_URL, headers=header, data=request_shipping.model_dump_json(), timeout=4)
    except Exception as ex:
        print(f"KANGU API ERROR - {ex}")
        return basic_quotation_error(address=address)

    quantity = request_shipping.volumes[0].quantidade

    try:
        quotation_result = QuotationResult(data=response.json())
    except Exception:
        print("VALIDATION ERROR")
        return basic_quotation_error(address=address)

    quotation_response = QuoteResponse.load_from_quotation_result(quotation_result, quantity, address)
    return quotation_response


@app.post("/webhook/automarticles/article/")
async def webhook_article(post_wrapper: PostWrapper, access_token: Annotated[str | None, Header()] = None):

    if not access_token == AUTOMARTICLES_TOKEN:
        raise HTTPException(status_code=404, detail="Access Token not found")

    if post_wrapper.event == "CHECK_INTEGRATION":
        return {"token": AUTOMARTICLES_TOKEN}

    shopify = ShopifyIntegration("https://de9306.myshopify.com/", "2024-01")

    if post_wrapper.event in ["POST_CREATED", "POST_UPDATED"]:
        return await shopify.add_article(post_wrapper)
    return {}


@app.post("/webhook/yampi/")
async def webhook_yampi(yampi_event: YampiEvent, request: Request, x_yampi_hmac_sha256: Annotated[str | None, Header()] = None):
    body = await request.body()
    await Yampi.validate_webhook_signature(body,
                                        x_yampi_hmac_sha256,
                                        YAMPI_WEBHOOK_SIGNATURE)

    mailchimp = MailChimp()
    response =  await mailchimp.add_abandoned_cart_contact(yampi_event.resource.customer.data,
                                                    yampi_event.resource.search.data.abandoned_step)
    return response
