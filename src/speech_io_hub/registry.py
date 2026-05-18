"""Loaded artifacts (STT models, TTS voices) keyed by id.

Defaults are tracked per type so the STT default does not collide with the TTS default.
A second mapping tracks the default per "category" ("stt" / "tts") to support
hot-swap across compatible types — e.g. flipping the active TTS voice from Piper to
the system voice with ``as_default=True``.

Threadsafe via a single lock.
"""

import threading
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Entry:
    id: str
    type: str  # "whisper" | "piper" | "system" | ...
    instance: Any
    source: str
    metadata: dict[str, str] = field(default_factory=dict)


_CATEGORY_FOR_TYPE: dict[str, str] = {
    "whisper": "stt",
    "piper": "tts",
    "system": "tts",
}


_lock = threading.Lock()
_entries: dict[str, Entry] = {}
_defaults: dict[str, str] = {}  # type -> entry_id
_category_defaults: dict[str, str] = {}  # category ("stt"/"tts") -> entry_id


def register(entry: Entry, as_default: bool = False) -> None:
    with _lock:
        _entries[entry.id] = entry
        if as_default or entry.type not in _defaults:
            _defaults[entry.type] = entry.id
        category = _CATEGORY_FOR_TYPE.get(entry.type)
        if category is not None and (as_default or category not in _category_defaults):
            _category_defaults[category] = entry.id


def unregister(entry_id: str) -> None:
    with _lock:
        entry = _entries.pop(entry_id, None)
        if entry is None:
            return
        if _defaults.get(entry.type) == entry_id:
            successor = next(
                (e.id for e in _entries.values() if e.type == entry.type),
                None,
            )
            if successor is not None:
                _defaults[entry.type] = successor
            else:
                _defaults.pop(entry.type, None)
        category = _CATEGORY_FOR_TYPE.get(entry.type)
        if category is not None and _category_defaults.get(category) == entry_id:
            # Promote any remaining entry whose type maps to the same category.
            successor = next(
                (e.id for e in _entries.values() if _CATEGORY_FOR_TYPE.get(e.type) == category),
                None,
            )
            if successor is not None:
                _category_defaults[category] = successor
            else:
                _category_defaults.pop(category, None)


def get(entry_id: str | None = None, type: str | None = None) -> Entry:
    """Look up an entry by id, or by type default if no id given."""
    with _lock:
        if entry_id is not None:
            if entry_id not in _entries:
                raise KeyError(f"No such entry: {entry_id!r}")
            return _entries[entry_id]
        if type is None:
            raise ValueError("Must specify entry_id or type")
        default = _defaults.get(type)
        if default is None or default not in _entries:
            raise KeyError(f"No default entry for type {type!r}")
        return _entries[default]


def list_all() -> list[Entry]:
    with _lock:
        return list(_entries.values())


def list_by_type(type: str) -> list[Entry]:
    with _lock:
        return [e for e in _entries.values() if e.type == type]


def default_id(type: str) -> str | None:
    with _lock:
        return _defaults.get(type)


def default_id_for_category(category: str) -> str | None:
    """Return the default entry id for a category ("stt" / "tts"), if any."""
    with _lock:
        return _category_defaults.get(category)


def _clear_all() -> None:
    """Reset registry state. For use in tests only."""
    with _lock:
        _entries.clear()
        _defaults.clear()
        _category_defaults.clear()
