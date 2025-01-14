#!/usr/bin/env bash

set -euo pipefail

VIRTUAL_ENV_DIR=${VIRTUAL_ENV_DIR:-".venv"}

if [ ! -d "$VIRTUAL_ENV_DIR" ]; then
  printf "\nCreating virtual environment: %s\n" "$VIRTUAL_ENV_DIR"
  python3 -m venv "$VIRTUAL_ENV_DIR"
fi

printf "\nActivating virtual environment: %s\n" "$VIRTUAL_ENV_DIR"

source "${VIRTUAL_ENV_DIR}/bin/activate"
