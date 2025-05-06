#!/usr/bin/env bash

MAGENTA='\033[0;35m'
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo_magenta() {
    echo
    echo -e "--- ${MAGENTA}$1${NC} ---"
}

if [ "$(dirname "$0")" == "." ]; then
    echo "Changing directory to the project directory"
    cd ..
fi

check_return() {
    if [ "$1" -ne 0 ]; then
        echo -e "${RED}Failed${NC}"
        exit 1
    fi
    echo -e "${GREEN}Passed${NC}"
}

echo "Running code checks locally"

# Prerequisites
uv sync

echo_magenta "Pytest"
pytest -q --show-capture=no >/dev/null
check_return $?


echo_magenta "Ruff format"
ruff format .
check_return $?

echo_magenta "Ruff check"
ruff check . --fix
check_return $?

echo_magenta "Mypy"
mypy .
check_return $?
