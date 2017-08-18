from os import system,sys
import os


if len(sys.argv) != 3:
    print("Please give database names as arguments. USAGE: python import_anganwadi_infra.py ang_infra ilp", file=sys.stderr)
    sys.exit()

#Before running this script
#change this to point to the ems database that is used for getting the data
fromdatabase = sys.argv[1]

#change this to ilp db to be populated with
todatabase = sys.argv[2]

basename = "anginfra"
dbs = []

tables=[
    {
        'name': 'temp_anginfra',
        'db': fromdatabase,
        'query': "COPY(select sid, ai_metric, perc_score, ai_group, value from tb_ang_infra_agg agg, tb_display_master master where agg.ai_metric=master.key) TO '$PWD/load/replacename.csv' NULL 'null' DELIMITER ',' quote '\\\"' csv;"
    },
    {
        'name': 'temp_anginfra',
        'db': todatabase,
        'query': 'CREATE TEMP TABLE replacetable(sid integer, ai_metric text, perc_score integer, ai_group text, description text);'
    },
    {
        'name': 'temp_anginfra',
        'db': todatabase,
        'query': "COPY replacetable(sid, ai_metric, perc_score, ai_group, description) from '$PWD/load/replacename.csv' with csv NULL 'null';"
    },
    {
        'name': 'assessments_survey',
        'db': todatabase,
        'query': "insert into replacetable(id, name,created_at,partner_id,status_id) values(1, 'Anganwadi Infrastructure', to_date('2014-02-03', 'YYYY-MM-DD'),'akshara','IA');"
    },
    {
        'name': 'assessments_questiongroup',
        'db': todatabase,
        'query': "insert into replacetable(id, name, start_date, end_date, double_entry, created_at, updated_at, academic_year_id, inst_type_id, status_id, survey_id, type_id) values(1,'Infrasturce Assessment',to_date('2014-02-03', 'YYYY-MM-DD'),to_date('2014-04-30', 'YYYY-MM-DD'), false, to_date('2014-02-03', 'YYYY-MM-DD'),to_date('2014-02-03', 'YYYY-MM-DD'),'1314','pre','IA',1,'monitor');"
    },
    {
        'name': 'assessments_question',
        'db': todatabase,
        'query': "ALTER SEQUENCE assessments_question_id_seq RESTART WITH 1; insert into replacetable(question_text, display_text, key, is_featured, status_id) select distinct  ai_metric, description, ai_group, true, 'IA' from temp_anginfra;"
    },
    {
        'name': 'assessments_questiongroupquestions',
        'db': todatabase,
        'query': "insert into replacetable(sequence, question_id, questiongroup_id) select row_number() over(), id, 1 from assessments_question;"
    },
    {
        'name': 'assessments_answerinstitution',
        'db': todatabase,
        'query': "insert into replacetable(answer, double_entry, date_of_visit, is_verified, entered_at, institution_id, question_id, questiongroup_id, status_id) select perc_score,0, to_date('2014-02-03', 'YYYY-MM-DD'), true, to_date('2014-02-03', 'YYYY-MM-DD'),sid, (select id from assessments_question where question_text=ai_metric),1, 'IA' from temp_anginfra, schools_institution s where temp_anginfra.sid=s.id;"
    }
]

#Create directory and files
def init():
    if not os.path.exists("load"):
    	os.makedirs("load")


def create_sql_files():
    #Loop through the tables
    for table in tables:
        if table["db"] not in dbs:
            dbs.append(table["db"])
            system('>'+table['db']+'_query.sql')
        filename=os.getcwd()+'/load/'+table['name']+'.csv'
        open(filename,'wb',0)
        os.chmod(filename,0o666)
        command='echo "'+table["query"].replace('replacetable',table["name"]).replace('replacename', table["name"])+'">>'+basename+'_'+table['db']+'_query.sql'
        #print(command)
        system(command)


def loaddata():
    for db in dbs:
        system('psql -U klp -d '+db+' -f '+db+'_query.sql')


#order in which function should be called.
init()
create_sql_files()
loaddata()
