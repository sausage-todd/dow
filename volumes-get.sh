#!/bin/bash -eu

source _base.sh

readonly VOLUME_ID="${1}"

req GET "/volumes/${VOLUME_ID}"
