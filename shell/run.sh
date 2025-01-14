#!/usr/bin/env bash

source ./pre_run.sh

printf "\nStarting app\n\n"

python3 docchatai/main.py "${CHAT_MODEL}" "${INPUT_FILE}"