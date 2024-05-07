import re
from typing import Optional
from pydantic import BaseModel
from .address import Address
from .quotation_result import QuotationResult


def clean_reference(reference: str) -> str:
    """
    Cleans the reference string by keeping only the first three parts separated by underscores.

    Args:
        reference (str): The original reference string.

    Returns:
        str: The cleaned reference string.
    """
    reference_parts = reference.split("_")
    cleaned_reference = "_".join(reference_parts[:3])
    return cleaned_reference

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
                service=clean_reference(quote.referencia),
                price=quote.vlrFrete,
                days=quote.prazoEntMin,
                quote_id=quote.idSimulacao
            )
            quotes.append(current_quote)

        response = ShippingScore.select_best_quotations(quotes, address)
        if quantity >= 2:
            response[0].price = 0.0

        return QuoteResponse(quotes=response)
