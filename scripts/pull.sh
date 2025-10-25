#!/bin/bash

set -xe

HOST=rpi
USER=dylanrandle

rsync -avz --progress --include='*.jpg' \
    $USER@$HOST:"/home/$USER/app/rubiks-cube-solver/debug/" debug