"""Loaded STT/TTS models, keyed by id. Threadsafe via a single lock."""

import threading
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ModelEntry:
    id: str
    type: str
    instance: Any
    source: str
    metadata: dict[str, str] = field(default_factory=dict)


_lock = threading.Lock()
_models: dict[str, ModelEntry] = {}
_default_id: str | None = None


def register(entry: ModelEntry, as_default: bool = False) -> None:
    global _default_id
    with _lock:
        _models[entry.id] = entry
        if as_default or _default_id is None:
            _default_id = entry.id


def unregister(model_id: str) -> None:
    global _default_id
    with _lock:
        _models.pop(model_id, None)
        if _default_id == model_id:
            _default_id = next(iter(_models), None)


def get(model_id: str | None = None) -> ModelEntry:
    with _lock:
        key = model_id or _default_id
        if key is None or key not in _models:
            raise KeyError(f"No such model: {model_id!r} (default={_default_id!r})")
        return _models[key]


def list_all() -> list[ModelEntry]:
    with _lock:
        return list(_models.values())


def default_id() -> str | None:
    return _default_id


def _clear_all() -> None:
    """Reset registry state. For use in tests only."""
    global _default_id
    with _lock:
        _models.clear()
        _default_id = None
