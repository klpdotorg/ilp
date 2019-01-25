#!/bin/bash
if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
    echo "Usage: runallreports.sh param1 param2 param3"
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
python manage.py sendreports DistrictReport --from=$FROM --to=$TO --config="apps/reports/config/ka_reports.ini" "$CSV_DIR_PATH/1million_districts.csv" 
echo "Done sending reports"
TIMESTAMP=`date "+%Y-%m-%d %H:%M:%S"`
echo $TIMESTAMP      
echo "================================"
echo "Starting district summarized  reports run `date '+%Y-%m-%d %H:%M:%S'`"
python manage.py sendreports DistrictReportSummarized --from=$FROM --to=$TO --config="apps/reports/config/ka_reports.ini" "$CSV_DIR_PATH/1million_districts.csv"
echo "Done sending reports"
TIMESTAMP=`date "+%Y-%m-%d %H:%M:%S"`
echo $TIMESTAMP  
echo "================================"
echo "Starting block  reports run `date '+%Y-%m-%d %H:%M:%S'`"
python manage.py sendreports BlockReport --from=$FROM --to=$TO --config="apps/reports/config/ka_reports.ini" "$CSV_DIR_PATH/1million_blocks.csv"
echo "Done sending reports"
TIMESTAMP=`date "+%Y-%m-%d %H:%M:%S"`
echo $TIMESTAMP
echo "================================"
echo "Starting block summarized reports run `date '+%Y-%m-%d %H:%M:%S'`"
python manage.py sendreports BlockReportSummarized --from=$FROM --to=$TO --config="apps/reports/config/ka_reports.ini" "$CSV_DIR_PATH/1million_blocks.csv"
echo "Done sending reports"
TIMESTAMP=`date "+%Y-%m-%d %H:%M:%S"`
echo $TIMESTAMP
echo "================================"
echo "Starting cluster  reports run `date '+%Y-%m-%d %H:%M:%S'`"
python manage.py sendreports ClusterReport --from=$FROM --to=$TO --config="apps/reports/config/ka_reports.ini" "$CSV_DIR_PATH/1million_clusters.csv"
echo "Done sending reports"
TIMESTAMP=`date "+%Y-%m-%d %H:%M:%S"`
echo $TIMESTAMP      
echo "================================"
echo "Starting Cluster SUMMARIZED reports run `date '+%Y-%m-%d %H:%M:%S'`"
python manage.py sendreports ClusterReportSummarized --from=$FROM --to=$TO --config="apps/reports/config/ka_reports.ini" "$CSV_DIR_PATH/1million_clusters.csv"
echo "Done sending reports"
TIMESTAMP=`date "+%Y-%m-%d %H:%M:%S"`
echo $TIMESTAMP
echo "================================"
echo "Starting GPContest reports run `date '+%Y-%m-%d %H:%M:%S'`"
python manage.py sendreports GPMathContestReport --from=$FROM --to=$TO --config="apps/reports/config/ka_reports.ini" "$CSV_DIR_PATH/1million_gps.csv"
echo "Done sending reports"
TIMESTAMP=`date "+%Y-%m-%d %H:%M:%S"`
echo $TIMESTAMP
echo "================================"
echo "Starting GPContest summarized reports run `date '+%Y-%m-%d %H:%M:%S'`"
python manage.py sendreports GPMathContestReportSummarized --from=$FROM --to=$TO --config="apps/reports/config/ka_reports.ini" "$CSV_DIR_PATH/1million_gps.csv"
echo "Done sending reports"
TIMESTAMP=`date "+%Y-%m-%d %H:%M:%S"`
echo $TIMESTAMP
echo "================================"
echo "Starting School reports run `date '+%Y-%m-%d %H:%M:%S'`"
python manage.py sendreports SchoolReport --from=$FROM --to=$TO --config="apps/reports/config/ka_reports.ini" "$CSV_DIR_PATH/1million_schools.csv"
echo "Done sending reports"
TIMESTAMP=`date "+%Y-%m-%d %H:%M:%S"`
echo $TIMESTAMP
    
    
