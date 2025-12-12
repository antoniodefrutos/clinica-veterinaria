import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def credentials():
    # ajusta si tu seed tiene otros valores
    return {"username": "admin@example.com", "password": "adminpass"}

def test_obtener_token_form(credentials):
    response = client.post(
        "/auth/token",
        data={"username": credentials["username"], "password": credentials["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"