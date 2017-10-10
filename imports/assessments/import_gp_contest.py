from os import system, sys
import os


if len(sys.argv) != 3:
    print("Please give database names as arguments. USAGE:" +
          "python import_gp_contest.py dubdubdub ilp")
    sys.exit()

fromdatabase = sys.argv[1]

todatabase = sys.argv[2]

basename = "gpcontest"
inputsqlfile = basename+"_getdata.sql"
loadsqlfile = basename+"_loaddata.sql"

tables = [
    {
        'name': 'assessments_survey',
        'getquery': "COPY(select id, name, created_at, updated_at, name, 'akshara', 'IA' from stories_survey where id=2) TO 'replacefilename' NULL 'null' DELIMITER ',' quote '\\\"' csv;",
        'insertquery': "COPY replacetablename(id, name, created_at, updated_at, description, partner_id, status_id) FROM 'replacefilename' with csv NULL 'null';"
    },
    {
        'name': 'assessments_questiongroup',
        'insertquery': "insert into replacetablename(id, name, start_date, double_entry, created_at, updated_at, academic_year_id, inst_type_id, status_id, survey_id, survey_on_id, type_id, group_text) values(21,'Class 4 Assessment',to_date('2016-12-01', 'YYYY-MM-DD'),false, to_date('2017-04-28', 'YYYY-MM-DD'),to_date('2017-04-28', 'YYYY-MM-DD'),'1617','primary','IA',2,'institution','monitor', 'child_name'), (22,'Class 5 Assessment',to_date('2016-12-01', 'YYYY-MM-DD'),false, to_date('2017-04-28','YYYY-MM-DD'),to_date('2017-04-28','YYYY-MM-DD'),'1617','primary','IA',2,'institution','monitor', 'child_name'),(23,'Class 6 Assessment',to_date('2016-12-01','YYYY-MM-DD'),false, to_date('2017-04-28','YYYY-MM-DD'),to_date('2017-04-28','YYYY-MM-DD'),'1617','primary','IA',2,'institution','monitor', 'child_name');"
    },
    {
        'name': 'assessments_question',
        'getquery': "COPY(select distinct id, text, display_text, key, options, is_featured, question_type_id,'IA' from stories_question where id in (select question_id from stories_questiongroup_questions where questiongroup_id in (select id from stories_questiongroup where survey_id =2))) TO 'replacefilename' NULL 'null' DELIMITER ',' quote '\\\"' csv;",
        'insertquery': "COPY replacetablename(id, question_text, display_text, key, options, is_featured, question_type_id,status_id) FROM 'replacefilename' with csv NULL 'null';"
    },
    {
        'name': 'assessments_questiongroup_questions',
        'getquery': "COPY(select distinct questiongroup_id, question_id, sequence from stories_questiongroup_questions where questiongroup_id in (select id from stories_questiongroup where survey_id =2)) TO 'replacefilename' NULL 'null' DELIMITER ',' quote '\\\"' csv;",
        'insertquery': "COPY replacetablename(questiongroup_id, question_id, sequence) FROM 'replacefilename' with csv NULL 'null';"
    },
    {
        'name': 'assessments_answergroup_institution',
        'getquery': "COPY(select distinct stories.id, 0, stories.date_of_visit,stories.is_verified,stories.entered_timestamp, stories.group_id, 'IA', stories.school_id, stories.name from stories_story stories,tb_school s where stories.group_id in (select id from stories_questiongroup where survey_id =2) and stories.school_id=s.id) TO 'replacefilename' NULL 'null' DELIMITER ',' quote '\\\"' csv;",
        'tempquery': "CREATE TEMP TABLE temp_replacetablename(id integer, double_entry integer, date_of_visit timestamp, is_verified boolean, entered_at timestamp, questiongroup_id integer, status_id text, institution_id integer, group_value text); COPY temp_replacetablename(id, double_entry, date_of_visit, is_verified, entered_at,questiongroup_id, status_id, institution_id, group_value) FROM 'replacefilename' with csv NULL 'null';",
        'insertquery': "INSERT INTO replacetablename(id, group_value, double_entry, date_of_visit, is_verified, institution_id, questiongroup_id, status_id,entered_at, respondent_type_id) select temp.id, temp.group_value, temp.double_entry, temp.date_of_visit, temp.is_verified, temp.institution_id, temp.questiongroup_id, temp.status_id,temp.entered_at,'CH' from temp_replacetablename temp, schools_institution s where institution_id=s.id;"
    },
    {
        'name': 'assessments_answerinstitution',
        'getquery': "COPY(select story_id, question_id, text from stories_answer answer, stories_story stories where answer.story_id=stories.id and stories.group_id in (select id from stories_questiongroup where survey_id =2)) TO 'replacefilename' NULL 'null' DELIMITER ',' quote '\\\"' csv;",
        'tempquery': "CREATE TEMP TABLE temp_replacetablename(story_id integer, question_id integer, answer text); COPY temp_replacetablename(story_id, question_id, answer) FROM 'replacefilename' with csv NULL 'null';",
        'insertquery': "INSERT INTO replacetablename(answergroup_id, question_id, answer) select temp.story_id, temp.question_id, temp.answer from temp_replacetablename temp, assessments_answergroup_institution answergroup where temp.story_id=answergroup.id;"
    }
]


# Create directory and files
def init():
    if not os.path.exists("load"):
        os.makedirs("load")
    open(inputsqlfile, 'wb', 0)
    open(loadsqlfile, 'wb', 0)


def create_sqlfiles():
    # Loop through the tables
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
