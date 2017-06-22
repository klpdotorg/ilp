#!/bin/sh
# Call this script with the database name
if [ $# -eq 0 ]; then
    echo "Please supply database name as argument. USAGE: `basename $0` databasename"
    exit 1;
fi
echo "######################"
echo "STARTING SCRIPT - CREATE ENUMERATED TYPES"
echo "######################"
dbname="$1";
echo $1
psql -U klp -d $dbname -f sql/createEnums.sql
exit_status=$?
if [ $exit_status -eq 1 ]; then
    echo "SQL script execution failed with error";
    exit $exit_status;
fi
echo "Script executed successfully";
echo "######################"
echo "ENDING SCRIPT - CREATE ENUMERATED TYPES"
echo "######################"
