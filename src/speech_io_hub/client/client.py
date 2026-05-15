"""HTTP client used by downstream apps (fante) to talk to the hub."""

import httpx


class SpeechClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8500", timeout: int = 30) -> None:
        self._base = base_url.rstrip("/")
        self._timeout = timeout

    def health(self) -> bool:
        response = httpx.get(f"{self._base}/health", timeout=self._timeout)
        response.raise_for_status()
        data: dict[str, str] = response.json()
        return data.get("status") == "ok"
