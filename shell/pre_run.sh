#!/usr/bin/env bash

ENV_FILE=${ENV_FILE:-".env"}
WORKING_DIR=${WORKING_DIR:-"src"}
VIRTUAL_ENV_DIR=${VIRTUAL_ENV_DIR:-".venv"}

cd .. || exit 1

source "${VIRTUAL_ENV_DIR}/bin/activate"

if [ -f "${ENV_FILE}" ]; then
  printf "\nExporting environment\n"

  set -a
  source "${ENV_FILE}"
  set +a
fi

export PYTHONUNBUFFERED=1
export PYTHONIOENCODING=utf8

cd "$WORKING_DIR" || (printf "\nCould not change to working dir: %s\n" "$WORKING_DIR" && exit 1)

printf "\nWorking from: %s\n" "$(pwd)"
