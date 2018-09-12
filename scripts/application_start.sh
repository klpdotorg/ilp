#!/bin/bash

systemctl start ka.service || exit 1
systemctl start od.service || exit 1
systemctl start jk.service || exit 1
npm install -g newman
cd postman_tests
./runreadonlytests.sh environments/development_env.json
