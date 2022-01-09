#!/bin/bash -eu

source _base.sh

do_POST '/droplets' "$@"
