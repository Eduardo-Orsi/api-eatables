from pydantic import BaseModel


class Platform(BaseModel):
    name: str
    external_id: int


class Sku(BaseModel):
    id: int
    product_id: int
    sku: str
    price: float
    quantity: int
    length: float
    width: float
    height: float
    weight: float
    availability_days: int
    platform: Platform


class ShippingInfo(BaseModel):
    zipcode: str
    amount: float
    skus: list[Sku]
