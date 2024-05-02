from typing import Optional
from pydantic import BaseModel
from .address import Address
from .quotation_result import QuotationResult


class Quote(BaseModel):
    name: str
    service: str
    price: float
    days: int
    quote_id: Optional[int]


class QuoteResponse(BaseModel):
    quotes: list[Quote]

    @classmethod
    def load_from_quotation_result(cls, quotation_result: QuotationResult,
                                   quantity: int, address: Address) -> "QuoteResponse":
        from ..utils.shipping_score import ShippingScore
        quotes = []
        fastest_quote = None
        cheapest_quote = None

        for quote in quotation_result.data:
            current_quote = Quote(
                name=quote.transp_nome,
                service=quote.referencia,
                price=quote.vlrFrete,
                days=quote.prazoEntMin,
                quote_id=quote.idSimulacao
            )
            quotes.append(current_quote)

        response = ShippingScore.select_best_quotations(quotes, address)
        return QuoteResponse(quotes=response)
