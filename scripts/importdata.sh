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
commonFolder="common";
institutionFolder="institution";

#Start with common folder..
cd $commonFolder
sh populateTables.sh $dbname
#Institution...
cd $institutionFolder
sh populateTables.sh $dbname
