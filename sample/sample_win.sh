#!/bin/sh -eu

# Automatic backup script
# Windows command for TaskScheduler:
# > wsl.exe --cd ~ --exec <./path/to/this.sh>

# !!! REPLACE HERE !!!
SRC_DIRS=C:\\Users
DST_DIR=D:\\win
# !!! REPLACE HERE !!!

# Windows
BACKUP_DIR=${DST_DIR}\\backup
ARCHIVE_DIR=${DST_DIR}\\archive
# WSL
LOG_DIR=$(wslpath ${DST_DIR})
LOG_FILE=${LOG_DIR}/backup.log
SELF_DIR=$(realpath $(dirname $0))
SCRIPT_DIR=${SELF_DIR}/../client

echo -------------------------------------------------------------------------------- >> ${LOG_FILE}
echo START >> ${LOG_FILE}
date -R >> ${LOG_FILE}
echo -------------------------------------------------------------------------------- >> ${LOG_FILE}

python3 ${SCRIPT_DIR}/runaswin.py ${SCRIPT_DIR}/bkup.py \
sync \
--src ${SRC_DIRS} \
--dst ${BACKUP_DIR} \
--force \
>> ${LOG_FILE} 2>&1

echo -------------------------------------------------------------------------------- >> ${LOG_FILE}
echo END >> ${LOG_FILE}
date -R >> ${LOG_FILE}
echo -------------------------------------------------------------------------------- >> ${LOG_FILE}
