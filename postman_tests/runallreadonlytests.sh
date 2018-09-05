#!/bin/bash
if [ $# -eq 0 ]
  then
    echo "Call this script with an environment json file path"
    exit 1
fi
newman run collections/boundary_endpoints.postman_collection.json -e $1 --bail newman
exit_code=$?
echo "Exit code from newman is: $exit_code"
if [ $exit_code != 0 ]
then
    echo "Exit is not clean. Tests failed"
    exit $exit_code
else
    echo "All tests passed. We're good to go"
fi