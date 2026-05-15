"""Functional tests for model management endpoints."""

import pytest
from fastapi.testclient import TestClient

from speech_io_hub.registry import ModelEntry, register


@pytest.mark.functional
def test_list_models_empty(test_client: TestClient, reset_registry: None) -> None:
    response = test_client.get("/models")
    assert response.status_code == 200
    assert response.json() == {"loaded": []}


@pytest.mark.functional
def test_list_models_shows_registered(test_client: TestClient, reset_registry: None) -> None:
    register(ModelEntry(id="base", type="whisper", instance=object(), source="base"))
    response = test_client.get("/models")
    assert response.status_code == 200
    loaded = response.json()["loaded"]
    assert len(loaded) == 1
    assert loaded[0]["id"] == "base"


@pytest.mark.functional
def test_load_model_returns_201(
    test_client: TestClient, reset_registry: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "speech_io_hub.server.routes.models.load_whisper_model",
        lambda *args, **kwargs: object(),
    )
    response = test_client.post(
        "/models/load",
        json={"id": "base", "source": "base"},
    )
    assert response.status_code == 201
    assert response.json() == {"id": "base", "status": "loaded"}


@pytest.mark.functional
def test_load_model_unsupported_type(test_client: TestClient, reset_registry: None) -> None:
    response = test_client.post(
        "/models/load",
        json={"id": "piper", "source": "/some/path", "type": "piper"},
    )
    assert response.status_code == 400


@pytest.mark.functional
def test_unload_model_returns_204(test_client: TestClient, reset_registry: None) -> None:
    register(ModelEntry(id="base", type="whisper", instance=object(), source="base"))
    response = test_client.delete("/models/base")
    assert response.status_code == 204

    remaining = test_client.get("/models").json()["loaded"]
    assert remaining == []
