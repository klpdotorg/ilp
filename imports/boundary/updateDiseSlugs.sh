#!/bin/sh
# Call this script with the database name
if [ $# -eq 0 ]; then
    echo "Please supply database names as argument. USAGE: `basename $0` olddatabasename newdatabasename"
    exit 1;
fi
echo "######################"
echo "STARTING SCRIPT - UPDATE DISE SLUGS"
echo "######################"
dbname="$1";
echo $1
psql -U klp -d $dbname -f `dirname $0`/sql/updatediseslugs.sql
exit_status=$?
if [ $exit_status -eq 1 ]; then
    echo "SQL script execution failed with error";
    exit $exit_status;
fi
echo "Script executed successfully";
echo "######################"
echo "ENDING SCRIPT - UPDATE DISE SLUGS"
echo "######################"
