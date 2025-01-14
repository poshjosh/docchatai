#!/usr/bin/env bash

export ENV_FILE="test.env"

source ./pre_run.sh

printf "\nStarting tests\n\n"

python3 -m unittest discover -s test -p "*_test.py"
