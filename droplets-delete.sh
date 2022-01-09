#!/bin/bash -eu

source _base.sh

readonly DROPLET_ID="${1}"

req DELETE "/droplets/${DROPLET_ID}"
