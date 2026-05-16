"""Functional tests for voice management endpoints."""

import pytest
from fastapi.testclient import TestClient

from speech_io_hub.registry import Entry, register


@pytest.mark.functional
def test_list_voices_empty(test_client: TestClient, reset_registry: None) -> None:
    response = test_client.get("/voices")
    assert response.status_code == 200
    assert response.json() == {"loaded": []}


@pytest.mark.functional
def test_list_voices_shows_piper_and_system(test_client: TestClient, reset_registry: None) -> None:
    register(Entry(id="p", type="piper", instance=object(), source="/voice.onnx"))
    register(Entry(id="s", type="system", instance=object(), source="Mónica"))
    loaded = test_client.get("/voices").json()["loaded"]
    assert {e["id"] for e in loaded} == {"p", "s"}


@pytest.mark.functional
def test_list_voices_excludes_whisper(test_client: TestClient, reset_registry: None) -> None:
    register(Entry(id="base", type="whisper", instance=object(), source="base"))
    loaded = test_client.get("/voices").json()["loaded"]
    assert loaded == []


@pytest.mark.functional
def test_load_piper_voice_returns_201(
    test_client: TestClient, reset_registry: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "speech_io_hub.server.routes.voices.load_piper_voice",
        lambda *args, **kwargs: object(),
    )
    response = test_client.post(
        "/voices/load",
        json={"id": "davefx", "type": "piper", "source": "/voice.onnx"},
    )
    assert response.status_code == 201
    assert response.json() == {"id": "davefx", "status": "loaded"}


@pytest.mark.functional
def test_load_system_voice_returns_201(test_client: TestClient, reset_registry: None) -> None:
    response = test_client.post(
        "/voices/load",
        json={"id": "monica", "type": "system", "source": "Mónica"},
    )
    assert response.status_code == 201


@pytest.mark.functional
def test_load_unsupported_type_returns_400(test_client: TestClient, reset_registry: None) -> None:
    response = test_client.post(
        "/voices/load",
        json={"id": "x", "type": "coqui", "source": "/model"},
    )
    assert response.status_code == 400


@pytest.mark.functional
def test_unload_voice_returns_204(test_client: TestClient, reset_registry: None) -> None:
    register(Entry(id="monica", type="system", instance=object(), source="Mónica"))
    response = test_client.delete("/voices/monica")
    assert response.status_code == 204
    assert test_client.get("/voices").json()["loaded"] == []
