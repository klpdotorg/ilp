#!/bin/sh
# Call this script with the database name
if [ $# -eq 0 ]; then
    echo "Please supply database name as argument. USAGE: `basename $0` databasename"
    exit 1;
fi
echo "######################"
echo "STARTING SCRIPT - POPULATE STATIC TABLES"
echo "######################"
dbname="$1";
#First give permissions to all the other scripts to run
chmod 777 *.sh
sh createEnums.sh $dbname
sh populateStatusTable.sh $dbname
sh populateAcademicYear.sh $dbname
sh populateInstCategory.sh $dbname
sh populateInstMgmt.sh $dbname

echo "######################"
echo "ENDING SCRIPT - POPULATE STATIC TABLES"
echo "######################"