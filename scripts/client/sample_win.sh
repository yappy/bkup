#!/bin/bash -u

# Automatic backup script for Windows
#
# Copy this file and replace the parameters.
#
# Windows command for TaskScheduler:
# > wsl.exe --cd ~ --exec <./path/to/this.sh>

# !!! REPLACE HERE !!!
SRC_DIRS="/mnt/c/Users"
DST_DIR=/mnt/d/backup/win
KEEP_COUNT=12
KEEP_DAYS=365
# Use ~/.ssh/config
# Disable upload by empty string
REMOTE=shanghai:/mnt/inbox
# !!! REPLACE HERE !!!

SELF_DIR=$(dirname "$(realpath "$0")")
. "${SELF_DIR}/main_win.sh"
