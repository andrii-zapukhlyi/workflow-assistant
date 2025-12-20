import os
import sys

from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

client = TestClient(app)


def test_me_unauthorized():
    response = client.get("/auth/me")
    assert response.status_code == 401
