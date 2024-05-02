from ..models.address import Address
from ..models.quote_response import Quote


DISCOUNT_STATES = ['RS', 'SC', 'PR', 'SP', 'RJ', 'MG']

class ShippingScore:

    @staticmethod
    def calculate_best_score(quotation: Quote) -> float:
        price_weight = 0.9
        time_weight = 0.1
        total_weight = price_weight + time_weight
        normalized_price_weight = price_weight / total_weight
        normalized_time_weight = time_weight / total_weight
        return (normalized_price_weight * quotation.price) + (normalized_time_weight * ( quotation.days))

    @staticmethod
    def calculate_fastest_score(quotation: Quote) -> int:
        return quotation.days

    @staticmethod
    def select_best_quotations(quotations: list[Quote], address: Address) -> list[Quote]:
        quotations = [quote for quote in quotations if quote.name != "Correios PAC"]
        sorted_by_best_score = sorted(quotations, key=lambda x: ShippingScore.calculate_best_score(x))
        sorted_by_fastest_score = sorted(quotations, key=lambda x: ShippingScore.calculate_fastest_score(x))

        best_quote = sorted_by_best_score[0]
        fastest_quote = sorted_by_fastest_score[0]

        for quote in quotations:
            if quote.name == "Loggi":
                best_quote = quote

        if best_quote.service == fastest_quote.service:
            best_quote = sorted_by_best_score[1]

        best_quote.name = f"FRETE EXPRESSO"
        fastest_quote.name = f"FRETE ULTRA EXPRESSO"

        if address.uf in DISCOUNT_STATES:
            best_quote.price = 9.90
        else:
            best_quote.price = best_quote.price * 0.75

        print(f"Best Quote: {best_quote}")
        print(f"Fast Quote: {fastest_quote}")

        return [best_quote, fastest_quote]
