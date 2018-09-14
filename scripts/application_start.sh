#!/bin/bash

systemctl start ka.service || exit 1
systemctl start od.service || exit 1
systemctl start jk.service || exit 1
cd ~/ilp/postman_tests
./runreadonlytests.sh environments/development_env.json || exit 1
