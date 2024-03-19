import os
from typing import Annotated

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Header

from .models.shipping_info import ShippingInfo
from .models.quote_response import QuoteResponse
from .models.quotation_result import QuotationResult
from .models.shipping_quotation import RequestShippingQuotation
from .models.abandoned_cart import YampiEvent

from .integration.mailchimp import MailChimp
from .integration.yampi import Yampi


load_dotenv()
KANGU_API_URL = os.getenv("KANGU_API_URL")
KANGU_API_KEY = os.getenv("KANGU_API_KEY")
SECRET_CODE = os.getenv("SECRET_CODE")
YAMPI_WEBHOOK_SIGNATURE = os.getenv("YAMPI_WEBHOOK_SIGNATURE")

app = FastAPI()


@app.post("/shipping/")
async def shipping(shipping_info: ShippingInfo, secret_code: Annotated[str | None, Header()] = None):

    if not secret_code == SECRET_CODE:
        raise HTTPException(status_code=404, detail="Secret Code not found")

    request_shipping = RequestShippingQuotation.load_from_shipping_info(shipping_info)

    header = {"token": KANGU_API_KEY}
    response = requests.get(KANGU_API_URL, headers=header, data=request_shipping.model_dump_json(), timeout=None)

    quotation_result = QuotationResult(data=response.json())
    return QuoteResponse.load_from_quotation_result(quotation_result)


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
