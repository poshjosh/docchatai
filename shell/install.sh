#!/usr/bin/env bash

set -euo pipefail

cd ..

source ./shell/venv.sh

python3 -m pip install --upgrade pip

python3 -m pip install pip-tools

cd "src/docchatai"

printf "\nCompiling dependencies to requirements.txt\n"
pip-compile requirements.in > requirements.txt

printf "\nInstalling dependencies from requirements.txt\n"
python3 -m pip install -r requirements.txt
