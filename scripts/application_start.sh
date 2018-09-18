#!/bin/bash

systemctl start ka.service || exit 1
systemctl start od.service || exit 1
systemctl start jk.service || exit 1
cd /home/ubuntu/ilp/postman_tests; ./runallreadonlytests.sh environments/development_env.json || exit 1
