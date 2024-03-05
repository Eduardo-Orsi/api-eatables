from typing import Annotated

import requests
from fastapi import FastAPI, Header, HTTPException

from .models.shipping_info import ShippingInfo
from .models.quote_response import QuoteResponse
from .models.quotation_result import QuotationResult
from .models.shipping_quotation import RequestShippingQuotation


KANGU_API_URL = "https://portal.kangu.com.br/tms/transporte/simular"

app = FastAPI()


@app.post("/shipping/")
async def shipping(shipping_info: ShippingInfo, secret_code: Annotated[str | None, Header()] = None):

    if not secret_code == SECRET_CODE:
        raise HTTPException(status_code=404, detail="Secret Code not found")

    request_shipping = RequestShippingQuotation.load_from_shipping_info(shipping_info)

    header = {"token": API_KEY}
    response = requests.get(KANGU_API_URL, headers=header, data=request_shipping.model_dump_json(), timeout=None)

    quotation_result = QuotationResult(data=response.json())
    return QuoteResponse.load_from_quotation_result(quotation_result)
