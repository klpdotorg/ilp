#!/bin/bash

systemctl start ka.service || exit 1
systemctl start od.service || exit 1
systemctl start jk.service || exit 1
cd /home/ubuntu/ilp/postman_tests ##./runallreadonlytests.sh environments/development_env.json || exit 1
if [[ `hostname` == "ilpdev" ]]; then
  ./runallreadonlytests.sh environments/development_env.json
 elif [[ `hostname` == "ilp-staging" ]]; then
  ./runallreadonlytests.sh environments/staging_env.json
 else
    echo "None of the condition met"
fi
