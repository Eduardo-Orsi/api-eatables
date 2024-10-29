from pydantic import BaseModel


class Address(BaseModel):
    cep: str
    logradouro: str
    complemento: str | None
    bairro: str
    localidade: str | None
    uf: str
    ibge: str | None
    gia: str | None
    ddd: str | None
    siafi: str | None
