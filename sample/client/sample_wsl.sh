#!/bin/sh -u

# Automatic backup script
# Windows command for TaskScheduler:
# > wsl.exe --cd ~ --exec <./path/to/this.sh>

# !!! REPLACE HERE !!!
SRC_DIR=~
DST_DIR=/mnt/d/backup/wsl
KEEP_COUNT=12
KEEP_DAYS=365
# Use ~/.ssh/config
REMOTE=shanghai:/mnt/bkupinbox
# Disable upload by empty string
# REMOTE=
# !!! REPLACE HERE !!!

ARCHIVE_DIR=${DST_DIR}
LOG_DIR=${DST_DIR}
LOG_FILE=${LOG_DIR}/backup.log
SELF_DIR=$(dirname "$(realpath "$0")")
SCRIPT_DIR=${SELF_DIR}/../client


mkdir -p ${LOG_DIR}
echo -------------------------------------------------------------------------------- | tee -a ${LOG_FILE}
echo START | tee -a ${LOG_FILE}
date -R    | tee -a ${LOG_FILE}
echo -------------------------------------------------------------------------------- | tee -a ${LOG_FILE}

python3 "${SCRIPT_DIR}/bkup.py" \
archive \
--src ${SRC_DIR} \
--dst ${ARCHIVE_DIR} \
2>&1 \
| tee -a ${LOG_FILE}

python3 "${SCRIPT_DIR}/bkup.py" \
clean \
--dst ${ARCHIVE_DIR} \
--keep-count ${KEEP_COUNT} \
--keep-days ${KEEP_DAYS} \
2>&1 \
| tee -a ${LOG_FILE}

if [ -n "${REMOTE}" ]; then
    python3 "${SCRIPT_DIR}/bkup.py" \
    upload \
    --src ${ARCHIVE_DIR} \
    --dst ${REMOTE} \
    2>&1 \
    | tee -a ${LOG_FILE}
fi

echo -------------------------------------------------------------------------------- | tee -a ${LOG_FILE}
echo END | tee -a ${LOG_FILE}
date -R  | tee -a ${LOG_FILE}
echo -------------------------------------------------------------------------------- | tee -a ${LOG_FILE}
echo "" | tee -a ${LOG_FILE}
