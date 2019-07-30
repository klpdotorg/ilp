import psycopg2
import csv

conn = psycopg2.connect("host=localhost dbname=ilp_latest user=klp")
cur = conn.cursor()
with open('notinilp.csv') as schools:
    readCSV = csv.reader(schools, delimiter=',')
    for row in readCSV:
        district_name = row[1]
        block_name = row[3]
        cluster_name = row[4]
        school_code = row[5]
        school_name = row[6]
        school_mgmt = row[7]
        school_medium = row[12]
        district_query = "select id from boundary_boundary where name={}".format(row[1])
        cur.execute(district_query)
        row = cur.fetchone()
        district_id = row[1][1]
        print("District id is:", district_id)
