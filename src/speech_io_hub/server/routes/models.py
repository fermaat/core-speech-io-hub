"""Endpoints for loading, listing, and unloading models."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from speech_io_hub.providers.whisper import load_whisper_model
from speech_io_hub.registry import ModelEntry, list_all, register, unregister


class LoadRequest(BaseModel):
    id: str
    source: str
    type: str = "whisper"
    device: str = "auto"
    compute_type: str = "auto"
    as_default: bool = False


router = APIRouter(prefix="/models", tags=["models"])


@router.get("")
def list_models() -> dict:  # type: ignore[type-arg]
    return {
        "loaded": [
            {"id": e.id, "type": e.type, "source": e.source, "metadata": e.metadata}
            for e in list_all()
        ],
    }


@router.post("/load", status_code=status.HTTP_201_CREATED)
def load_model(body: LoadRequest) -> dict:  # type: ignore[type-arg]
    if body.type != "whisper":
        raise HTTPException(400, f"Unsupported model type: {body.type}")
    try:
        instance = load_whisper_model(
            body.id,
            body.source,
            device=body.device,
            compute_type=body.compute_type,
        )
    except Exception as exc:
        raise HTTPException(500, f"Failed to load model: {exc}") from exc
    register(
        ModelEntry(id=body.id, type=body.type, instance=instance, source=body.source),
        as_default=body.as_default,
    )
    return {"id": body.id, "status": "loaded"}


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
def unload_model(model_id: str) -> None:
    unregister(model_id)
