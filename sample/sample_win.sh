#!/bin/sh -u

# Automatic backup script
# Windows command for TaskScheduler:
# > wsl.exe --cd ~ --exec <./path/to/this.sh>

# !!! REPLACE HERE !!!
SRC_DIRS=C:\\Users
DST_DIR=D:\\backup\\win
# !!! REPLACE HERE !!!

# Windows
BACKUP_DIR=${DST_DIR}\\backup
ARCHIVE_DIR=${DST_DIR}\\archive
# WSL
LOG_DIR=$(wslpath ${DST_DIR})
LOG_FILE=${LOG_DIR}/backup.log
SELF_DIR=$(realpath $(dirname $0))
SCRIPT_DIR=${SELF_DIR}/../client

mkdir -p ${LOG_DIR}
echo -------------------------------------------------------------------------------- | tee -a ${LOG_FILE}
echo START  | tee -a ${LOG_FILE}
date -R     | tee -a ${LOG_FILE}
echo -------------------------------------------------------------------------------- | tee -a ${LOG_FILE}

# Robocopy may be failed due to access restriction or locked files
python3 ${SCRIPT_DIR}/runaswin.py ${SCRIPT_DIR}/bkup.py \
sync \
--src ${SRC_DIRS} \
--dst ${BACKUP_DIR} \
--force \
2>&1 \
| tee -a ${LOG_FILE}

python3 ${SCRIPT_DIR}/runaswin.py ${SCRIPT_DIR}/bkup.py \
archive \
--src ${BACKUP_DIR} \
--dst ${ARCHIVE_DIR} \
2>&1 \
| tee -a ${LOG_FILE}

echo -------------------------------------------------------------------------------- | tee -a ${LOG_FILE}
echo END | tee -a ${LOG_FILE}
date -R  | tee -a ${LOG_FILE}
echo -------------------------------------------------------------------------------- | tee -a ${LOG_FILE}
