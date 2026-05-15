"""Unit tests for the model registry."""

import pytest

from speech_io_hub.registry import ModelEntry, default_id, get, list_all, register, unregister


@pytest.mark.unit
def test_register_and_get(reset_registry: None) -> None:
    register(ModelEntry(id="a", type="whisper", instance=object(), source="base"))
    assert get("a").id == "a"
    assert default_id() == "a"


@pytest.mark.unit
def test_get_default_when_no_id_given(reset_registry: None) -> None:
    register(ModelEntry(id="a", type="whisper", instance=object(), source="base"))
    assert get().id == "a"


@pytest.mark.unit
def test_unregister_promotes_next_as_default(reset_registry: None) -> None:
    register(ModelEntry(id="a", type="whisper", instance=object(), source="base"))
    register(ModelEntry(id="b", type="whisper", instance=object(), source="small"))
    assert default_id() == "a"
    unregister("a")
    assert default_id() == "b"


@pytest.mark.unit
def test_list_all(reset_registry: None) -> None:
    register(ModelEntry(id="x", type="whisper", instance=object(), source="base"))
    register(ModelEntry(id="y", type="whisper", instance=object(), source="small"))
    ids = {e.id for e in list_all()}
    assert ids == {"x", "y"}


@pytest.mark.unit
def test_get_missing_raises(reset_registry: None) -> None:
    with pytest.raises(KeyError):
        get("nonexistent")


@pytest.mark.unit
def test_unregister_missing_is_noop(reset_registry: None) -> None:
    unregister("ghost")
    assert default_id() is None


@pytest.mark.unit
def test_as_default_flag(reset_registry: None) -> None:
    register(ModelEntry(id="a", type="whisper", instance=object(), source="base"))
    register(ModelEntry(id="b", type="whisper", instance=object(), source="small"), as_default=True)
    assert default_id() == "b"
