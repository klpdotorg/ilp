from os import system,sys
import os
import csv
import json
import datetime
import psycopg2

from optparse import make_option

if len(sys.argv) != 3:
    print("Please give database names as arguments. USAGE: " +
          "python import_communityfromcsv.py pathtofilesdir ilp")
    sys.exit()

fromdir = sys.argv[1]

todatabase = sys.argv[2]

basename = "communityfile"
inputsqlfile = basename+"_getdata.sql"
loadsqlfile = basename+"_loaddata.sql"



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
            return int(day) in range(1,32)
        except:
            return False

def is_month_correct(month):
        return int(month) in range(1,13)

def is_year_correct(year):
        return (len(year) == 4 and int(year))


num_to_user_type = {
    '1':'PR',
    '2':'SM',
    '3':'ER',
    '4':'CM',
    '5':'CM'
}

for filename in os.listdir(fromdir):
    if not filename.endswith(".csv"):
        continue
    print(filename)
    connectionstring = "dbname=%s user=klp" % todatabase
    conn = psycopg2.connect(connectionstring);
    cursor = conn.cursor()
    f = open(fromdir+"/"+filename, 'r')
    csv_f = csv.reader(f)

    missing_ids = {}
    missing_ids['schools'] = []
    count = 0

    previous_date = ""

    for row in csv_f:
        if count < 2 :
            count += 1
            continue

        name = row[7]
        school_id = row[6].strip()
        if school_id == '':
            print('School id is empty'+str(row))
            continue
        sqlselect = "select exists(select 1 from schools_institution where id=%s);"
        cursor.execute(sqlselect, [school_id])
        school_present = cursor.fetchall()[0][0]
        if not school_present:
            print('School id not present :'+school_id)
            continue
        accepted_answers = {'1':'Yes', '0':'No', '99':'Unknown', '88':'Unknown'}

        user_type = num_to_user_type[row[8]]
        day, month, year = row[26], row[27], row[28]
        previous_date = date_of_visit = parse_date(
                previous_date, day, month, year)


        question_sequence = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
                                 12, 13, 14, 15, 16, 17]
        answer_columns = [9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
                              19, 20, 21, 22, 23, 24, 25]

        at_least_one_answer = False
        for answer_column in answer_columns:
            if row[answer_column] in accepted_answers:
                at_least_one_answer = True
                break

        if at_least_one_answer:
            sqlinsert = "insert into assessments_answergroup_institution(institution_id,group_value,is_verified,questiongroup_id,date_of_visit,respondent_type_id,double_entry,status_id) values(%s, %s, %s, %s, %s, %s, %s, %s) returning id;"
            cursor.execute(sqlinsert, (school_id ,name, 'true', 7, date_of_visit, user_type,'0','IA'))
            group_id = cursor.fetchone()[0]

            for sequence_number, answer_column in zip(question_sequence, answer_columns):
                if row[answer_column] in accepted_answers:
                    sqlselect = "select distinct question_id from assessments_questiongroup_questions where questiongroup_id=7 and sequence=%s;"
                    cursor.execute(sqlselect, [sequence_number])
                    question_id = cursor.fetchall()[0]
                    #Create answer
                    sqlanswer = "insert into assessments_answerinstitution(answergroup_id, question_id, answer) values(%s, %s, %s)"
                    cursor.execute(sqlanswer, (group_id, question_id, row[answer_column]))
                    #answer = Answer.objects.get_or_create( story=story, question=question, text=accepted_answers[row[answer_column]],)
                else:
                    print("No accepted answers")
                    print(row)


    conn.commit()
    cursor.close()
    conn.close()
