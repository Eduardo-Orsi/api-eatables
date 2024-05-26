import requests
from ..models.address import Address


class CEP:

    @staticmethod
    async def get_address_from_cep(cep: str) -> Address:
        response = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=None)
        try:
            return Address(**response.json())
        except:
            return Address(
                cep="41311486",
                logradouro="Travessa das Palmeiras de Cajazeiras",
                bairro="Águas Claras",
                uf="BA",
                complemento=None,
                localidade=None,
                ibge=None,
                ddd=None,
                gia=None,
                siafi=None
            )
