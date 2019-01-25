#!/bin/bash
if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
    echo "Usage: rungponlyreports.sh param1 param2 param3"
    echo "Parameters:"
    echo "- param1: Starting date of reports in yyyymm format. Eg. 201706"
    echo "- param2: End date of reports in yyyymm format. Eg. 201809"
    echo "- param3: Directory where all the contact CSV files reside. No Slash at the end. Eg. /home/ubuntu"
    exit 1
fi
FROM=$1
TO=$2
CSV_DIR_PATH=$3

TIMESTAMP=`date "+%Y-%m-%d %H:%M:%S"`
echo "Starting district  reports run $TIMESTAMP"
python manage.py sendreports DistrictReport --gka=False --gp=True --hhsurvey=False --from=$FROM --to=$TO "$CSV_DIR_PATH/1million_districts.csv"
echo "Done sending reports"
TIMESTAMP=`date "+%Y-%m-%d %H:%M:%S"`
echo $TIMESTAMP      
echo "================================"
echo "Starting block  reports run `date '+%Y-%m-%d %H:%M:%S'`"
python manage.py sendreports BlockReport --gka=False --gp=True --hhsurvey=False --from=$FROM --to=$TO "$CSV_DIR_PATH/1million_blocks.csv"
echo "Done sending reports"
TIMESTAMP=`date "+%Y-%m-%d %H:%M:%S"`
echo $TIMESTAMP
echo "================================"
echo "Starting cluster  reports run `date '+%Y-%m-%d %H:%M:%S'`"
python manage.py sendreports ClusterReport --gka=False --gp=True --hhsurvey=False --from=$FROM --to=$TO "$CSV_DIR_PATH/1million_clusters.csv"
echo "Done sending reports"
TIMESTAMP=`date "+%Y-%m-%d %H:%M:%S"`
echo $TIMESTAMP      
echo "================================"
echo "Starting GPContest reports run `date '+%Y-%m-%d %H:%M:%S'`"
python manage.py sendreports GPMathContestReport --gka=False --gp=True --hhsurvey=False --from=$FROM --to=$TO "$CSV_DIR_PATH/1million_gps.csv"
echo "Done sending reports"
TIMESTAMP=`date "+%Y-%m-%d %H:%M:%S"`
echo $TIMESTAMP
echo "================================"

