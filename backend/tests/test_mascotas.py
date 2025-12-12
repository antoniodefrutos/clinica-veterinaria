from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def login_admin():
    r = client.post("/auth/token", data={
        "username": "admin@example.com",
        "password": "adminpass"
    })
    return r.json()["access_token"]


def test_list_mascotas():
    token = login_admin()
    r = client.get("/mascotas/", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)