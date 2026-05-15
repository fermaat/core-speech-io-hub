"""Functional tests: /health endpoint via FastAPI TestClient."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.functional
def test_health_returns_200(test_client: TestClient) -> None:
    response = test_client.get("/health")
    assert response.status_code == 200


@pytest.mark.functional
def test_health_returns_ok_payload(test_client: TestClient) -> None:
    response = test_client.get("/health")
    assert response.json() == {"status": "ok"}
