from os import system,sys
import os

if len(sys.argv) != 3:
    print("Please give database names as arguments. USAGE: python updateinstitution_disecode.py ems ilp", file=sys.stderr)
    sys.exit()


#Before running this script
#change this to point to the ems database that is used for getting the data
fromdatabase = sys.argv[1]

#change this to ilp db to be populated with
todatabase = sys.argv[2]

basename = "updatedise"
inputsqlfile = basename+"_getdata.sql"
loadsqlfile = basename+"_loaddata.sql"


tables=[
        {
            'name': 'schools_institution',
            'getquery': "COPY(select id, dise_code::bigint from replacetablename where dise_code is not null and dise_code ~ '^[0-9]') TO 'replacefilename' NULL 'null' DELIMITER   ',' quote '\\\"' csv;",
            'tempquery': "CREATE TEMP TABLE temp_replacetablename(id integer, dise_code bigint); COPY temp_replacetablename(id, dise_code) FROM 'replacefilename' with csv NULL 'null'; select count(*) from schools_institution where id in (select id from temp_replacetablename);",
            'updatequery': "UPDATE schools_institution set dise_id=disedata.id from dise_basicdata disedata, temp_replacetablename temp where disedata.school_code=temp.dise_code and disedata.academic_year_id='1516' and schools_institution.id=temp.id;"
        },
]

#Create directory and files
def init():
    if not os.path.exists("load"):
        os.makedirs("load")
    open(inputsqlfile, 'wb', 0)
    open(loadsqlfile, 'wb', 0)


#Create the getdata.sql and loaddata.sql files
# getdata.sql file has the "Copy to" commands for populating the various csv files
# loaddata.sql file has the "copy from" commands for loading the data into the db
def create_sqlfiles():
    #Loop through the tables
    for table in tables:
        filename = os.getcwd()+'/load/'+basename+'_'+table['name']+'.csv'
        open(filename, 'wb', 0)
        os.chmod(filename, 0o666)
        if 'getquery' in table:
            command = 'echo "'+table['getquery'].replace('replacetablename', table['name']).replace('replacefilename', filename)+'">>'+inputsqlfile
            system(command)
        if 'tempquery' in table:
            command = 'echo "'+table['tempquery'].replace('replacetablename', table['name']).replace('replacefilename', filename)+'">>'+loadsqlfile
            system(command)
        if 'updatequery' in table:
            command = 'echo "'+table['updatequery'].replace('replacetablename', table['name']).replace('replacefilename', filename)+'">>'+loadsqlfile
            system(command)



#Running the "copy to" commands to populate the csvs.
def getdata():
    system("psql -U klp -d "+fromdatabase+" -f "+inputsqlfile)


#Running the "copy from" commands for loading the db.
def loaddata():
    system('psql -U klp -d '+todatabase+' -f '+loadsqlfile)


#order in which function should be called.
init()
create_sqlfiles()
getdata()
loaddata()
