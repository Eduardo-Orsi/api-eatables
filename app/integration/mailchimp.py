import os
from enum import Enum

from dotenv import load_dotenv
from fastapi import HTTPException
from mailchimp_marketing import Client as MarketingClient
from mailchimp_marketing.api_client import ApiClientError as MarketingApiClientError

from ..models.abandoned_cart import Customer


load_dotenv()


class AbandonedStep(Enum):
    PERSONAL_INFO = "personal_info"
    SHIPMENT = "shippment"
    PAYMENT = "payment"


class AbandonedStepCartTags(Enum):
    CARRINHO_ABANDONADO = "Carrinho Abandonado"
    ABANDONADO_EM_PAGAMENTO = "Abandonado em Pagamento"
    ABANDONADO_EM_ENTREGA = "Abandonado em Entrega"
    ABANDONADO_EM_DADOS = "Abandonado em Dados"


class MailChimp:

    def __init__(self) -> None:
        self.__api_key = os.getenv("MAILCHIMP_API_KEY")
        self.__list_id = os.getenv("MAILCHIMP_LIST_ID")
        self.__server = os.getenv("MAILCHIMP_SERVER")

        self.marketing_client = MarketingClient({
            "api_key": self.__api_key,
            "server": self.__server
        })

    def add_abandoned_cart_contact(self, customer: Customer, abandoned_step: str) -> dict[str, str]:
        member = self.__abandoned_cart_contact_to_member(customer, abandoned_step)
        return self.__add_member(member)

    def __add_member(self, member: dict[str, str]) -> dict[str, str]:
        try:
            print(member)
            return self.marketing_client.lists.add_list_member(self.__list_id, member)
        except MarketingApiClientError as error:
            raise HTTPException(status_code=error.status_code, detail=error.text) from error

    def __abandoned_cart_contact_to_member(self, customer: Customer, abandoned_step: str) -> dict[str, str]:
        abandoned_step_tag = self.__resolve_abandoned_step(abandoned_step)
        return {
            "email_address": customer.email,
            "status": "unsubscribed",
            "language": "pt",
            "ip_signup": str(customer.ip),
            "timestamp_signup": customer.created_at.date.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "timestamp_opt": customer.created_at.date.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "ip_opt": str(customer.ip),
            "tags": [AbandonedStepCartTags.CARRINHO_ABANDONADO.value, abandoned_step_tag],
            "merge_fields": {
                "FNAME": customer.first_name,
                "LNAME": customer.last_name,
                "PHONE": f"+55{customer.phone.full_number}",
                "ADDRESS": ""
            }
        }

    def __resolve_abandoned_step(self, abandoned_step: AbandonedStep) -> AbandonedStepCartTags:
        if abandoned_step == AbandonedStep.PERSONAL_INFO.value:
            return AbandonedStepCartTags.ABANDONADO_EM_DADOS.value
        elif abandoned_step == AbandonedStep.SHIPMENT.value:
            return AbandonedStepCartTags.ABANDONADO_EM_ENTREGA.value
        elif abandoned_step == AbandonedStep.PAYMENT.value:
            return AbandonedStepCartTags.ABANDONADO_EM_PAGAMENTO.value
        else:
            return

    def get_tags(self) -> dict[str, str]:
        try:
            return self.marketing_client.lists.tag_search(self.__list_id)
        except MarketingApiClientError as error:
            raise HTTPException(status_code=error.status_code, detail=error.text) from error

    def get_merge_fields(self) -> dict[str, str]:
        try:
            return self.marketing_client.lists.get_list_merge_fields(self.__list_id)
        except MarketingApiClientError as error:
            raise HTTPException(status_code=error.status_code, detail=error.text) from error

    def get_lists(self) -> dict[str, str]:
        try:
            return self.marketing_client.lists.get_all_lists()
        except MarketingApiClientError as error:
            raise HTTPException(status_code=error.status_code, detail=error.text) from error

    def ping(self) -> dict[str, str]:
        try:
            return self.marketing_client.ping.get()
        except MarketingApiClientError as error:
            raise HTTPException(status_code=error.status_code, detail=error.text) from error

    def dev(self) -> dict[str, str]:
        return self.get_tags()
