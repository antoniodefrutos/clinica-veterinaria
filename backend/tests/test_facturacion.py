from fastapi.testclient import TestClient
from app.main import app
import datetime

client = TestClient(app)

def login_admin():
    r = client.post("/auth/token", data={
        "username": "admin@example.com",
        "password": "adminpass"
    })
    return r.json()["access_token"]


def test_crear_factura():
    token = login_admin()

    nuevo = {
        "client_id": 1,
        "date": str(datetime.date.today()),
        "total": 50.0
    }

    r = client.post("/facturacion/crear", json=nuevo, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code in (200, 201)