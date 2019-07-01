#run script
LOGFILE="refresh_mvs_p1_`date +"%Y%m%d%H%M"`.log"
echo "[INFO] - refresh_mvs_p1.sh has started" >> ${LOGFILE}
psql -U $2 -d $3 --echo-queries -f $1/refresh_materialized_view_p1.sql >> ${LOGFILE}
echo "[INFO] - refresh_mvs_p1.sh has finished" >>${LOGFILE}
