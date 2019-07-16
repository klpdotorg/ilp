#!/bin/bash
if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
    echo "Usage: rungkaonlyreports.sh param1 param2 param3"
    echo "Parameters:"
    echo "- param1: Starting date of reports in yyyymm format. Eg. 201706"
    echo "- param2: End date of reports in yyyymm format. Eg. 201809"
    echo "- param3: Directory where all the contact CSV files reside. No Slash at the end. Eg. /home/ubuntu"
    echo "- param4: two character state code. Eg. ka, od etc.."
    exit 1
fi
FROM=$1
TO=$2
CSV_DIR_PATH=$3
# All config files are named in the following format: {statecode}_reports.ini
CONFIG_FILE = "apps/reports/config/" + $STATE_CODE + "_reports.ini"

TIMESTAMP=`date "+%Y-%m-%d %H:%M:%S"`
echo "Starting district  reports run $TIMESTAMP"
python manage.py sendreports DistrictReport --gka=True --gp=False --hhsurvey=False --from=$FROM --to=$TO --config=$CONFIG_FILE "$CSV_DIR_PATH/1million_districts.csv"
echo "Done sending reports"
TIMESTAMP=`date "+%Y-%m-%d %H:%M:%S"`
echo $TIMESTAMP      
echo "================================"
echo "Starting block  reports run `date '+%Y-%m-%d %H:%M:%S'`"
python manage.py sendreports BlockReport --gka=True --gp=False --hhsurvey=False --from=$FROM --to=$TO --config=$CONFIG_FILE "$CSV_DIR_PATH/1million_blocks.csv"
echo "Done sending reports"
TIMESTAMP=`date "+%Y-%m-%d %H:%M:%S"`
echo $TIMESTAMP
echo "================================"
echo "Starting cluster  reports run `date '+%Y-%m-%d %H:%M:%S'`"
python manage.py sendreports ClusterReport --gka=True --gp=False --hhsurvey=False --from=$FROM --to=$TO --config=$CONFIG_FILE "$CSV_DIR_PATH/1million_clusters.csv"
echo "Done sending reports"
TIMESTAMP=`date "+%Y-%m-%d %H:%M:%S"`
echo $TIMESTAMP      
echo "================================"
echo "Starting GPContest reports run `date '+%Y-%m-%d %H:%M:%S'`"
python manage.py sendreports GPMathContestReport --gka=False --gp=True --hhsurvey=False --from=$FROM --to=$TO --config=$CONFIG_FILE "$CSV_DIR_PATH/1million_gps.csv"
echo "Done sending reports"
TIMESTAMP=`date "+%Y-%m-%d %H:%M:%S"`
echo $TIMESTAMP
echo "================================"

