from os import system, sys
import os
import inspect


if len(sys.argv) != 3:
    print("Please give database names as arguments. USAGE: python import_student_data.py ems ilp")
    sys.exit()

fromdatabase = sys.argv[1]

todatabase = sys.argv[2]

basename = "student"
scriptdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

inputdatafile = scriptdir+"/"+basename+"_getdata.sql"
loaddatafile = scriptdir+"/"+basename+"_loaddata.sql"

mt_case = "when 1 then 'kan' when 2 then 'urd' when 3 then 'tam' when 4 then 'tel' when 5 then 'eng' when 6 then 'mar' when 7 then 'hin' when 8 then 'kon' when 9 then 'sin' when 10    then 'oth' when 11 then 'guj' when 12 then 'unknown' when 13 then 'multi' when 14 then   'nep' when 15 then 'ori' when 16 then 'ben' when 17 then 'mal' when 18 then 'san' when   19 then 'lam'"

tables = [
    {
        'name': 'schools_student_primary',
        'table_name': 'schools_student',
        'columns': 'id, first_name, middle_name, last_name, uid, dob, gender_id, mt_id, institution_id, status_id',
        'query': "\COPY (select stu.id, c.first_name, c.middle_name, c.last_name, c.uid, c.dob, case c.gender when '' then 'male' else c.gender end, case c.mt_id "+mt_case+" end, stu.sid,'AC' from schools_child c ,(select distinct stu.id as id, stu.child_id as child_id, s.id as sid from  schools_student stu, schools_boundary b, schools_student_studentgrouprelation stusg, schools_studentgroup sg, schools_institution s where stu.id = stusg.student_id and stu.active=2 and stusg.student_group_id = sg.id and stusg.academic_id=105 and stusg.active in (0,1,2) and sg.institution_id=s.id and s.active =2 and s.boundary_id=b.id and b.boundary_type_id=1)stu where  stu.child_id = c.id and c.first_name <> '')TO '"+scriptdir+"/load/schools_student_primary.csv' NULL 'null' DELIMITER ',' quote '\\\"' csv;",
    },
    {
        'name': 'schools_student_pre',
        'table_name': 'schools_student',
        'columns': 'id, first_name, middle_name, last_name, uid, dob, gender_id,mt_id, institution_id, status_id',
        'query': "\COPY (select stu.id, c.first_name, c.middle_name, c.last_name, c.uid, c.dob, c.gender, case c.mt_id "+mt_case+"  end, stu.sid, 'AC' from schools_child c ,(select distinct stu.id as id,stu.child_id as child_id, s.id as sid from schools_student stu, schools_student_studentgrouprelation stusg, schools_studentgroup sg, schools_institution s, schools_boundary b where stu.id = stusg.student_id and stu.active=2 and stusg.student_group_id = sg.id and stusg.active in (0,1,2) and  sg.institution_id=s.id and s.active=2 and s.boundary_id=b.id and b.boundary_type_id=2)stu where stu.child_id = c.id and c.first_name <> '' and date_part('year',age(timestamp '2017-03-31',c.dob))<7 )TO '"+scriptdir+"/load/schools_student_pre.csv' NULL 'null' DELIMITER ',' quote '\\\"' csv;",
    }
]


# Create directory and files
def init():
    if not os.path.exists(scriptdir+"/load"):
        os.makedirs(scriptdir+"/load")
    open(inputdatafile, 'wb', 0)
    open(loaddatafile, 'wb', 0)


# Create the getdata.sql and loaddata.sql files
# getdata.sql file has the "Copy to" commands for populating the various csv files
# loaddata.sql file has the "copy from" commands for loading the data into the db
def create_sqlfiles():
    # Loop through the tables
    for table in tables:
        # create the "copy to" file to get data from ems
        system('echo "'+table['query']+'\">>'+inputdatafile)

        # create the file where the data will be written into
        filename = scriptdir+'/load/'+table['name']+'.csv'
        open(filename, 'wb', 0)
        os.chmod(filename, 0o666)

        # create the "copy from" file to load data into db
        system('echo "\COPY '+table['table_name']+"("+table['columns']+") from '"+filename+"' with csv NULL 'null';"+'\">>'+loaddatafile)


# Running the "copy to" commands to populate the csvs.
def getdata():
    system("psql -U klp -d "+fromdatabase+" -f "+inputdatafile)


# Running the "copy from" commands for loading the db.
def loaddata():
    system("psql -U klp -d "+todatabase+" -f "+loaddatafile)


# order in which function should be called.
init()
create_sqlfiles()
getdata()
loaddata()
