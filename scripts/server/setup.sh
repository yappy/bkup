#!/bin/sh -ue

SELF_DIR=$(dirname "$(realpath "$0")")
ELF=${SELF_DIR}/../../server/target/release/bkupserver
CONFIG=${SELF_DIR}/config.toml


if [ -e "${CONFIG}" ]; then
    set -x
    mv -i "${CONFIG}" "${CONFIG}~"
    set +x
fi
set -x
${ELF} --gen-config "${CONFIG}"
set +x

echo Open and edit: "${CONFIG}"
