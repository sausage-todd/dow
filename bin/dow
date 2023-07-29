#!/bin/bash -eu

pushd "$(realpath "$(dirname "$0")/..")" >/dev/null
trap 'popd >/dev/null' EXIT

poetry run python src/dow/main.py "$@"
