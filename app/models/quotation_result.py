from typing import Optional
from pydantic import BaseModel


class Tarifa(BaseModel):
    valor: float
    descricao: str

class Error(BaseModel):
    codigo: str
    mensagem: str

class Alertas(BaseModel):
    alertas: Optional[list[str]]

class KanguData(BaseModel):
    vlrFrete: float
    prazoEnt: int
    prazoEntMin: int
    dtPrevEnt: str
    dtPrevEntMin: str
    tarifas: list[Tarifa]
    error: Error
    idSimulacao: int
    idTransp: int
    cnpjTransp: str
    idTranspResp: int
    cnpjTranspResp: str
    nf_obrig: str
    url_logo: str
    transp_nome: str
    descricao: str
    servico: str
    referencia: str

class QuotationResult(BaseModel):
    data: list[KanguData]
