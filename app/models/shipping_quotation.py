import os
from enum import Enum
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel
from .shipping_info import ShippingInfo


load_dotenv()
SOURCE_ZIP_CODE = os.getenv("SOURCE_ZIP_CODE")


class ShippingBox(Enum):
    HEIGHT = 6
    WIDTH = 16
    LENGTH = 22


class Volume(BaseModel):
    peso: float
    altura: int
    largura: int
    comprimento: int
    tipo: str = ""
    valor: float
    quantidade: int


class Produto(BaseModel):
    peso: float
    altura: int
    largura: int
    comprimento: int
    valor: float
    quantidade: int


class RequestShippingQuotation(BaseModel):
    cepOrigem: str
    cepDestino: str
    vlrMerc: float
    pesoMerc: float
    volumes: list[Volume]
    produtos: Optional[list[Produto]]
    servicos: list[str]
    ordernar: Optional[str]

    @classmethod
    def load_from_shipping_info(cls, shipping_info: ShippingInfo) -> "RequestShippingQuotation":
        products = []
        love_chocolate_quantity = 0
        peso = 0
        for sku in shipping_info.skus:
            peso = peso + sku.weight

            if sku.sku == "LOVCHOBOX":
                love_chocolate_quantity = sku.quantity

        volume = Volume(
            peso=peso,
            altura=ShippingBox.HEIGHT.value,
            largura=ShippingBox.WIDTH.value,
            comprimento=ShippingBox.LENGTH.value,
            tipo="C",
            valor=shipping_info.amount,
            quantidade=love_chocolate_quantity
        )

        return RequestShippingQuotation(
            cepOrigem=SOURCE_ZIP_CODE,
            cepDestino=shipping_info.zipcode,
            vlrMerc=shipping_info.amount,
            pesoMerc=peso,
            volumes=[volume],
            produtos=products,
            servicos=["E", "X"],
            ordernar="preco"
        )
