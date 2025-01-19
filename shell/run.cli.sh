#!/usr/bin/env bash

source ./pre_run.sh

printf "\nStarting app\n\n"

python3 docchatai/main_cli.py "${CHAT_MODEL}" "${CHAT_FILE}"