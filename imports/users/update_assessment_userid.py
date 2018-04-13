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
            'table_name': 'assessments_answergroup_institution',
            'name': 'assessments_answergroup_institution_1',
            'getquery': "\COPY (select id, case when user_id=1 then 2 else user_id end,group_id from stories_story where user_id is not null and user_id in (select id from users_user where mobile_no not like '%,%')) TO 'replacefilename' NULL 'null' DELIMITER   ',' quote '\\\"' csv;",
            'tempquery': "CREATE TEMP TABLE temp_replacetablename(id integer, user_id integer, group_id integer); \COPY temp_replacetablename(id, user_id, group_id) FROM 'replacefilename' with csv NULL 'null';",
            'updatequery': "UPDATE replacetablename set created_by_id=users.id from  temp_replacetablename temp, users_user users where replacetablename.id=temp.id and temp.user_id = users.id and replacetablename.questiongroup_id=temp.group_id;"
        },
        {
            'table_name': 'assessments_answergroup_institution',
            'name': 'assessments_answergroup_institution_2',
            'getquery': "\COPY (select story.id, story.user_id, story.group_id, split_part(users.mobile_no,',',1) from stories_story story, users_user users where story.user_id = users.id and users.mobile_no like '%,%') TO 'replacefilename' NULL 'null' DELIMITER   ',' quote '\\\"' csv;",
            'tempquery': "CREATE TEMP TABLE temp_replacetablename(id integer, user_id integer, group_id integer, mobile_no text); \COPY temp_replacetablename(id, user_id, group_id, mobile_no) FROM 'replacefilename' with csv NULL 'null';",
            'updatequery': "UPDATE replacetablename set created_by_id=users.id from  temp_replacetablename temp, users_user users where replacetablename.id=temp.id and users.mobile_no = temp.mobile_no and replacetablename.questiongroup_id=temp.group_id;"
        },
        {
            'table_name': 'assessments_answergroup_student',
            'name': 'assessments_answergroup_student_1',
            'getquery': "\COPY (select id, user_id, group_id from stories_story where user_id is not null and user_id in (select id from users_user where mobile_no not like '%,%')) TO 'replacefilename' NULL 'null' DELIMITER   ',' quote '\\\"' csv;",
            'tempquery': "CREATE TEMP TABLE temp_replacetablename(id integer, user_id integer, group_id integer); \COPY temp_replacetablename(id, user_id, group_id) FROM 'replacefilename' with csv NULL 'null';",
            'updatequery': "UPDATE replacetablename set created_by_id=users.id from  temp_replacetablename temp, users_user users where replacetablename.id=temp.id and temp.user_id = users.id and replacetablename.questiongroup_id = temp.group_id;"
        },
        {
            'table_name': 'assessments_answergroup_student',
            'name': 'assessments_answergroup_student_2',
            'getquery': "\COPY (select story.id, story.user_id, story.group_id, split_part(users.mobile_no,',',1) from stories_story story, users_user users where story.user_id = users.id and users.mobile_no like '%,%') TO 'replacefilename' NULL 'null' DELIMITER   ',' quote '\\\"' csv;",
            'tempquery': "CREATE TEMP TABLE temp_replacetablename(id integer, user_id integer, group_id integer, mobile_no text); \COPY temp_replacetablename(id, user_id, group_id, mobile_no) FROM 'replacefilename' with csv NULL 'null';",
            'updatequery': "UPDATE replacetablename set created_by_id=users.id from  temp_replacetablename temp, users_user users where replacetablename.id=temp.id and users.mobile_no = temp.mobile_no and replacetablename.questiongroup_id=temp.group_id;"
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
            command = 'echo "'+table['getquery'].replace('temp_replacetablename', table['name']).replace('replacefilename', filename).replace('replacetablename', table['table_name'])+'">>'+inputsqlfile
            system(command)
        if 'tempquery' in table:
            command = 'echo "'+table['tempquery'].replace('temp_replacetablename', table['name']).replace('replacefilename', filename).replace('replacetablename', table['table_name'])+'">>'+loadsqlfile
            system(command)
        if 'updatequery' in table:
            command = 'echo "'+table['updatequery'].replace('temp_replacetablename', table['name']).replace('replacefilename', filename).replace('replacetablename', table['table_name'])+'">>'+loadsqlfile
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
