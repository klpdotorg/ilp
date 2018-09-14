#!/bin/bash

WORK_DIR=/home/ubuntu/ilp
mkdir -p $WORK_DIR
chown -vc ubuntu:www-data $WORK_DIR || exit 1
cd $WORK_DIR
[[ -d venv ]] || /usr/bin/virtualenv -p /usr/bin/python3 venv
chown -R ubuntu:www-data venv || exit 1
chown -R $USER ~/.npm || exit 1
chown -R $USER /usr/lib/node_modules || exit 1
chown -R $USER /usr/local/lib/node_modules || exit 1
