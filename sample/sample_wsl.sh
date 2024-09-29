#!/bin/sh -u

# Automatic backup script
# Windows command for TaskScheduler:
# > wsl.exe --cd ~ --exec <./path/to/this.sh>

# !!! REPLACE HERE !!!
SRC_DIR=~
DST_DIR=/mnt/d/wsl
# !!! REPLACE HERE !!!

ARCHIVE_DIR=${DST_DIR}
LOG_DIR=${DST_DIR}
LOG_FILE=${LOG_DIR}/backup.log
SELF_DIR=$(realpath $(dirname $0))
SCRIPT_DIR=${SELF_DIR}/../client

echo -------------------------------------------------------------------------------- >> ${LOG_FILE}
echo START >> ${LOG_FILE}
date -R >> ${LOG_FILE}
echo -------------------------------------------------------------------------------- >> ${LOG_FILE}

python3 ${SCRIPT_DIR}/bkup.py \
archive \
--src ${SRC_DIR} \
--dst ${ARCHIVE_DIR} \
>> ${LOG_FILE} 2>&1

echo -------------------------------------------------------------------------------- >> ${LOG_FILE}
echo END >> ${LOG_FILE}
date -R >> ${LOG_FILE}
echo -------------------------------------------------------------------------------- >> ${LOG_FILE}
