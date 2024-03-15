import os
from typing import Annotated

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Header

from .models.shipping_info import ShippingInfo
from .models.quote_response import QuoteResponse
from .models.quotation_result import QuotationResult
from .models.shipping_quotation import RequestShippingQuotation
from .models.abandoned_cart import YampiEvent

from .integration.mailchimp import MailChimp


load_dotenv()
KANGU_API_URL = os.getenv("KANGU_API_URL")
KANGU_API_KEY = os.getenv("KANGU_API_KEY")
SECRET_CODE = os.getenv("SECRET_CODE")

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
async def webhook_yampi(yampi_event: YampiEvent, secret_code: Annotated[str | None, Header()] = None):

    if not secret_code == SECRET_CODE:
        raise HTTPException(status_code=404, detail="Secret Code not found")

    mailchimp = MailChimp()
    response = mailchimp.add_abandoned_cart_contact(yampi_event.resource.customer.data,
                                                    yampi_event.resource.search.data.abandoned_step)
    return response
