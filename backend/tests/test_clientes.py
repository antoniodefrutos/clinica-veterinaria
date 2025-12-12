import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def login_admin():
    r = client.post("/auth/token", data={
        "username": "admin@example.com",
        "password": "adminpass"
    })
    return r.json()["access_token"]


def test_list_clientes():
    token = login_admin()
    r = client.get("/clientes/", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_create_cliente():
    token = login_admin()

    nuevo = {
        "dni": "XYZ123",
        "name": "Cliente Test",
        "email": "test@example.com",
        "phone": "600000000"
    }

    r = client.post("/clientes/", json=nuevo, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert data["dni"] == "XYZ123"