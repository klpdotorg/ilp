#!/bin/bash

WORK_DIR=/home/ubuntu/ilp_deploy
mkdir -p $WORK_DIR
chown -vc ubuntu:www-data $WORK_DIR || exit 1
cd $WORK_DIR
/usr/bin/virtualenv -p /usr/bin/python3 venv || exit 1
chown -R ubuntu:www-data venv || exit 1
