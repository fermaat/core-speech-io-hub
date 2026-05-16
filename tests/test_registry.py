"""Unit tests for the model registry."""

import pytest

from speech_io_hub.registry import Entry, default_id, get, list_all, register, unregister


@pytest.mark.unit
def test_register_and_get(reset_registry: None) -> None:
    register(Entry(id="a", type="whisper", instance=object(), source="base"))
    assert get("a").id == "a"
    assert default_id("whisper") == "a"


@pytest.mark.unit
def test_get_default_when_no_id_given(reset_registry: None) -> None:
    register(Entry(id="a", type="whisper", instance=object(), source="base"))
    assert get(type="whisper").id == "a"


@pytest.mark.unit
def test_unregister_promotes_next_as_default(reset_registry: None) -> None:
    register(Entry(id="a", type="whisper", instance=object(), source="base"))
    register(Entry(id="b", type="whisper", instance=object(), source="small"))
    assert default_id("whisper") == "a"
    unregister("a")
    assert default_id("whisper") == "b"


@pytest.mark.unit
def test_list_all(reset_registry: None) -> None:
    register(Entry(id="x", type="whisper", instance=object(), source="base"))
    register(Entry(id="y", type="whisper", instance=object(), source="small"))
    ids = {e.id for e in list_all()}
    assert ids == {"x", "y"}


@pytest.mark.unit
def test_get_missing_raises(reset_registry: None) -> None:
    with pytest.raises(KeyError):
        get("nonexistent")


@pytest.mark.unit
def test_get_no_default_raises(reset_registry: None) -> None:
    with pytest.raises(KeyError):
        get(type="whisper")


@pytest.mark.unit
def test_get_no_args_raises(reset_registry: None) -> None:
    with pytest.raises(ValueError):
        get()


@pytest.mark.unit
def test_unregister_missing_is_noop(reset_registry: None) -> None:
    unregister("ghost")
    assert default_id("whisper") is None


@pytest.mark.unit
def test_as_default_flag(reset_registry: None) -> None:
    register(Entry(id="a", type="whisper", instance=object(), source="base"))
    register(Entry(id="b", type="whisper", instance=object(), source="small"), as_default=True)
    assert default_id("whisper") == "b"


@pytest.mark.unit
def test_per_type_defaults_are_independent(reset_registry: None) -> None:
    register(Entry(id="w", type="whisper", instance=object(), source="base"))
    register(Entry(id="p", type="piper", instance=object(), source="/voice.onnx"))
    assert default_id("whisper") == "w"
    assert default_id("piper") == "p"
    unregister("w")
    assert default_id("whisper") is None
    assert default_id("piper") == "p"
