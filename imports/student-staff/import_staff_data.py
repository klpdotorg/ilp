from os import system,sys
import os, inspect


if len(sys.argv) != 3:
    print("Please give database names as arguments. USAGE: python import_staff_data.py ems ilp")
    sys.exit()

#Before running this script
#change this to point to the ems database that is used for getting the data
fromdatabase = sys.argv[1]

#change this to ilp db to be populated with
todatabase = sys.argv[2]

basename = "staff"
scriptdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

inputdatafile =  scriptdir+"/"+basename+"_getdata.sql"
loaddatafile =  scriptdir+"/"+basename+"_loaddata.sql"

mt_case = "when 1 then 'kan' when 2 then 'urd' when 3 then 'tam' when 4 then 'tel' when 5 then 'eng' when 6 then 'mar' when 7 then 'hin' when 8 then 'kon' when 9 then 'sin' when 10    then 'oth' when 11 then 'guj' when 12 then 'unknown' when 13 then 'multi' when 14 then   'nep' when 15 then 'ori' when 16 then 'ben' when 17 then 'mal' when 18 then 'san' when   19 then 'lam' end"

tables=[
    {
        'name': 'schools_qualification',
        'table_name': 'schools_qualification',
        'columns': 'id, name',
        'query': "\COPY (select id, qualification from schools_staff_qualifications) TO '"+scriptdir+"/load/schools_qualification.csv' NULL 'null' DELIMITER ',' quote '\\\"' csv;",
    },
    {
        'name': 'schools_stafftype',
        'table_name': 'schools_stafftype',
        'columns': 'id, staff_type, institution_type_id',
        'query': "\COPY (select id, staff_type, case category_type when 1 then 'primary' when 2 then 'pre' end from schools_staff_type) TO '"+scriptdir+"/load/schools_stafftype.csv' NULL 'null' DELIMITER ',' quote '\\\"' csv;",
    },
    {
        'name': 'schools_staff',
        'table_name': 'schools_staff',
        'columns': 'id, first_name, middle_name, last_name, uid, doj, gender_id, institution_id, mt_id, staff_type_id, status_id',
        'query': "\COPY (select id, first_name, middle_name, last_name, uid, doj, gender, institution_id, case mt_id "+mt_case+", staff_type_id, 'AC' from schools_staff where active=2 and institution_id in (select id from schools_institution where active=2)) TO '"+scriptdir+"/load/schools_staff.csv' NULL 'null' DELIMITER ',' quote '\\\"' csv;",
    },
    {
        'name': 'schools_staffqualification',
        'table_name': 'schools_staffqualification',
        'columns': 'id, qualification_id, staff_id',
        'query': "\COPY (select sq.id, sq.staff_qualifications_id, sq.staff_id from schools_staff_qualification sq, schools_staff s where sq.staff_id=s.id and s.active=2 and s.institution_id in (select id from schools_institution where active=2))  TO '"+scriptdir+"/load/schools_staffqualification.csv' NULL 'null' DELIMITER ',' quote '\\\"' csv;",
    }
]

#Create directory and files
def init():
    if not os.path.exists(scriptdir+"/load"):
    	os.makedirs(scriptdir+"/load")
    inputfile = open(inputdatafile,'wb',0)
    loadfile = open(loaddatafile,'wb',0)


#Create the getdata.sql and loaddata.sql files
# getdata.sql file has the "Copy to" commands for populating the various csv files
# loaddata.sql file has the "copy from" commands for loading the data into the db
def create_sqlfiles():
    #Loop through the tables
    for table in tables:
        #create the "copy to" file to get data from ems
        system('echo "'+table['query']+'\">>'+inputdatafile)

        #create the file where the data will be written into
        filename = scriptdir+'/load/'+table['name']+'.csv'
        open(filename,'wb',0)
        os.chmod(filename,0o666)

        #create the "copy from" file to load data into db
        system('echo "\COPY '+table['table_name']+"("+table['columns']+") from '"+filename+"' with csv NULL 'null';"+'\">>'+loaddatafile)


#Running the "copy to" commands to populate the csvs.
def getdata():
    system("psql -U klp -d "+fromdatabase+" -f "+inputdatafile)


#Running the "copy from" commands for loading the db.
def loaddata():
    system("psql -U klp -d "+todatabase+" -f "+loaddatafile)


#order in which function should be called.
init()
create_sqlfiles()
getdata()
loaddata()
