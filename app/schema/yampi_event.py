from typing import Optional, Any
from datetime import datetime

from pydantic import BaseModel, EmailStr, HttpUrl, IPvAnyAddress


class Timestamp(BaseModel):
    date: datetime
    timezone_type: int
    timezone: str


class Phone(BaseModel):
    number: str
    area_code: str
    full_number: str
    whatsapp_link: HttpUrl
    formated_number: str


class Customer(BaseModel):
    id: int
    ip: Optional[IPvAnyAddress]
    cpf: Optional[str]
    cnpj: Optional[str]
    name: str
    type: str
    email: EmailStr
    notes: Optional[str]
    phone: Phone
    token: str
    active: bool
    birthday: Optional[str]
    whatsapp: bool
    last_name: Optional[str]
    login_url: Optional[HttpUrl]
    social_id: Optional[str]
    anonymized: bool
    cluster_id: Optional[int]
    created_at: Timestamp
    first_name: Optional[str]
    newsletter: bool
    updated_at: Timestamp
    utm_source: Optional[str]
    merchant_id: int
    generic_name: Optional[str]
    razao_social: Optional[str]
    utm_campaign: Optional[str]
    social_driver: Optional[str]
    marketplace_id: Optional[int]
    state_registration: Optional[str]


class CustomerData(BaseModel):
    data: Customer


class Customizations(BaseModel):
    data: list[Any]


class SKU(BaseModel):
    id: int
    sku: str
    order: int
    title: str
    token: str
    width: float
    erp_id: Optional[int]
    height: float
    length: float
    weight: float
    barcode: Optional[str]
    seller_id: Optional[int]
    created_at: Timestamp
    price_cost: float
    price_sale: float
    product_id: int
    updated_at: Timestamp
    variations: list[Any]
    availability: int
    blocked_sale: bool
    combinations: str
    purchase_url: HttpUrl
    total_orders: Optional[int]
    customizations: Customizations
    price_discount: float
    total_in_stock: int
    quantity_managed: bool
    availability_soldout: int
    image_reference_sku_id: Optional[int]
    days_availability_formated: str
    allow_sell_without_customization: bool


class SKUData(BaseModel):
    data: SKU


class Item(BaseModel):
    id: int
    sku: SKUData
    gift: bool
    price: float
    sku_id: int
    item_sku: str
    quantity: int
    bundle_id: Optional[int]
    gift_value: float
    has_recomm: int
    is_digital: bool
    price_cost: float
    product_id: int
    bundle_name: Optional[str]
    shipment_cost: float
    customizations: list[Any]


class Items(BaseModel):
    data: list[Item]


class Metadata(BaseModel):
    key: str
    value: str


class Metadatalist(BaseModel):
    data: list[Metadata]


class Payment(BaseModel):
    name: str
    alias: str
    icon_url: HttpUrl


class PixData(BaseModel):
    pix_qr_code: str
    pix_expiration_date: datetime


class Pix(BaseModel):
    data: list[Any] | PixData


class Services(BaseModel):
    data: list[Any]


class Status(BaseModel):
    id: int
    name: str
    alias: str
    description: str


class StatusData(BaseModel):
    data: Status


class Search(BaseModel):
    created_at: str
    payment_id: int
    updated_at: str
    captured_at: str
    cancelled_at: Optional[str]
    products_ids: list[int]
    date_delivery: str
    inventory_ids: list[int]
    payment_retry: bool
    affiliation_id: int
    payment_method: str
    antifraud_status: Optional[str]
    gateway_transaction_id: str


class SearchData(BaseModel):
    data: Search


class StatusItem(BaseModel):
    id: int
    name: str
    alias: str
    details: Optional[str]
    created_at: Timestamp
    updated_at: Timestamp
    description: str


class Statuses(BaseModel):
    data: list[StatusItem]


class WhatsAppDataFields(BaseModel):
    pix: Optional[Any]
    billet: Optional[Any]
    order_shipped: Optional[Any]
    abandoned_cart: Optional[Any]


class WhatsAppData(BaseModel):
    data: WhatsAppDataFields


class Promocode(BaseModel):
    id: int
    code: str
    used: int
    value: float
    active: bool
    end_at: Timestamp
    expired: bool
    quantity: int
    start_at: Timestamp
    min_value: float
    accumulate: bool
    created_at: Timestamp
    newsletter: bool
    updated_at: Timestamp
    customer_id: Optional[int]
    description: Optional[str]
    items_count: int
    cart_default: bool
    payments_ids: list[int]
    discount_type: str
    free_shipment: bool
    abandoned_cart: bool
    price_products: float | str | None
    for_the_price_of: bool
    product_quantity: int
    once_per_customer: bool
    ignore_promotion_products: bool


class PromocodeData(BaseModel):
    data: Promocode | list[Any] | dict


class SpreadsheetItem(BaseModel):
    sku: str
    status: str
    payment: str
    product: str
    customer: str
    quantity: int
    delivered: int
    total_cost: float
    total_item: float
    credit_card: str | None
    payment_date: str
    customization: str
    shipping_city: str
    billet_barcode: Optional[str]
    cancelled_date: str
    customer_email: EmailStr
    customer_phone: str
    shipping_state: str
    shipping_number: str
    shipping_street: str
    shipping_address: str
    customer_document: str
    shipping_zip_code: str
    shipping_complement: str
    shipping_neighborhood: str
    gateway_transaction_id: str


class SpreadsheetData(BaseModel):
    data: list[SpreadsheetItem]


class PaymentDetails(BaseModel):
    id: int
    name: str
    alias: str
    is_pix: bool
    icon_url: HttpUrl
    is_billet: bool
    is_wallet: bool
    has_config: bool
    is_deposit: bool
    active_config: bool
    is_credit_card: bool
    is_pix_in_installments: bool


class PaymentData(BaseModel):
    data: PaymentDetails


class TransactionMetadata(BaseModel):
    data: list[Any] | PixData


class BilletDate(BaseModel):
    date: datetime
    timezone: str
    timezone_type: int


class Transaction(BaseModel):
    id: int
    amount: float
    status: str
    payment: PaymentData
    captured: bool
    metadata: TransactionMetadata
    bank_name: Optional[str]
    cancelled: bool
    authorized: bool
    bank_alias: Optional[str]
    billet_url: Optional[str]
    created_at: Timestamp
    error_code: Optional[str]
    payment_id: int
    total_logs: int
    updated_at: Timestamp
    billet_date: Optional[BilletDate]
    captured_at: Optional[Timestamp]
    customer_id: int
    holder_name: str | None
    buyer_amount: float
    cancelled_at: Optional[str]
    capture_date: Optional[str]
    installments: int
    authorized_at: Timestamp
    error_message: Optional[str]
    affiliation_id: int
    billet_barcode: Optional[str]
    marketplace_id: Optional[int]
    truncated_card: str | None
    antifraud_score: Optional[str]
    can_be_captured: bool
    holder_document: str | None
    antifraud_status: Optional[str]
    can_be_cancelled: bool
    gateway_order_id: Optional[str]
    antifraud_sale_id: Optional[str]
    billet_our_number: Optional[str]
    gateway_billet_id: Optional[str]
    installment_value: float
    sent_to_antifraud: bool
    billet_whatsapp_link: Optional[HttpUrl]
    installment_formated: str
    billet_document_number: Optional[str]
    gateway_transaction_id: str
    marketplace_account_id: Optional[int]
    buyer_installment_value: float
    buyer_installment_formated: str
    gateway_authorization_code: Optional[str]


class Transactions(BaseModel):
    data: Optional[list[Transaction]]


class ShippingAddress(BaseModel):
    id: int
    uf: str
    city: str
    state: str
    number: str
    street: str
    country: str
    zipcode: str
    order_id: int
    receiver: str
    zip_code: str
    reference: Optional[str]
    complement: Optional[str]
    address_name: Optional[str]
    full_address: str
    neighborhood: str


class ShippingAddressData(BaseModel):
    data: ShippingAddress


class MarketplaceData(BaseModel):
    data: list[Any]


class MarketplaceAccountData(BaseModel):
    data: list[Any]


class WhatsAppAppData(BaseModel):
    data: dict[str, Optional[Any]]


class Resource(BaseModel):
    id: int
    ip: str
    pix: Pix
    items: Items
    device: str
    number: int
    search: SearchData
    status: StatusData
    customer: CustomerData
    metadata: Metadatalist
    payments: list[Payment]
    services: Services
    statuses: Statuses
    utm_term: Optional[str]
    whatsapp: WhatsAppData
    delivered: bool
    is_upsell: bool
    promocode: PromocodeData
    status_id: int
    track_url: Optional[str]
    value_tax: float
    authorized: bool
    cart_token: str
    created_at: Timestamp
    has_recomm: bool
    has_upsell: bool
    public_url: HttpUrl
    track_code: Optional[str]
    updated_at: Timestamp
    utm_medium: Optional[str]
    utm_source: Optional[str]
    customer_id: int
    has_payment: bool
    marketplace: MarketplaceData
    merchant_id: int
    reorder_url: HttpUrl
    spreadsheet: SpreadsheetData
    sync_by_erp: bool
    utm_content: Optional[str]
    value_total: float
    promocode_id: Optional[int]
    transactions: Transactions
    utm_campaign: Optional[str]
    whatsapp_app: WhatsAppAppData
    b2w_label_url: Optional[str]
    date_delivery: Timestamp
    days_delivery: int
    desire_status: list[str]
    shipment_cost: float
    marketplace_id: Optional[int]
    total_comments: int
    value_discount: float
    value_products: float
    value_shipment: float
    buyer_value_tax: float
    desire_status_id: list[int]
    shipment_service: Optional[str]
    shipping_address: ShippingAddressData
    buyer_value_total: float
    shipment_icon_url: Optional[str]
    shipment_quote_id: Optional[str]
    marketplace_account: MarketplaceAccountData
    shipment_service_id: Optional[str]
    billet_whatsapp_link: Optional[HttpUrl]
    content_statement_url: Optional[HttpUrl]
    marketplace_account_id: Optional[int]
    marketplace_partner_id: Optional[int]
    marketplace_sale_number: Optional[int]
    billet_whatsapp_app_link: Optional[str]


class Merchant(BaseModel):
    id: int
    alias: str


class YampiEvent(BaseModel):
    time: datetime
    event: str
    merchant: Merchant
    resource: Resource
