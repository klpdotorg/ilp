from os import system, sys
import os
import inspect


if len(sys.argv) != 3:
    print("Please give database names as arguments. USAGE: " +
          "python import_ivrs_data.py dubdubdub ilp")
    sys.exit()

fromdatabase = sys.argv[1]

todatabase = sys.argv[2]

basename = "ivrs"
scriptdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
inputsqlfile = scriptdir+"/"+basename+"_getdata.sql"
loadsqlfile = scriptdir+"/"+basename+"_loaddata.sql"

tables = [
    {
        'name': 'ivrs_questiongrouptype',
        'getquery': "\COPY (select distinct id, name, is_active, questiongroup_id from ivrs_questiongrouptype) TO 'replacefilename' NULL 'null' DELIMITER ',' quote '\\\"' csv;",
        'insertquery': "\COPY replacetablename(id, name, is_active, questiongroup_id) FROM 'replacefilename' with csv NULL 'null';"
    },
    {
        'name': 'ivrs_state',
        'getquery': "\COPY (select id, session_id, school_id, answers, date_of_visit, telephone, is_processed, is_invalid, qg_type_id, raw_data, comments, user_id from ivrs_state) TO 'replacefilename' NULL 'null' DELIMITER ',' quote '\\\"' csv;",
        'tempquery': "CREATE TEMP TABLE temp_replacetablename(id integer, session_id text, school_id integer, answers character varying[], date_of_visit timestamp, telephone text, is_processed boolean, is_invalid boolean, qg_type_id integer, raw_data text, comments text, user_id integer); \COPY temp_replacetablename(id, session_id, school_id, answers, date_of_visit, telephone, is_processed, is_invalid, qg_type_id, raw_data, comments, user_id) FROM 'replacefilename' with csv NULL 'null';",
        'insertquery': "INSERT INTO replacetablename(id, session_id, school_id, answers, date_of_visit, telephone, is_processed, is_invalid, qg_type_id, raw_data, comments, user_id) select temp.id, temp.session_id, temp.school_id, temp.answers, temp.date_of_visit, temp.telephone, temp.is_processed, temp.is_invalid, temp.qg_type_id, temp.raw_data, temp.comments, temp.user_id FROM temp_replacetablename temp, users_user users where temp.user_id = users.id;"
    },
    {
        'name': 'ivrs_incomingnumber',
        'getquery': "\COPY (select id, number, qg_type_id, name from ivrs_incomingnumber) TO 'replacefilename' NULL 'null' DELIMITER ',' quote '\\\"' csv;",
        'insertquery': "\COPY replacetablename(id, number, qg_type_id, name) FROM 'replacefilename' with csv NULL 'null';"
    }
]


# Create directory and files
def init():
    if not os.path.exists(scriptdir+"/load"):
        os.makedirs(scriptdir+"/load")
    open(inputsqlfile, 'wb', 0)
    open(loadsqlfile, 'wb', 0)


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
        if 'insertquery' in table:
            command = 'echo "'+table['insertquery'].replace('replacetablename', table['name']).replace('replacefilename', filename)+'">>'+loadsqlfile
            system(command)


def get_data():
    system('psql -U klp -d '+fromdatabase+' -f '+inputsqlfile)


def load_data():
    system('psql -U klp -d '+todatabase+' -f '+loadsqlfile)


# order in which function should be called.
init()
create_sqlfiles()
get_data()
load_data()
