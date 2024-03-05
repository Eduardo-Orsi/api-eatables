import json
from fastapi.testclient import TestClient
from .mocks.yampi_json_data import yampi_json_data
from ..app.shipping import app


client = TestClient(app)

def test_shipping_receiving() -> None:
    response = client.post("/shipping/", data=json.dumps(yampi_json_data))
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_shipping_response() -> None:
    pass

def test_shipping_request() -> None:
    pass
