#!/bin/sh
# Call this script with the database name
if [ $# -eq 0 ]; then
    echo "Please supply database names as argument. USAGE: `basename $0` olddatabasename newdatabasename"
    exit 1;
fi
echo "######################"
echo "STARTING SCRIPT - POPULATE BOUNDARY TABLES"
echo "######################"
legacydb="$1";
ilpdbname="$2";
psql -U klp -d $ilpdbname -f sql/deleteFromTables.sql
psql -U klp -d $ilpdbname -f sql/fillBoundaryStatics.sql
psql -U klp -d $legacydb -f sql/exportBoundaryData.sql
psql -U klp -d $ilpdbname -f sql/importBoundaryTable.sql
exit_status=$?
if [ $exit_status -eq 1 ]; then
    echo "SQL script execution failed with error";
    exit $exit_status;
fi
echo "Script executed successfully";
echo "######################"
echo "ENDING SCRIPT - POPULATE BOUNDARY TABLES"
echo "######################"