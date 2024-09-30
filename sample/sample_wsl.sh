#!/bin/sh -u

# Automatic backup script
# Windows command for TaskScheduler:
# > wsl.exe --cd ~ --exec <./path/to/this.sh>

# !!! REPLACE HERE !!!
SRC_DIR=~
DST_DIR=/mnt/d/backup/wsl
# !!! REPLACE HERE !!!

ARCHIVE_DIR=${DST_DIR}
LOG_DIR=${DST_DIR}
LOG_FILE=${LOG_DIR}/backup.log
SELF_DIR=$(realpath $(dirname $0))
SCRIPT_DIR=${SELF_DIR}/../client

mkdir -p ${LOG_DIR}
echo -------------------------------------------------------------------------------- | tee -a ${LOG_FILE}
echo START | tee -a ${LOG_FILE}
date -R    | tee -a ${LOG_FILE}
echo -------------------------------------------------------------------------------- | tee -a ${LOG_FILE}

python3 ${SCRIPT_DIR}/bkup.py \
archive \
--src ${SRC_DIR} \
--dst ${ARCHIVE_DIR} \
2>&1 \
| tee -a ${LOG_FILE}

echo -------------------------------------------------------------------------------- | tee -a ${LOG_FILE}
echo END | tee -a ${LOG_FILE}
date -R  | tee -a ${LOG_FILE}
echo -------------------------------------------------------------------------------- | tee -a ${LOG_FILE}
