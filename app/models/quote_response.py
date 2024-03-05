from typing import Optional
from pydantic import BaseModel
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
    def load_from_quotation_result(cls, quotation_result: QuotationResult) -> "QuoteResponse":
        quotes = []
        for quote in quotation_result.data:
            quotes.append(
                Quote(
                    name=quote.transp_nome,
                    service=quote.transp_nome.replace(" ", "_") + "_Kangu",
                    price=quote.vlrFrete,
                    days=quote.prazoEntMin,
                    quote_id=quote.idSimulacao
                )
            )
        return QuoteResponse(quotes=quotes)
