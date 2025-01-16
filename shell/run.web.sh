#!/usr/bin/env bash

source ./pre_run.sh

printf "\nStarting app\n\n"

python3 docchatai/main_web.py "${CHAT_MODEL}" "${INPUT_FILE}"