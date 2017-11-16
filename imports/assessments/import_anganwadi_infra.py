from os import system, sys
import os, inspect


if len(sys.argv) != 3:
    print("Please give database names as arguments. USAGE: python import_anganwadi_infra.py ang_infra ilp")
    sys.exit()

fromdatabase = sys.argv[1]

todatabase = sys.argv[2]

basename = "anginfra"
scriptdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
dbs = []

tables = [
    {
        'name': 'temp_anginfra',
        'db': fromdatabase,
        'query': "\COPY (select sid, ai_metric, perc_score, ai_group, value from tb_ang_infra_agg agg, tb_display_master master where agg.ai_metric=master.key) TO '"+scriptdir+"/load/replacename.csv' NULL 'null' DELIMITER ',' quote '\\\"' csv;"
    },
    {
        'name': 'temp_anginfra',
        'db': todatabase,
        'query': 'CREATE TEMP TABLE replacetable(sid integer, ai_metric text, perc_score integer, ai_group text, description text);'
    },
    {
        'name': 'temp_anginfra',
        'db': todatabase,
        'query': "\COPY replacetable(sid, ai_metric, perc_score, ai_group, description) from '"+scriptdir+"/load/replacename.csv' with csv NULL 'null';"
    },
    {
        'name': 'assessments_survey',
        'db': todatabase,
        'query': "insert into replacetable(id, name,created_at,partner_id,status_id, admin0_id) values(4, 'Anganwadi Infrastructure', to_date('2014-02-03', 'YYYY-MM-DD'),'akshara','IA', 2);"
    },
    {
        # Setting id as 30
        'name': 'assessments_questiongroup',
        'db': todatabase,
        'query': "insert into replacetable(id, name, start_date, end_date, double_entry, created_at, updated_at, academic_year_id, inst_type_id, status_id, survey_id, survey_on_id, type_id) values(30,'Infrasturce Assessment',to_date('2014-02-03', 'YYYY-MM-DD'),to_date('2014-04-30', 'YYYY-MM-DD'), false, to_date('2014-02-03', 'YYYY-MM-DD'),to_date('2014-02-03', 'YYYY-MM-DD'),'1314','pre','IA',4,'institution','monitor');"
    },
    {
        'name': 'assessments_question',
        'db': todatabase,
        'query': "insert into replacetable(question_text, display_text, key, is_featured, status_id) select distinct  ai_metric, description, ai_group, true, 'IA' from temp_anginfra;"
    },
    {
        'name': 'assessments_answergroup_institution',
        'db': todatabase,
        'query': "insert into replacetable(double_entry, date_of_visit, is_verified, entered_at, institution_id, questiongroup_id, status_id) select distinct 0, to_date('2014-02-03', 'YYYY-MM-DD'), true, to_date('2014-02-03', 'YYYY-MM-DD'),sid, 30, 'IA' from temp_anginfra, schools_institution s where temp_anginfra.sid=s.id;"
    },
    {
        'name': 'assessments_answerinstitution',
        'db': todatabase,
        'query': "insert into replacetable(answergroup_id, answer, question_id) select answergroup.id, perc_score,(select id from assessments_question where question_text=ai_metric) from temp_anginfra, schools_institution s, assessments_answergroup_institution answergroup where temp_anginfra.sid=s.id and temp_anginfra.sid=answergroup.institution_id;"
    },
    {
        'name': 'assessments_questiongroup_questions',
        'db': todatabase,
        'query': "insert into replacetable(question_id, questiongroup_id) select distinct ans.question_id,30 from assessments_answerinstitution ans, assessments_answergroup_institution ansgroup where ans.answergroup_id=ansgroup.id and ansgroup.questiongroup_id=30;"
    }
]


# Create directory and files
def init():
    if not os.path.exists(scriptdir+"/load"):
        os.makedirs(scriptdir+"/load")


def create_sql_files():
    # Loop through the tables
    for table in tables:
        if table["db"] not in dbs:
            dbs.append(table["db"])
            system('>'+basename+'_'+table['db']+'_query.sql')
        filename = scriptdir+'/load/'+table['name']+'.csv'
        open(filename, 'wb', 0)
        os.chmod(filename, 0o666)
        command = 'echo "'+table["query"].replace('replacetable', table["name"]).replace('replacename', table["name"])+'">>'+basename+'_'+table['db']+'_query.sql'
        system(command)


def loaddata():
    for db in dbs:
        system('psql -U klp -d '+db+' -f '+basename+'_'+db+'_query.sql')


# order in which function should be called.
init()
create_sql_files()
loaddata()
