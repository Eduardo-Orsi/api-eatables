import requests
from ..models.address import Address


class CEP:

    @staticmethod
    async def get_address_from_cep(cep: str) -> Address:
        response = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=None)
        return Address(**response.json())
