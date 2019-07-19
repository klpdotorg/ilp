#run script
LOGFILE="refresh_mvs_p2_`date +"%Y%m%d%H%M"`.log"
echo "[INFO] - refresh_mvs_p2.sh has started" >> ${LOGFILE}
psql -U $2 -d $3 --echo-queries -f $1/refresh_materialized_view_p2.sql >> ${LOGFILE}
echo "[INFO] - refresh_mvs_p2.sh has finished" >>${LOGFILE}
