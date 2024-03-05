from pydantic import BaseModel
from .shipping_info import ShippingInfo


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
    produtos: list[Produto]
    servicos: list[str]
    ordernar: str

    @classmethod
    def load_from_shipping_info(cls, shipping_info: ShippingInfo) -> "RequestShippingQuotation":
        products = []
        love_chocolate_quantity = 0
        for sku in shipping_info.skus:
            products.append(
                Produto(
                    peso=sku.weight,
                    altura=sku.height,
                    largura=sku.width,
                    comprimento=sku.length,
                    valor=sku.price,
                    quantidade=sku.quantity
                )
            )

            if sku.sku == "LOVCHOBOX":
                love_chocolate_quantity = sku.quantity

        altura = 4
        largura = 16
        peso = 0.3
        if love_chocolate_quantity >= 2:
            altura = 19
            largura = 13
            peso = 0.4

        volume = Volume(
            peso=peso,
            altura=altura,
            largura=largura,
            comprimento=22,
            tipo="caixa",
            valor=shipping_info.amount,
            quantidade=1
        )

        return RequestShippingQuotation(
            cepOrigem="88331085",
            cepDestino=shipping_info.zipcode,
            vlrMerc=shipping_info.amount,
            pesoMerc=peso,
            volumes=[volume],
            produtos=products,
            servicos=["E", "X"],
            ordernar=""
        )
