#!/bin/sh -ue

SELF_DIR=$(dirname "$(realpath "$0")")
ELF=${SELF_DIR}/../../server/target/release/bkupserver
CONFIG=${SELF_DIR}/config.toml

set -x
${ELF} --config-file "${CONFIG}"
set +x
