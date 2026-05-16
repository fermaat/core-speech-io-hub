"""Endpoints for loading, listing, and unloading TTS voices."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from speech_io_hub.providers.piper import load_piper_voice
from speech_io_hub.providers.system import SystemTTSProvider
from speech_io_hub.registry import Entry, list_by_type, register, unregister

_VOICE_TYPES = ("piper", "system")


class LoadVoiceRequest(BaseModel):
    id: str
    type: str  # "piper" | "system"
    source: str  # path to .onnx (piper) or macOS voice name (system)
    as_default: bool = False


router = APIRouter(prefix="/voices", tags=["voices"])


@router.get("")
def list_voices() -> dict:  # type: ignore[type-arg]
    return {
        "loaded": [
            {"id": v.id, "type": v.type, "source": v.source, "metadata": v.metadata}
            for type_ in _VOICE_TYPES
            for v in list_by_type(type_)
        ],
    }


@router.post("/load", status_code=status.HTTP_201_CREATED)
def load_voice(body: LoadVoiceRequest) -> dict:  # type: ignore[type-arg]
    if body.type == "piper":
        try:
            instance = load_piper_voice(body.source)
        except Exception as exc:
            raise HTTPException(500, f"Failed to load Piper voice: {exc}") from exc
        register(
            Entry(id=body.id, type="piper", instance=instance, source=body.source),
            as_default=body.as_default,
        )
    elif body.type == "system":
        register(
            Entry(
                id=body.id,
                type="system",
                instance=SystemTTSProvider(),
                source=body.source,
            ),
            as_default=body.as_default,
        )
    else:
        raise HTTPException(400, f"Unsupported voice type: {body.type}")
    return {"id": body.id, "status": "loaded"}


@router.delete("/{voice_id}", status_code=status.HTTP_204_NO_CONTENT)
def unload_voice(voice_id: str) -> None:
    unregister(voice_id)
