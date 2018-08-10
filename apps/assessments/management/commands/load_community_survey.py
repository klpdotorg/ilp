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
    help = """python3 manage.py load_community_survey --filepath=filepath"""
    
    def add_arguments(self, parser):
        parser.add_argument('--filepath')
   
    def handle(self, *args, **options):
        file_path = options.get('filepath', None)
        csv_file = settings.PROJECT_ROOT + '/../'+ file_path
         

        with open(csv_file, 'r+') as data_file:
            data = csv.reader(data_file)
            header = 1
            for row in data:
                if header:
                    header = 0 
                else:
                    group_value = row[9]
                    date = row[21]
                    month = row[22]
                    year = row[23]
                    ddmmyyyy = date + "/"+ month + "/"+ year
                    parsed = datetime.strptime(ddmmyyyy, '%d/%m/%Y')
                    date_string = parsed.strftime('%Y-%m-%d')
                    dov = parser.parse(date_string)
                    inst_id = row[3]
                    entererd_at = now
                
                    answergroup = AnswerGroup_Institution.objects.create(
                            group_value = group_value,
                       	    date_of_visit = dov,
                       	    questiongroup_id = 20,
                       	    institution_id = inst_id,
                       	    status_id = 'AC',
                       	    is_verified = True)
 
                    quescnt = QuestionGroup_Questions.objects.filter(questiongroup=20).count()
                    anscnt = 9
                    answers_accepted = {'1':'Yes','0':'No','99':'Unknown','88':'Unknown'}
                    for i in range(quescnt):
                        anscnt += 1
                        seqcnt = i+1
                        question_id = QuestionGroup_Questions.objects.filter(questiongroup=20,sequence=seqcnt).values('question_id')
                        ans = row[anscnt]
                        answer = answers_accepted[ans]
                        answer = AnswerInstitution.objects.create(
                               answer = answer,
                               answergroup_id = answergroup.id,
                               question_id = question_id[0]['question_id'] )                
