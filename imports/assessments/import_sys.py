from os import system, sys
import os
import inspect


if len(sys.argv) != 3:
    print("Please give database names as arguments. USAGE: " +
          "python import_sys.py dubdubdub ilp")
    sys.exit()

fromdatabase = sys.argv[1]

todatabase = sys.argv[2]

basename = "sys"
scriptdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
inputsqlfile = scriptdir+"/"+basename+"_getdata.sql"
loadsqlfile = scriptdir+"/"+basename+"_loaddata.sql"

tables = [
    {
        'name': 'assessments_survey',
        'insertquery': "insert into replacetablename(id, name,created_at,partner_id,status_id, admin0_id) values(5, 'SYS', to_date('2016-05-19', 'YYYY-MM-DD'),'akshara','AC', 2);"
    },
    {
        'name': 'assessments_questiongroup',
        'getquery': "\COPY (select id, 'SYS', to_date('2014-05-13', 'YYYY-MM-DD'), version, 0, to_date('2014-05-13', 'YYYY-MM-DD'), case(school_type_id) when 1 then 'primary' when 2 then 'pre' else 'both' end, case(status) when 2 then 'AC' when 1 then 'IA' else 'AC' end,    source_id, 5, 'institution', 'perception', 'name' from stories_questiongroup where id in (1,6)) TO 'replacefilename' NULL 'null' DELIMITER ',' quote '\\\"' csv;",
        'insertquery': "\COPY replacetablename(id, name, start_date, version, double_entry, created_at, inst_type_id, status_id, source_id,survey_id, survey_on_id, type_id, group_text) FROM 'replacefilename' with csv NULL 'null';"
    },
    {
        'name': 'assessments_question',
        'getquery': "\COPY (select distinct id, text, display_text, key, options, is_featured, question_type_id,case(is_active) when 't' then 'AC' when 'f' then 'IA' end from stories_question where id in (select question_id from stories_questiongroup_questions where questiongroup_id in (1,6))) TO 'replacefilename' NULL 'null' DELIMITER ',' quote '\\\"' csv;",
        'tempquery': "CREATE TEMP TABLE temp_replacetablename(id integer,question_text text, display_text text, key text, options text, is_featured boolean, question_type_id integer,status_id text); \COPY temp_replacetablename(id,question_text, display_text, key, options, is_featured,question_type_id,status_id) FROM 'replacefilename' with csv NULL 'null';",
        'insertquery': 'INSERT INTO replacetablename(id, question_text, display_text, key, options, is_featured, question_type_id,status_id) select id,  question_text, display_text, key, options, is_featured, question_type_id,status_id from temp_replacetablename where id not in (select id from replacetablename); INSERT INTO replacetablename(id, question_text, display_text, key, options, is_featured, question_type_id,status_id) values(141,\'Was the school open?\',\'Was the school open?\',\'webs-school-open\',\'{"Yes", "No", "Unknown"}\' ,false,1,\'AC\');'
    },
    {
        'name': 'assessments_questiongroup_questions',
        'getquery': "\COPY (select questiongroup_id, question_id, sequence from stories_questiongroup_questions where questiongroup_id in (1,6)) TO 'replacefilename' NULL 'null' DELIMITER ',' quote '\\\"' csv;",
        'insertquery': "\COPY replacetablename(questiongroup_id, question_id, sequence) FROM 'replacefilename' with csv NULL 'null';INSERT INTO replacetablename(questiongroup_id, question_id) values(6,141);"
    },
    {
        'name': 'assessments_answergroup_institution',
        'getquery': "\COPY (select distinct stories.id, stories.date_of_visit, stories.comments, stories.is_verified, stories.sysid, stories.entered_timestamp, stories.school_id, stories.group_id, 'AC', usertype.name, stories.name from stories_story stories left outer join stories_usertype usertype on (stories.user_type_id = usertype.id), stories_questiongroup qg where stories.group_id in (1,6)) TO 'replacefilename' NULL 'null' DELIMITER ',' quote '\\\"' csv;",
        'tempquery': "CREATE TEMP TABLE temp_replacetablename(id integer, date_of_visit timestamp, comments text, is_verified boolean, sysid integer, entered_at timestamp, school_id integer, questiongroup_id integer, status_id text, user_type_id text, group_value text); \COPY temp_replacetablename(id, date_of_visit, comments, is_verified, sysid, entered_at, school_id,questiongroup_id, status_id, user_type_id, group_value) FROM 'replacefilename' with csv NULL 'null';",
        'insertquery': "INSERT INTO replacetablename(id, group_value, date_of_visit, comments, is_verified, sysid, entered_at, institution_id, questiongroup_id, status_id, respondent_type_id) select temp.id, temp.group_value, temp.date_of_visit, temp.comments, temp.is_verified, temp.sysid, temp.entered_at, temp.school_id, temp.questiongroup_id, temp.status_id,temp.user_type_id from temp_replacetablename temp, schools_institution s where temp.school_id=s.id;"
    },
    {
        'name': 'assessments_answerinstitution',
        'getquery': "\COPY (select story_id, question_id, text from stories_answer answer, stories_story stories where answer.story_id=stories.id and stories.group_id in (1,6)) TO 'replacefilename' NULL 'null' DELIMITER ',' quote '\\\"' csv;",
        'tempquery': "CREATE TEMP TABLE temp_replacetablename(story_id integer, question_id integer, answer text); \COPY temp_replacetablename(story_id, question_id, answer) FROM 'replacefilename' with csv NULL 'null';",
        'insertquery': "INSERT INTO replacetablename(answergroup_id, question_id, answer) select temp.story_id, temp.question_id, temp.answer from temp_replacetablename temp, assessments_answergroup_institution answergroup where temp.story_id=answergroup.id;"
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
