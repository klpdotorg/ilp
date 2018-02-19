#!/bin/bash
# Call this script with the database name
if [ $# -eq 0 ]; then
    echo "Please supply database names as argument. USAGE: `basename $0` klpdbname electrepdbname newdatabasename pathtostorecsvs pathtosqls"
    exit 1;
fi
echo "######################"
echo "STARTING SCRIPT - POPULATE BOUNDARY TABLES"
echo "######################"
legacydb="$1";
ilpdbname="$3";
electedrepdbname="$2";
csvdirname="$4";
sqldir="$5";

mkdir -p $csvdirname

#Delete from tables
psql -U klp -d $ilpdbname -f $sqldir/deleteFromTables.sql

#Export the boundary table data
boundaryfile=$csvdirname"/boundaries.csv"
query=`cat $sqldir/exportBoundaryData.sql`
query="${query/replacefilename/$boundaryfile}"
psql -U klp -d $legacydb -c "$query"

#Import the boundary table data
query=`cat $sqldir/importBoundaryTable.sql`
query="${query/replacefilename/$boundaryfile}"
psql -U klp -d $ilpdbname --set=inputdir="$csvdirname" -c "$query"

exit_status=$?
if [ $exit_status -eq 1 ]; then
    echo "SQL script execution failed with error";
    exit $exit_status;
fi

#Populate the boundary neighbors table
python `dirname $0`"/"loadBoundaryNeighbors.py $ilpdbname
exit_status=$?
if [ $exit_status -eq 1 ]; then
    echo "Python script execution failed with error";
    exit $exit_status;
fi

#Export the election boundary data from electrep_new DB
electionboundaryfile=$csvdirname"/electionboundary.csv"
electionneighboursfile=$csvdirname"/electboundneighbours.csv"

query=`cat $sqldir/exportElectionBoundary.sql`
query="${query/replacefilename/$electionboundaryfile}"
psql -U klp -d $electedrepdbname -c "$query"

query=`cat $sqldir/exportElectionNeighbours.sql`
query="${query/replacefilename/$electionneighboursfile}"
psql -U klp -d $electedrepdbname -c "$query"

#Import the election boundary data from the CSV into boundary_electionboundary table
query=`cat $sqldir/importElectionBoundary.sql`
query="${query/replacefilename/$electionboundaryfile}"
psql -U klp -d $ilpdbname -c "$query"

query=`cat $sqldir/importElectionNeighbours.sql`
query="${query/replacefilename/$electionneighboursfile}"
psql -U klp -d $ilpdbname -c "$query"
exit_status=$?
if [ $exit_status -eq 1 ]; then
    echo "SQL script execution failed with error";
    exit $exit_status;
fi
echo "Script executed successfully";
echo "######################"
echo "ENDING SCRIPT - POPULATE BOUNDARY TABLES"
echo "######################"
