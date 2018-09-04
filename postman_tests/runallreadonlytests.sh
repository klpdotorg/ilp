#!/bin/bash
newman run collections/boundary_endpoints.postman_collection.json -e environments/development.postman_environment.json --bail newman
exit_code=$?
echo "Exit code from newman is: $exit_code"
if [ $exit_code != 0 ]
then
    echo "Exit is not clean. Tests failed"
else
    echo "All tests passed. We're good to go"
fi