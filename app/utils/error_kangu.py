from ..models.address import Address
from ..models.quote_response import Quote, QuoteResponse
from ..utils.shipping_score import ShippingScore


DISCOUNT_STATES = ['RS', 'SC', 'PR', 'SP', 'RJ', 'MG']

def basic_quotation_error(address: Address, quantity: int) -> QuoteResponse:
    basic_quote = Quote(
        name="Loggi",
        service="kangu_E_20999999999988",
        price=9.90,
        days=6,
        quote_id=None
    )

    fast_quote = Quote(
        name="Correios SEDEX",
        service="kangu_X_99999999000000",
        price=39.90,
        days=3,
        quote_id=None
    )

    if address.uf not in DISCOUNT_STATES:
        fast_quote.days = 4

    response = ShippingScore.select_best_quotations([fast_quote, basic_quote], address=address)
    return QuoteResponse(quotes=response)
