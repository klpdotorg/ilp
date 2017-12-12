from os import sys, system
import os
import inspect


if len(sys.argv) != 3:
    print("Please give database names as arguments. USAGE: " +
          "python import_community.py dubdubdub ilp")
    sys.exit()

fromdatabase = sys.argv[1]

todatabase = sys.argv[2]

basename = "community"
scriptdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
inputsqlfile = scriptdir+"/"+basename+"_getdata.sql"
loadsqlfile = scriptdir+"/"+basename+"_loaddata.sql"

tables = [
    {
        'name': 'assessments_survey',
        'insertquery': "insert into replacetablename(id, name,created_at,partner_id,status_id, admin0_id) values(1, 'Community', to_date('2014-02-03', 'YYYY-MM-DD'),'akshara','AC', 2);"
    },
    {
        'name': 'assessments_questiongroup',
        'getquery': "\COPY (select id, case id when 4 then 'Community(2014-2015)' when 7 then 'Community(2015-2016)' end, case id when 4 then to_date('2014-06-01', 'YYYY-MM-DD') when 7 then start_date end , version, 0, case id when 4 then to_date('2014-06-01', 'YYYY-MM-DD') when 7 then start_date end, case id when 7 then 'both' else 'primary' end, case(status) when 2 then 'AC' when 1 then 'IA' else 'IA' end,    source_id, 1, 'institution', 'monitor', 'name' from stories_questiongroup where id in (4,7)) TO 'replacefilename' NULL 'null' DELIMITER ',' quote '\\\"' csv;",
        'insertquery': "\COPY replacetablename(id, name, start_date, version, double_entry, created_at, inst_type_id, status_id, source_id,survey_id, survey_on_id, type_id, group_text) FROM 'replacefilename' with csv NULL 'null';"
    },
    {
        'name': 'assessments_question',
        'getquery': "\COPY (select distinct id, text, display_text, key, options, is_featured, question_type_id,case(is_active) when 't' then 'AC' when 'f' then 'IA' end from stories_question where id in (select question_id from stories_questiongroup_questions where questiongroup_id in (4,7))) TO 'replacefilename' NULL 'null' DELIMITER ',' quote '\\\"' csv;",
        'tempquery': "CREATE TEMP TABLE temp_replacetablename(id integer, text text, display_text text, key text, options text, is_featured boolean, question_type_id integer, status text ); \COPY temp_replacetablename(id, text, display_text, key, options, is_featured, question_type_id,status) FROM 'replacefilename' with csv NULL 'null';",
        'insertquery': "INSERT INTO replacetablename(id, question_text, display_text, key, options, is_featured, question_type_id, status_id) select temp.id, temp.text, temp.display_text, temp.key, temp.options, temp.is_featured, temp.question_type_id, temp.status from temp_replacetablename temp where temp.id not in (select id from replacetablename);"
    },
    {
        'name': 'assessments_questiongroup_questions',
        'getquery': "\COPY (select questiongroup_id, question_id, sequence from stories_questiongroup_questions where questiongroup_id in (4,7)) TO 'replacefilename' NULL 'null' DELIMITER ',' quote '\\\"' csv;",
        'insertquery': "\COPY replacetablename(questiongroup_id, question_id, sequence) FROM 'replacefilename' with csv NULL 'null';"
    },
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
