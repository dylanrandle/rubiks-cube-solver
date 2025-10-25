#!/bin/bash

set -xe

HOST=rpi
USER=dylanrandle

rpi_sync() {
  if [ -z "$1" ]; then
    echo "Error: Please provide a local source directory."
    echo "Usage: rpi_sync /path/to/your/project"
    return 1
  fi

  REMOTE_USER_HOST="$USER@$HOST"
  REMOTE_BASE_PATH="/home/$USER/app/rubiks-cube-solver"

  # Strip trailing slash from input for consistent path handling
  SOURCE_DIR="${1%/}"

  # Extract the base directory name (e.g., from /home/user/project, it gets 'project')
  BASE_NAME=$(basename "$SOURCE_DIR")

  # Construct the full remote destination (e.g., .../deployment/project)
  DESTINATION="${REMOTE_USER_HOST}:${REMOTE_BASE_PATH}/${BASE_NAME}"

  echo "Synchronizing contents of ${SOURCE_DIR}/ to ${DESTINATION}/..."

  rsync -avz --progress \
    --exclude-from=.gitignore \
    "${SOURCE_DIR}/" \
    "${DESTINATION}/"
}

rpi_sync src
rpi_sync scripts
rpi_sync data
