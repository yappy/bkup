# No shebang: include only
# shellcheck shell=bash

# Automatic backup script for Windows
# Create a separate script file and set required parameters,
# then include this file by "." or "source".

# Check required parameters
set -u
# !!! Required Variables !!!
echo "SRC_DIRS:   ${SRC_DIRS}"
echo "DST_DIR:    ${DST_DIR}"
echo "KEEP_COUNT: ${KEEP_COUNT}"
echo "KEEP_DAYS : ${KEEP_DAYS}"
echo "REMOTE:     ${REMOTE}"
# !!! Required Variables !!!

BACKUP_DIR=${DST_DIR}/backup
ARCHIVE_DIR=${DST_DIR}/archive
LOG_DIR=${DST_DIR}
LOG_FILE=${LOG_DIR}/backup.log
SELF_DIR=$(dirname "$(realpath "$0")")
SCRIPT_DIR=${SELF_DIR}/../../client

mkdir -p "${LOG_DIR}"
echo -------------------------------------------------------------------------------- | tee -a "${LOG_FILE}"
echo START  | tee -a "${LOG_FILE}"
date -R     | tee -a "${LOG_FILE}"
echo -------------------------------------------------------------------------------- | tee -a "${LOG_FILE}"

# Robocopy may be failed due to access restriction or locked files
# shellcheck disable=SC2086
python3 "${SCRIPT_DIR}/bkup.py" \
sync \
--src ${SRC_DIRS} \
--dst "${BACKUP_DIR}" \
--force \
2>&1 \
| tee -a "${LOG_FILE}"

python3 "${SCRIPT_DIR}/bkup.py" \
archive \
--src "${BACKUP_DIR}" \
--dst "${ARCHIVE_DIR}" \
2>&1 \
| tee -a "${LOG_FILE}"

python3 "${SCRIPT_DIR}/bkup.py" \
clean \
--dst "${ARCHIVE_DIR}" \
--keep-count "${KEEP_COUNT}" \
--keep-days "${KEEP_DAYS}" \
2>&1 \
| tee -a "${LOG_FILE}"

if [ -n "${REMOTE}" ]; then
    python3 "${SCRIPT_DIR}/bkup.py" \
    upload \
    --src "${ARCHIVE_DIR}" \
    --dst "${REMOTE}" \
    2>&1 \
    | tee -a "${LOG_FILE}"
fi

echo -------------------------------------------------------------------------------- | tee -a "${LOG_FILE}"
echo END | tee -a "${LOG_FILE}"
date -R  | tee -a "${LOG_FILE}"
echo -------------------------------------------------------------------------------- | tee -a "${LOG_FILE}"
echo "" | tee -a "${LOG_FILE}"
