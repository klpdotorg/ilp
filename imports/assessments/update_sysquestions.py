from os import sys
import os
import inspect
import csv
import datetime
import psycopg2
import re


if len(sys.argv) != 3:
    print("Please give directory and database names as arguments. USAGE: " +
          "python update_sysquestions.py pathtofilesdir ilp")
    sys.exit()

fromdir = sys.argv[1]

todatabase = sys.argv[2]

basename = "sysquestions"
scriptdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
inputsqlfile = scriptdir+"/"+basename+"_getdata.sql"
loadsqlfile = scriptdir+"/"+basename+"_loaddata.sql"


connectionstring = "dbname=%s user=klp" % todatabase


for filename in os.listdir(fromdir):
    if not filename.endswith(".csv"):
        continue
    conn = psycopg2.connect(connectionstring)
    cursor = conn.cursor()
    f = open(fromdir+"/"+filename, 'r')
    csv_f = csv.reader(f)

    count = 0
    for row in csv_f:
        if count < 1:
            count += 1
            continue

        question_id = row[0].strip()
        new_key = row[2].strip()
        new_displaytext = row[5]

        sqlupdate= "update assessments_question set key=%s, display_text=%s where id=%s;"
        cursor.execute(sqlupdate, (new_key, new_displaytext, question_id))
        conn.commit()

    conn.commit()
    cursor.close()
    conn.close()
