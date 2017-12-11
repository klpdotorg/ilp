from os import sys, system
import os, inspect


if len(sys.argv) != 3:
    print("Please give database names as arguments. USAGE: " +
          "python import_gka_basicinfo.py dubdubdub ilp")
    sys.exit()

fromdatabase = sys.argv[1]

todatabase = sys.argv[2]

basename = "gkabasic"
scriptdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
inputsqlfile = scriptdir+"/"+basename+"_getdata.sql"
loadsqlfile = scriptdir+"/"+basename+"_loaddata.sql"

tables = [
    {
        'name': 'assessments_survey',
        'insertquery': "insert into replacetablename(id, name,created_at,partner_id,status_id, admin0_id) values(3, 'Ganitha Kalika Andolana', '2016-05-19', 'akshara','AC', 2);"
    },
    {
        'name': 'assessments_questiongroup',
        'insertquery': "\COPY replacetablename(id,description, name, academic_year_id, start_date, end_date,status_id,double_entry, created_at, inst_type_id,survey_id, survey_on_id, type_id, source_id) FROM '"+scriptdir+"/EkStep_Concepts.csv' with csv NULL 'null';"
    },
    {
        'name': 'assessments_question',
        'getquery': "\COPY (select question_id, description, concept,true,3,'AC',1,1  from gka_concepts) TO 'replacefilename' NULL 'null' DELIMITER ',' quote '\\\"' csv;",
        'insertquery': "\COPY replacetablename(question_text,display_text,key,is_featured,question_type_id,status_id,max_score,pass_score) FROM 'replacefilename' with csv NULL 'null';"
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
