#!/bin/bash -eu

source _base.sh

set -o pipefail

readonly DROPLET_NAME=$1

function err() {
    echo -e "\e[1;31m [-]\e[0m $*" >&2
}

function log() {
    echo -e "\e[1;33m [+]\e[0m $*"
}

function droplet_id() {
    local droplet_name=$1
    local result
    result="$(./droplets-list.sh | jq --compact-output ".droplets[] | {name, id}")"

    log "all droplets:" >&2
    echo "${result}" >&2

    local droplet_id
    droplet_id="$(echo "${result}" | jq --raw-output ". | select(.name == \"${droplet_name}\") | .id")"
    if [[ -z "${droplet_id}" ]]; then
        err "droplet not found" >&2
        exit 1
    fi

    log "using droplet id: ${droplet_id}" >&2

    echo "${droplet_id}"
}

function droplet_network() {
    local droplet_id=$1

    ./droplets-get.sh "${droplet_id}" |
        jq --raw-output '.droplet.networks.v4[] | select(.type == "public") | .ip_address'
}

log "fetching droplet id    "
DROPLET_ID="$(droplet_id "${DROPLET_NAME}")"
readonly DROPLET_ID
DROPLET_IP="$(droplet_network "${DROPLET_ID}")"
readonly DROPLET_IP

ssh -A misha@"${DROPLET_IP}"
