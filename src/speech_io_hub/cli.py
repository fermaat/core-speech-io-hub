"""speech-io-hub CLI — quick smoke tests.

Usage:
    python -m speech_io_hub.cli record-and-transcribe [--prompt "..."]
    python -m speech_io_hub.cli synthesize "texto a hablar" [--voice id] [--no-play]
"""

import argparse
import sys
from pathlib import Path

import httpx

from speech_io_hub.audio.vad import record_until_silence
from speech_io_hub.client.client import SpeechClient


def _print_http_error(exc: BaseException) -> None:
    if isinstance(exc, httpx.HTTPStatusError):
        try:
            detail = exc.response.json().get("detail", exc.response.text)
        except Exception:
            detail = exc.response.text
        print(f"Error del servidor ({exc.response.status_code}): {detail}", file=sys.stderr)
    else:
        print(f"Error: {exc}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(prog="speech-io-hub")
    sub = parser.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("record-and-transcribe")
    r.add_argument("--prompt", default=None, help="initial_prompt to bias Whisper")
    r.add_argument("--language", default="es")
    r.add_argument("--server", default="http://127.0.0.1:8500")

    s = sub.add_parser("synthesize")
    s.add_argument("text", help="Texto a sintetizar")
    s.add_argument("--voice", default=None)
    s.add_argument("--server", default="http://127.0.0.1:8500")
    s.add_argument("--no-play", action="store_true", help="Guarda en out.wav en vez de reproducir")

    args = parser.parse_args()

    if args.cmd == "record-and-transcribe":
        print("Habla. Pararé cuando dejes de hablar...")
        try:
            wav = record_until_silence()
        except RuntimeError as exc:
            print(f"Error grabando: {exc}", file=sys.stderr)
            return 1
        print("Grabación terminada. Transcribiendo...")
        client = SpeechClient(base_url=args.server)
        try:
            result = client.transcribe(wav, language=args.language, initial_prompt=args.prompt)
        except Exception as exc:
            _print_http_error(exc)
            return 1
        print(f"\nTranscripción: {result['text']}")
        print(f"Idioma: {result.get('language')}  Confianza: {result.get('confidence')}")
        return 0

    if args.cmd == "synthesize":
        client = SpeechClient(base_url=args.server)
        try:
            if args.no_play:
                wav = client.synthesize(args.text, voice=args.voice)
                Path("out.wav").write_bytes(wav)
                print("Guardado en out.wav")
            else:
                client.say(args.text, voice=args.voice)
        except Exception as exc:
            _print_http_error(exc)
            return 1
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
