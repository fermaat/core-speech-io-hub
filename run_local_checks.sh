#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")"

echo "Running local validation for $(basename "$PWD")..."

pdm run black --check src tests
pdm run mypy src
pdm run pytest -m "unit or functional"

echo "All local checks passed!"
