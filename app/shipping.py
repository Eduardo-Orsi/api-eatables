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
from .integration.yampi import Yampi
from .integration.mailchimp import MailChimp
from .utils.error_kangu import basic_quotation_error
from .utils.cep import CEP


load_dotenv()
KANGU_API_URL = str(os.getenv("KANGU_API_URL"))
KANGU_API_KEY = os.getenv("KANGU_API_KEY")
SECRET_CODE = os.getenv("SECRET_CODE")
YAMPI_WEBHOOK_SIGNATURE = str(os.getenv("YAMPI_WEBHOOK_SIGNATURE"))
YAMPI_SHIPPING_SIGNATURE = str(os.getenv("YAMPI_SHIPPING_SIGNATURE"))

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"\nValidation error: {exc}\n")
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

    header = {"token": KANGU_API_KEY}
    response = requests.get(KANGU_API_URL, headers=header, data=request_shipping.model_dump_json(), timeout=4)

    if response.status_code != 200:
        return basic_quotation_error(address=address)

    quantity = request_shipping.volumes[0].quantidade
    quotation_result = QuotationResult(data=response.json())
    quotation_response = QuoteResponse.load_from_quotation_result(quotation_result, quantity, address)
    return quotation_response


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
