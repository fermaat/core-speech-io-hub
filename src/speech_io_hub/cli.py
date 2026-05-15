"""speech-io-hub CLI — quick smoke tests.

Usage:
    python -m speech_io_hub.cli record-and-transcribe [--prompt "..."]
"""

import argparse
import sys

from speech_io_hub.audio.vad import record_until_silence
from speech_io_hub.client.client import SpeechClient


def main() -> int:
    parser = argparse.ArgumentParser(prog="speech-io-hub")
    sub = parser.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record-and-transcribe")
    r.add_argument("--prompt", default=None, help="initial_prompt to bias Whisper")
    r.add_argument("--language", default="es")
    r.add_argument("--server", default="http://127.0.0.1:8500")

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
        result = client.transcribe(
            wav,
            language=args.language,
            initial_prompt=args.prompt,
        )
        print(f"\nTranscripción: {result['text']}")
        print(f"Idioma: {result.get('language')}  Confianza: {result.get('confidence')}")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
