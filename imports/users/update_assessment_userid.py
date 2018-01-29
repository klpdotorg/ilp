from os import system, sys
import os
import inspect

if len(sys.argv) != 3:
    print("Please give database names as arguments. USAGE: python update_assessment_userid.py dubdubdub ilp")
    sys.exit()

fromdatabase = sys.argv[1]

todatabase = sys.argv[2]

basename = "updateuserid"
scriptdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

inputsqlfile = scriptdir+"/"+basename+"_getdata.sql"
loadsqlfile = scriptdir+"/"+basename+"_loaddata.sql"

tables = [
        {
            'name': 'assessments_answergroup_institution',
            'getquery': "\COPY (select id, user_id from stories_story where user_id is not null) TO 'replacefilename' NULL 'null' DELIMITER   ',' quote '\\\"' csv;",
            'tempquery': "CREATE TEMP TABLE temp_replacetablename(id integer, user_id integer); \COPY temp_replacetablename(id, user_id) FROM 'replacefilename' with csv NULL 'null';",
            'updatequery': "UPDATE replacetablename set created_by_id=temp.user_id from  temp_replacetablename temp, users_user users where replacetablename.id=temp.id and temp.user_id = users.id;"
        },
        {
            'name': 'assessments_answergroup_student',
            'getquery': "\COPY (select id, user_id from stories_story where user_id is not null) TO 'replacefilename' NULL 'null' DELIMITER   ',' quote '\\\"' csv;",
            'tempquery': "CREATE TEMP TABLE temp_replacetablename(id integer, user_id integer); \COPY temp_replacetablename(id, user_id) FROM 'replacefilename' with csv NULL 'null';",
            'updatequery': "UPDATE replacetablename set created_by_id=temp.user_id from  temp_replacetablename temp, users_user users where replacetablename.id=temp.id and temp.user_id = users.id;"
        }
]


# Create directory and files
def init():
    if not os.path.exists(scriptdir+"/load"):
        os.makedirs(scriptdir+"/load")
    open(inputsqlfile, 'wb', 0)
    open(loadsqlfile, 'wb', 0)


# Create the getdata.sql and loaddata.sql files
# getdata.sql file has the "Copy to" commands for populating the various csv files
# loaddata.sql file has the "copy from" commands for loading the data into the db
def create_sqlfiles():
    # Loop through the tables
    for table in tables:
        filename = scriptdir+'/load/'+basename+'_'+table['name']+'.csv'
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


# Running the "copy to" commands to populate the csvs.
def getdata():
    system("psql -U klp -d "+fromdatabase+" -f "+inputsqlfile)


# Running the "copy from" commands for loading the db.
def loaddata():
    system('psql -U klp -d '+todatabase+' -f '+loadsqlfile)


# order in which function should be called.
init()
create_sqlfiles()
getdata()
loaddata()
