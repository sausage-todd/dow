#!/bin/bash -eu

function log() {
  local msg="$1"

  echo -e "\033[1;33m [+]\033[0m ${msg}" >&2
}

readonly BASE_URL="https://api.digitalocean.com/v2"

function req() {
  local method=$1
  shift
  local url_path=$1
  shift

  http "${method}" \
    "${BASE_URL}${url_path}" \
    "Authorization:Bearer ${DO_TOKEN}" \
    "$@"
}

function do_POST() {
  local path=$1
  shift
  req POST "${path}" "$@"
}

function do_GET() {
  local url_path=$1
  req GET "${url_path}"
}
