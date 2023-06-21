#!/bin/bash -eu

source _base.sh

readonly NAME="$1"
shift
readonly SIZE_GIGABYTES="$1"
shift

do_POST '/volumes' \
    name="${NAME}" \
    region="${DO_REGION}" \
    size_gigabytes:="${SIZE_GIGABYTES}" \
    "$@"
