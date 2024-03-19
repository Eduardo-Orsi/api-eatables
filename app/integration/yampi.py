import base64
import hmac
import hashlib
from fastapi import HTTPException

class Yampi:

    @staticmethod
    async def validate_webhook_signature(body: bytes, signature: str | None, secret_key: str):
        if not signature:
            raise HTTPException(status_code=401, detail='Missing webhook signature')

        expected_signature = base64.b64encode(hmac.new(
            secret_key.encode(),
            body,
            hashlib.sha256
        ).digest()).decode()

        if not signature == expected_signature:
            raise HTTPException(status_code=401, detail='Invalid webhook signature')
