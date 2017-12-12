from os import sys
import os
import inspect
import csv
import datetime
import psycopg2
import re


if len(sys.argv) != 3:
    print("Please give directory and database names as arguments. USAGE: " +
          "python import_communityfromcsv14_15.py pathtofilesdir ilp")
    sys.exit()

fromdir = sys.argv[1]

todatabase = sys.argv[2]

basename = "community14_15"
scriptdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
inputsqlfile = scriptdir+"/"+basename+"_getdata.sql"
loadsqlfile = scriptdir+"/"+basename+"_loaddata.sql"


def parse_date(previous_date,  day, month, year):
        date = day + "/" + month + "/" + year
        if date:
            date, date_is_sane = check_date_sanity(date)
            if date_is_sane:
                date_of_visit = datetime.datetime.strptime(
                    date, '%d/%m/%Y'
                )
                return date_of_visit

        return previous_date


def check_date_sanity(date):
        months = {
            'june': '6',
            'july': '7',
        }

        day = date.split("/")[0]
        month = date.split("/")[1]
        year = date.split("/")[2]

        if month.strip().lower() in months:
            month = months[month.strip().lower()]
            date = day + "/" + month + "/" + year

        if not is_day_correct(day):
            return (date, False)

        if not is_month_correct(month):
            return (date, False)

        if not is_year_correct(year):
            return (date, False)

        return (date, True)


def is_day_correct(day):
        try:
            return int(day) in range(1, 32)
        except:
            return False


def is_month_correct(month):
        return int(month) in range(1, 13)


def is_year_correct(year):
        return (len(year) == 4 and int(year))


user_to_user_type = {
    'parent': 'PR',
    'parents': 'PR',
    'sdmc': 'SM',
    'sdmc-1': 'SM',
    'sdmc-2': 'SM',
    'elected/localleader': 'ER',
    'elected-localleader': 'ER',
    'electedlocalleader': 'ER',
    'localleader': 'ER',
    'educated/localleader': 'ER',
    'cbomember': 'CM',
    'educatedyouth': 'EY',
    'na': 'PR'
}

connectionstring = "dbname=%s user=klp" % todatabase


def reset_sequences():
    conn = psycopg2.connect(connectionstring)
    cursor = conn.cursor()
    query = "SELECT setval('assessments_questiongroup_id_seq', COALESCE((SELECT MAX(id)+1 FROM assessments_questiongroup), 1), false); SELECT setval('assessments_question_id_seq', COALESCE((SELECT MAX(id)+1 FROM assessments_question), 1), false); SELECT setval('assessments_answergroup_institution_id_seq', COALESCE((SELECT MAX(id)+1 FROM assessments_answergroup_institution), 1), false); SELECT setval('assessments_answerinstitution_id_seq', COALESCE((SELECT MAX(id)+1 FROM assessments_answerinstitution), 1), false);"
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()


for filename in os.listdir(fromdir):
    if not filename.endswith(".csv"):
        continue
    print(filename)
    conn = psycopg2.connect(connectionstring)
    cursor = conn.cursor()
    f = open(fromdir+"/"+filename, 'r')
    csv_f = csv.reader(f)

    missing_ids = {}
    missing_ids['schools'] = []
    count = 0

    # reset sequences
    reset_sequences()

    for row in csv_f:
        if count < 1:
            count += 1
            continue

        name = row[8]
        school_id = row[4].strip()
        if school_id == '':
            print('School id is empty'+str(row))
            continue
        sqlselect = "select exists(select 1 from schools_institution where id=%s);"
        cursor.execute(sqlselect, [school_id])
        school_present = cursor.fetchall()[0][0]
        if not school_present:
            print('School id not present :'+school_id)
            continue
        accepted_answers = {'Yes': 'Yes', 'No': 'No'}

        user_type = user_to_user_type[row[7].strip().lower().replace(' ', '')]
        date = row[6]
        if date == 'NA':
            date = '01/04/2015'
        if re.match('^.*/14$', date):
            date = re.sub('14', '2014', date)
        if re.match('^.*/15$', date):
            date = re.sub('15', '2015', date)
        date_of_visit = datetime.datetime.strptime(date, '%d/%m/%Y')

        question_sequence = [1, 2, 3, 4, 5, 6, 7, 8]
        answer_columns = [9, 10, 11, 12, 13, 14, 15, 16]

        at_least_one_answer = False
        for answer_column in answer_columns:
            if row[answer_column].strip() in accepted_answers:
                at_least_one_answer = True

        if at_least_one_answer:
            sqlinsert = "insert into assessments_answergroup_institution(institution_id,group_value,is_verified,questiongroup_id,date_of_visit,respondent_type_id,status_id) values(%s, %s, %s, %s, %s, %s, %s) returning id;"
            cursor.execute(sqlinsert, (school_id, name, 'true', 4,
                                       date_of_visit, user_type, 'AC'))
            group_id = cursor.fetchone()[0]

            for sequence_number, answer_column in zip(question_sequence,
                                                      answer_columns):
                answer = row[answer_column].strip()
                if answer in accepted_answers:
                    sqlselect = "select distinct question_id from assessments_questiongroup_questions where questiongroup_id=4 and sequence=%s;"
                    cursor.execute(sqlselect, [sequence_number])
                    question_id = cursor.fetchall()[0]
                    # Create answer
                    sqlanswer = "insert into assessments_answerinstitution(answergroup_id, question_id, answer) values(%s, %s, %s)"
                    cursor.execute(sqlanswer, (group_id, question_id,
                                               answer))

    conn.commit()
    cursor.close()
    conn.close()
