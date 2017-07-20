#!/bin/sh
# Call this script with the database name
if [ $# -eq 0 ]; then
    echo "Please supply database name as argument. USAGE: `basename $0` databasename"
    exit 1;
fi
echo "######################"
echo "STARTING SCRIPT - START IMPORTING DATA"
echo "######################"
dbname="$1";
boundaryFolder="boundary";
institutionFolder="institution";

#Start with common folder..
cd $boundaryFolder
chmod 777 *.sh;
sh populateBoundaryTables.sh $dbname
