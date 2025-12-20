from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_me_unauthorized():
    response = client.get("/auth/me")
    assert response.status_code == 401
