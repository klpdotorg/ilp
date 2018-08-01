import csv
import os
import json
from datetime import datetime
now = datetime.datetime.now()
import sys
from django.core.management.base import BaseCommand, CommandError
import argparse
from django.conf import settings
from assessments.models import AnswerGroup_Institution, AnswerInstitution


class Command(BaseCommand):

    args = ""
    help = """python3 manage.py loadgpc [--filename=gp_raw.csv] [--grade=4] [--questionfile=gp_ques_map_4.json]"""
    
    def add_arguments(self, parser):
        parser.add_argument('--filename')
        parser.add_argument('--grade')
        parser.add_argument('--questionfile')

    def handle(self, *args, **options):
        file_name = options.get('filename', None)
        grade = options.get('grade', None)
        questionfile = options.get('questionfile', None)
        csv_file = settings.PROJECT_ROOT + '/../apps/assessments/management/commands/csv/' + file_name
        question_file = settings.PROJECT_ROOT + '/../apps/assessments/management/commands/csv/' + questionfile

        with open(csv_file, 'r+') as data_file:
            data = csv.reader(data_file)
            for row in data:
                group_value = row[9]
                ddmmyyyy = row[3]
                dov = datetime.datetime.strptime(ddmmyyyy, "%Y-%m-%d")
                inst_id = row[4]
                entererd_at = now
                json_data = open(question_file)   
                ques_data = json.load(json_data)
                for data in range(len(ques_data)):
                    print(data)
                    if ques_data[data]["class"] == grade:
                        answergroup = AnswerGroup_Institution.objects.create(
                        	 group_value = group_value,
                        	 date_of_visit = dov,
                        	 questiongroup_id = ques_data[data]["question_group"],
                        	 institution_id = inst_id,
                        	 status_id = 'AC',
                        	 is_verified = True)

                        answer = AnswerInstitution.objects.create(
                            	answer = ques_data[data]["class"],
                                answergroup_id = answergroup.id,
                                question_id = 130)

                        anscnt = 9 #the answers to questions begin here
                        for i in range(len(ques_data[data]["questions"])-1):
                            anscnt += 1 
                            answer = AnswerInstitution.objects.create(
                            	answer = row[anscnt],
                            	answergroup_id = answergroup.id,
                            	question_id = ques_data[data]["questions"][i+1])
