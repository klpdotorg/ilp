#!/bin/bash

mkdir -p /home/ubuntu/ilp_deploy
chown -vc ubuntu:www-data /home/ubuntu/ilp_deploy || exit 1
cd /home/ubuntu/ilp_deploy
/usr/bin/virtualenv -p /usr/bin/python3 venv || exit 1
chown -R ubuntu:www-data venv || exit 1
