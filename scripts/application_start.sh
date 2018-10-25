#!/bin/bash

systemctl start ka.service || exit 1
systemctl start od.service || exit 1
systemctl start jk.service || exit 1
cd /home/ubuntu/ilp/postman_tests ##./runallreadonlytests.sh environments/development_env.json || exit 1
if [[ `hostname` == "ilpdev" ]]; then
  ./runallreadonlytests.sh environments/development_env.json
   m=$(echo $?)
 elif [[ `hostname` == "ilp-staging" ]]; then
  ./runallreadonlytests.sh environments/staging_env.json
   m=$(echo $?)
 else
    echo "None of the condition met"
fi || exit 1
if [ $m -ne 0 ]
then
 #zip -r test_results_summary test_results_summary.zip
 rm -rf test_results_summary.zip
 zip -r test_results_summary . -i test_results_summary.zip
 mail -s "Warning: Postman tests failure post-deployment. Check deployment"  dev@klp.org.in -A test_results_summary.zip
fi
 
