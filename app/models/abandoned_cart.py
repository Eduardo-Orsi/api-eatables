from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, HttpUrl, IPvAnyAddress


class Phone(BaseModel):
    full_number: str
    area_code: str
    number: str
    formated_number: str
    whatsapp_link: HttpUrl


class Timestamp(BaseModel):
    date: datetime
    timezone_type: int
    timezone: str


class Customer(BaseModel):
    id: int
    merchant_id: int
    marketplace_id: Optional[int]
    cluster_id: Optional[int]
    active: bool
    type: str
    name: str
    razao_social: Optional[str]
    first_name: str
    last_name: str
    generic_name: str
    email: EmailStr
    cnpj: Optional[str]
    state_registration: Optional[str]
    cpf: Optional[str]
    birthday: Optional[str]
    phone: Phone
    social_driver: Optional[str]
    social_id: Optional[str]
    newsletter: bool
    whatsapp: bool
    utm_source: Optional[str]
    utm_campaign: Optional[str]
    ip: Optional[IPvAnyAddress]
    notes: Optional[str]
    token: str
    login_url: Optional[HttpUrl]
    anonymized: bool
    created_at: Timestamp
    updated_at: Timestamp


class CustomerData(BaseModel):
    data: Customer


class SKU(BaseModel):
    id: int
    product_id: int
    sku: str
    title: str
    price_sale: float
    price_discount: float
    created_at: Timestamp
    updated_at: Timestamp
    customizations: dict


class SKUData(BaseModel):
    data: SKU


class Item(BaseModel):
    id: int
    product_id: int
    sku_id: int
    quantity: int
    price: float
    created_at: Timestamp
    updated_at: Timestamp
    sku: SKUData


class Items(BaseModel):
    data: list[Item]


class Metadata(BaseModel):
    key: str
    value: str


class Metadatas(BaseModel):
    data: list[Metadata]


class Email(BaseModel):
    id: int
    cart_id: int
    promocode_id: int
    turn: int
    email: EmailStr
    subject: str
    fire_date: datetime
    sent_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class Emails(BaseModel):
    data: list[Email]


class Search(BaseModel):
    has_shipment_service: bool
    has_address: bool
    has_customer: bool
    has_refused_payment: bool
    abandoned_step: str
    count_recover_mail_sent: int
    created_at: str
    updated_at: str


class SearchData(BaseModel):
    data: Search


class Spreadsheet(BaseModel):
    customer_phone: str
    last_order_date: Optional[str]
    products: str
    products_skus: str
    categories: str
    brands: str
    purchase_url: HttpUrl
    abandoned_step: str
    count_recover_mail_sent: str


class SpreadsheetData(BaseModel):
    data: Spreadsheet


class TotalizersData(BaseModel):
    total_items: int
    subtotal: float
    discount: float
    shipment: float
    shipment_original_value: float
    shipment_discount_value: float
    shipment_discount_percent: float
    progressive_discount_value: float
    combos_discount_value: float
    total: float
    shipment_formated: str
    subtotal_formated: str
    discount_formated: str
    total_formated: str


class TrackingData(BaseModel):
    name: str
    email: EmailStr


class ResourceData(BaseModel):
    id: int
    merchant_id: int
    customer_id: int
    token: str
    has_recommendation: bool
    is_upsell: bool
    totalizers: TotalizersData
    shipping_service: Optional[str]
    tracking_data: TrackingData
    total_transactions: int
    simulate_url: HttpUrl
    unauth_simulate_url: HttpUrl
    last_transaction_status: Optional[str] = None
    created_at: Timestamp
    updated_at: Timestamp
    customer: CustomerData
    items: Items
    transactions: dict
    spreadsheet: SpreadsheetData
    metadata: Metadatas
    search: SearchData
    emails: Emails


class MerchantData(BaseModel):
    id: int
    alias: str


class YampiEvent(BaseModel):
    event: str
    time: datetime
    merchant: MerchantData
    resource: ResourceData
