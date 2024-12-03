import base64
import hmac
import hashlib

import requests
from fastapi import HTTPException

class Yampi:

    def __init__(self, alias: str, token: str, secret: str) -> None:
        self.__alias = alias
        self.__token = token
        self.__secret = secret
        self.api_url = f"https://api.dooki.com.br/v2/{self.__alias}"
        self.__auth_header = {
            "User-Token": self.__token,
            "User-Secret-Key": self.__secret
        }

    @staticmethod
    async def validate_webhook_signature(body: bytes, signature: str | None, secret_key: str):
        if not signature:
            raise HTTPException(status_code=401, detail='Missing webhook signature')

        expected_signature = base64.b64encode(hmac.new(
            secret_key.encode(),
            body,
            hashlib.sha256
        ).digest()).decode()

        if not hmac.compare_digest(signature, expected_signature):
            raise HTTPException(status_code=401, detail='Invalid webhook signature')

    def get_order_by_id(self, order_id: str) -> dict:
        response = requests.get(
            url=f"{self.api_url}/orders/{order_id}?include=metadata",
            headers=self.__auth_header,
            timeout=5
        )

        if not response.status_code == 200:
            return {}

        return response.json()

    def get_shopify_order_name(self, yampi_order_id: str) -> str:
        order = self.get_order_by_id(yampi_order_id)

        if not order:
            return ""

        metadata = order["data"]["metadata"]["data"]
        for item in metadata:
            if item.get("key") == "platform_order_number":
                return item.get("value")
        return ""
