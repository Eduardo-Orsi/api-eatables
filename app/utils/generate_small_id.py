import uuid
import base64


def generate_small_id() -> str:
    unique_id = base64.urlsafe_b64encode(uuid.uuid4().bytes).decode('utf-8').rstrip("=")
    return unique_id[:8]
