import csv
import os
import json
from datetime import datetime
now = datetime.now()
from dateutil import parser
import sys
from django.core.management.base import BaseCommand, CommandError
import argparse
from django.conf import settings
from assessments.models import AnswerGroup_Institution, AnswerInstitution, QuestionGroup_Questions

class Command(BaseCommand):

    args = ""
    help = """python3 manage.py loadgpc [--filename=filename] [--grade=4] [--qgroup=47] """
    
    def add_arguments(self, parser):
        parser.add_argument('--filename')
        parser.add_argument('--grade')
        parser.add_argument('--qgroup')
        
    def handle(self, *args, **options):
        file_name = options.get('filename', None)
        grade = options.get('grade', None)
        qgroup= options.get('qgroup', None)
        csv_file = settings.PROJECT_ROOT + '/../'+ file_name

        with open(csv_file, 'r+') as data_file:
            data = csv.reader(data_file)
            header = 1
            for row in data:
                if header:
                    header = 0 
                else:
                    group_value = row[9]
                    ddmmyyyy = row[3]
                    parsed = datetime.strptime(ddmmyyyy, '%d/%m/%Y')
                    date_string = parsed.strftime('%Y-%m-%d')
                    dov = parser.parse(date_string)
                    inst_id = row[4]
                    entererd_at = now
                
                    answergroup = AnswerGroup_Institution.objects.create(
                                group_value = group_value,
                           	date_of_visit = dov,
                           	questiongroup_id = qgroup,
                       	        institution_id = inst_id,
                       	        status_id = 'AC',
                       	        is_verified = True)

                    question_id = QuestionGroup_Questions.objects.filter(questiongroup=qgroup,sequence=1).values('question_id')
                    answer = AnswerInstitution.objects.create(
                                answer = grade,
                                answergroup_id = answergroup.id,
                                question_id = question_id[0]['question_id'])
                
                    quescnt = QuestionGroup_Questions.objects.filter(questiongroup=qgroup).count()
                    anscnt = 9 #the answers to questions begin here

                    for i in range(quescnt-1):
                        anscnt += 1
                        seqcnt = i+2
                        question_id = QuestionGroup_Questions.objects.filter(questiongroup=qgroup,sequence=seqcnt).values('question_id')
                        answer = AnswerInstitution.objects.create(
                               answer = row[anscnt],
                               answergroup_id = answergroup.id,
                               question_id = question_id[0]['question_id'] )
