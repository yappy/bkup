#!/bin/sh -xue

# Register sample_wsl.sh on Windows TaskScheduler.

# !!! REPLACE HERE !!!
TASK_NAME="backup\\wsl"
TASK_CMD="sample_wsl.sh"
# Every month, day, time
TASK_OPT="/SC MONTHLY /D 1 /ST 04:00"
# !!! REPLACE HERE !!!

SELF_DIR=$(dirname "$(realpath "$0")")

# use TASK_OPT as is
# shellcheck disable=SC2086
schtasks.exe /Create /F /TN ${TASK_NAME} ${TASK_OPT} /TR "wsl.exe --cd ~ -e ${SELF_DIR}/${TASK_CMD}"

echo Notice!
echo Win+R \"taskschd.msc\" to change more detailed settings.
