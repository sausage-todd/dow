#!/bin/bash -eu

source _base.sh

readonly DROPLET_ID=$1

do_GET "/droplets/${DROPLET_ID}"

