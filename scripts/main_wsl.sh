# No shebang: include only
# shellcheck shell=bash

# Automatic backup script for WSL
# Create a separate script file and set required parameters,
# then include this file by "." or "source".

# Check required parameters
set -u
# Propagate backup command failures through tee.
set -o pipefail
# !!! Required Variables !!!
echo "SRC_DIRS:   ${SRC_DIRS}"
echo "DST_DIR:    ${DST_DIR}"
echo "KEEP_COUNT: ${KEEP_COUNT}"
echo "KEEP_DAYS : ${KEEP_DAYS}"
echo "REMOTE:     ${REMOTE}"
# !!! Required Variables !!!

ARCHIVE_DIR=${DST_DIR}
LOG_DIR=${DST_DIR}
LOG_FILE=${LOG_DIR}/backup.log
SELF_DIR=$(dirname "$(realpath "$0")")
SCRIPT_DIR=${SELF_DIR}/../src


mkdir -p "${LOG_DIR}"
echo -------------------------------------------------------------------------------- | tee -a "${LOG_FILE}"
echo START | tee -a "${LOG_FILE}"
date -R    | tee -a "${LOG_FILE}"
echo -------------------------------------------------------------------------------- | tee -a "${LOG_FILE}"

# shellcheck disable=SC2086
python3 "${SCRIPT_DIR}/bkup.py" \
archive \
--src ${SRC_DIRS} \
--dst "${ARCHIVE_DIR}" \
2>&1 \
| tee -a "${LOG_FILE}" || return "$?"

python3 "${SCRIPT_DIR}/bkup.py" \
clean \
--dst "${ARCHIVE_DIR}" \
--keep-count "${KEEP_COUNT}" \
--keep-days "${KEEP_DAYS}" \
2>&1 \
| tee -a "${LOG_FILE}" || return "$?"

if [ -n "${REMOTE}" ]; then
    python3 "${SCRIPT_DIR}/bkup.py" \
    upload \
    --src "${ARCHIVE_DIR}" \
    --dst "${REMOTE}" \
    2>&1 \
    | tee -a "${LOG_FILE}" || return "$?"
fi

echo -------------------------------------------------------------------------------- | tee -a "${LOG_FILE}"
echo END | tee -a "${LOG_FILE}"
date -R  | tee -a "${LOG_FILE}"
echo -------------------------------------------------------------------------------- | tee -a "${LOG_FILE}"
echo "" | tee -a "${LOG_FILE}"
