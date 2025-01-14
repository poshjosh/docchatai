#!/usr/bin/env bash

set -euo pipefail

#######################################################################################
# Make sure you have already run `./shell/install.dev.sh` before running this script. #
#######################################################################################

cd ..

# Make main modules accessible to test modules
python3 -m pip install -e .
