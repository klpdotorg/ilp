from os import sys
import os
import inspect
import csv
import datetime
import psycopg2
import re


if len(sys.argv) != 3:
    print("Please give directory and database names as arguments. USAGE: " +
          "python import_usersfromcsv.py pathtofilesdir ilp")
    sys.exit()

fromdir = sys.argv[1]

todatabase = sys.argv[2]

basename = "csvusers"
scriptdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
inputsqlfile = scriptdir+"/"+basename+"_getdata.sql"
loadsqlfile = scriptdir+"/"+basename+"_loaddata.sql"


connectionstring = "dbname=%s user=klp" % todatabase


def reset_sequences():
    conn = psycopg2.connect(connectionstring)
    cursor = conn.cursor()
    query = "SELECT setval('users_user_id_seq', COALESCE((SELECT MAX(id)+1 FROM users_user), 1), false);SELECT setval('users_userboundary_id_seq', COALESCE((SELECT MAX(id)+1 FROM users_userboundary), 1), false);SELECT setval('users_user_groups_id_seq', COALESCE((SELECT MAX(id)+1 FROM users_user_groups), 1), false);"
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()


for filename in os.listdir(fromdir):
    if not filename.endswith(".csv"):
        continue
    conn = psycopg2.connect(connectionstring)
    cursor = conn.cursor()
    f = open(fromdir+"/"+filename, 'r')
    csv_f = csv.reader(f)

    missing_ids = {}
    missing_ids['schools'] = []
    count = 0

    # reset sequences
    reset_sequences()

    present = 0
    not_present = 0
    mobile_empty = 0
    boundary_entry_present = 0
    boundary_inserted = 0
    for row in csv_f:
        if count < 2:
            count += 1
            continue

        school_id = row[4].strip()
        password = "NOT SET"
        email = row[11]
        mobile_no = row[10]
        first_name = row[3]
        user_type = 'VR'
        is_active = 'true'
        is_email_verified = 'false'
        is_mobile_verified = 'false'
        opted_email = 'false'
        is_superuser = 'false'
        is_staff = 'false'
        if mobile_no== '':
            mobile_empty+=1
            continue
        boundary = row[2].lower()
        sqlselect = "select id from boundary_boundary where name=%s;"
        cursor.execute(sqlselect, [boundary])
        result = cursor.fetchone()
        if result is not None:
            boundary_id = result[0]
        else:
            print("Incorrect boundary: "+boundary)


        sqlselect = "select id from users_user where mobile_no=%s or email=%s;"
        cursor.execute(sqlselect, (mobile_no,email))
        user_present = cursor.fetchone()
        if user_present is not None:
            user_id = user_present[0]
            present +=1
        else:
            not_present +=1
            sqlinsert = "insert into users_user(password,email,mobile_no,first_name,user_type_id,is_active,is_email_verified, is_mobile_verified, opted_email,is_superuser, is_staff) values(%s, %s, %s, %s, %s, %s, %s, %s ,%s, %s, %s) returning id;"
            cursor.execute(sqlinsert, (password, email, mobile_no, first_name,
                                       user_type, is_active, is_email_verified,
                                       is_mobile_verified, opted_email, is_superuser, is_staff))
            user_id = cursor.fetchone()[0]
            sqlinsert = "insert into users_user_groups(user_id, group_id) select %s,groups.id from auth_group groups where groups.name in ('ilp_auth_user', 'ilp_konnect_user');"
            cursor.execute(sqlinsert, [user_id])

        sqlselect = "select id from users_userboundary where boundary_id=%s and user_id=%s;"
        cursor.execute(sqlselect, (boundary_id, user_id))
        entry_present = cursor.fetchone()
        if entry_present:
            boundary_entry_present += 1
        else:
            boundary_inserted += 1
            sqlinsert = "insert into users_userboundary(boundary_id, user_id) values(%s, %s) returning id;"
            cursor.execute(sqlinsert, (boundary_id, user_id))


    print("User present: ",present)
    print("User not present: ",not_present)
    print("Mobile num is empty: ",mobile_empty)
    print("User Boundary entry present: ",boundary_entry_present)
    print("User Boundary entry not present: ",boundary_inserted)

    conn.commit()
    cursor.close()
    conn.close()
