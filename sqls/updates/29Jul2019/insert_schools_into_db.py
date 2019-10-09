import psycopg2
import csv

if len(sys.argv) != 3:
    print("Please give database name, full path of CSV file and current DISE academic year id as arguments. USAGE: " +
          "python insert_phase3_schools.py ilp /home/xxxxxxx/schools.csv 1617")
    sys.exit()

dbname = sys.argv[1]
user = sys.argv[2]
host = sys.argv[3]
passwd = sys.argv[4]
# passwd="\\u4<AKdnC~y268GF6v"
connectionstring = "dbname="+dbname+" user="+user+" password="+passwd+" host="+host
conn = psycopg2.connect(host=host, database=dbname, user=user, password=passwd)
cur = conn.cursor()
with open('notinilp.csv') as schools:
    readCSV = csv.reader(schools, delimiter=',')
    count = 0;
    for row in readCSV:
        if count==0:
            count=1
            continue
        district_name = row[1].strip()
        block_name = row[3].strip()
        print("Block name: ", block_name)
        cluster_name = row[4].strip()
        school_code = row[5]
        school_name = row[6].strip()
        school_mgmt = 1
        school_medium = row[12].strip()
        #Decide school category based on school name
        if school_name.lower().find("lower primary") != -1 or school_name.lower().find("lps") != -1:
            school_mgmt = 13
        elif school_name.lower().find("higher primary") != -1 or school_name.lower().find("hps") != -1:
            school_mgmt = 14
        elif school_name.lower().find("model") != -1:
            school_mgmt = 9
        else:
            school_mgmt = 13
        # Fetch the district ID
        district_query = "select id from boundary_boundary where name=\'{0}\' and boundary_type_id=\'{1}\'".format(district_name.lower(), 'SD')
        cur.execute(district_query)
        current = cur.fetchone()
        district_id = int(current[0])
        print("District Name: %s; District id: %s" % (district_name, district_id))
        # Fetch the block ID
        block_query = "select id from boundary_boundary where name=\'{0}\' and boundary_type_id=\'{1}\'".format(block_name.lower(), 'SB')
        print(block_query)
        result = cur.execute(block_query)
        print(result)
        current = cur.fetchone()
        block_id = int(current[0])
        print("Block Name: %s ; Block ID is: %s" % (block_name, block_id))
        # Fetch the cluster ID
        cluster_query = "select id from boundary_boundary where name=\'{0}\' and boundary_type_id=\'{1}\'".format(cluster_name.lower(), 'SC')
        cur.execute(cluster_query)
        current = cur.fetchone()
        cluster_id = int(current[0])
        print("Cluster Name: %s; ID is: %s" % (cluster_name,cluster_id))
        # Fetch the GP ID
        gp_query = "select gp_id from schools_institution where admin1_id={0} and admin2_id={1} and admin3_id={2}".format(district_id,block_id,cluster_id)
        cur.execute(gp_query)
        #Assume all GPs in same cluster have same GP id
        current = cur.fetchall()
        gp_id = None
        # Some schools don't have GP ID set..just iterate through and find one that's set
        for row2 in current:
            if row2[0] is not None:
                gp_id=int(row2[0])
                break
        print("GP ID is: ", gp_id)
        dise_query="select id from dise_basicdata where school_code={}".format(school_code)
        cur.execute(dise_query)
        current = cur.fetchone()
        dise_id=int(current[0])
        # Insert into the schools table
        try:
            insert_query = "insert into schools_institution(\
                name,admin0_id,admin1_id, admin2_id, admin3_id,institution_type_id, category_id, gender_id, management_id, dise_id, status_id, gp_id)\
                values(\'{0}\', 2, {1}, {2}, {3}, 'primary', {4}, 'co-ed', 1,{5}, 'AC', {6})".format(school_name,district_id,block_id,cluster_id,school_mgmt,dise_id,gp_id)
            print(insert_query)
            cur.execute(insert_query)
        except Exception as e:
            print("Error inserting %s school" % school_code)
        else:
            print("DONE===>" + insert_query)
        conn.commit()