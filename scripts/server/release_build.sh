#!/bin/sh -uex

SELF_DIR=$(dirname "$(realpath "$0")")
DIR=${SELF_DIR}/../../server

cd "${DIR}"
cargo build --release
