from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/api/v1")
    assert response.status_code == 404  # No root endpoint defined


def test_read_docs():
    response = client.get("/docs")
    assert response.status_code == 200  # Swagger docs should be available 