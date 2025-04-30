#!/bin/bash -xue

# Register sample_wsl.sh on Windows TaskScheduler.

SELF_DIR=$(dirname "$(realpath "$0")")

DEF_TASK_NAME="backup\\wsl"
DEF_TASK_CMD="sample_wsl.sh"
# Every month, day, time
DEF_TASK_OPT="/SC MONTHLY /D 1 /ST 04:00"

read -r -p "Task Name (default: ${DEF_TASK_NAME}): " TASK_NAME
read -r -p "Task Command (default: ${DEF_TASK_CMD}): " TASK_CMD
read -r -p "Task Options (default: ${DEF_TASK_OPT}): " TASK_OPT
echo "${TASK_NAME:=${DEF_TASK_NAME}}"
echo "${TASK_CMD:=${DEF_TASK_CMD}}"
echo "${TASK_OPT:=${DEF_TASK_OPT}}"

# use TASK_OPT as is
# shellcheck disable=SC2086
schtasks.exe /Create /F /TN ${TASK_NAME} ${TASK_OPT} /TR "wsl.exe --cd ~ -e ${SELF_DIR}/${TASK_CMD}"

echo Notice!
echo Win+R \"taskschd.msc\" to change more detailed settings.
