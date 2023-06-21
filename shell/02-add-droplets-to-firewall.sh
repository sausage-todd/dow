#!/bin/bash -eu

source _base.sh

readonly FIREWALL_ID=$1
readonly DROPLET_ID=$2

do_POST \
  "/firewalls/${FIREWALL_ID}/droplets" \
  droplet_ids:="$(jo -a "${DROPLET_ID}")"
