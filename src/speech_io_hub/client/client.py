"""HTTP client used by downstream apps (fante) to talk to the hub."""

import httpx


class SpeechClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8500", timeout: int = 60) -> None:
        self._base = base_url.rstrip("/")
        self._timeout = timeout

    def health(self) -> bool:
        response = httpx.get(f"{self._base}/health", timeout=self._timeout)
        response.raise_for_status()
        data: dict[str, str] = response.json()
        return data.get("status") == "ok"

    def transcribe(
        self,
        audio: bytes,
        language: str | None = None,
        initial_prompt: str | None = None,
        model: str | None = None,
    ) -> dict[str, object]:
        files = {"audio": ("recording.wav", audio, "audio/wav")}
        data: dict[str, str] = {}
        if language is not None:
            data["language"] = language
        if initial_prompt is not None:
            data["initial_prompt"] = initial_prompt
        if model is not None:
            data["model"] = model
        response = httpx.post(
            f"{self._base}/transcribe",
            files=files,
            data=data,
            timeout=self._timeout,
        )
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    def list_models(self) -> dict[str, object]:
        response = httpx.get(f"{self._base}/models", timeout=self._timeout)
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    def load_model(
        self,
        id: str,
        source: str,
        type: str = "whisper",
        device: str = "auto",
        compute_type: str = "auto",
        as_default: bool = False,
    ) -> dict[str, object]:
        body = {
            "id": id,
            "source": source,
            "type": type,
            "device": device,
            "compute_type": compute_type,
            "as_default": as_default,
        }
        response = httpx.post(f"{self._base}/models/load", json=body, timeout=self._timeout)
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    def unload_model(self, model_id: str) -> None:
        response = httpx.delete(f"{self._base}/models/{model_id}", timeout=self._timeout)
        response.raise_for_status()

    def synthesize(self, text: str, voice: str | None = None) -> bytes:
        body: dict[str, object] = {"text": text}
        if voice is not None:
            body["voice"] = voice
        response = httpx.post(f"{self._base}/synthesize", json=body, timeout=self._timeout)
        response.raise_for_status()
        return response.content

    def say(self, text: str, voice: str | None = None) -> None:
        """Synthesize and play locally. Convenience for terminal apps."""
        from speech_io_hub.client.playback import play_wav

        play_wav(self.synthesize(text, voice=voice))

    def list_voices(self) -> dict[str, object]:
        response = httpx.get(f"{self._base}/voices", timeout=self._timeout)
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    def load_voice(
        self,
        id: str,
        source: str,
        type: str = "piper",
        as_default: bool = False,
    ) -> dict[str, object]:
        body = {"id": id, "source": source, "type": type, "as_default": as_default}
        response = httpx.post(f"{self._base}/voices/load", json=body, timeout=self._timeout)
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    def unload_voice(self, voice_id: str) -> None:
        response = httpx.delete(f"{self._base}/voices/{voice_id}", timeout=self._timeout)
        response.raise_for_status()
