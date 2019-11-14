import csv
import xlrd
import os
#from datetime import datetime
import datetime
from django.conf import settings
from pytz import timezone
from dateutil import parser
from django.core.management.base import BaseCommand
from assessments.models import (AnswerGroup_Institution, AnswerInstitution,
                                QuestionGroup_Questions, QuestionGroup)
from schools.models import Institution
from boundary.models import ElectionBoundary


class Command(BaseCommand):

    args = ""
    help = """python3 manage.py deletefudged [--filename=filename]"""
    cols = {"disecode":8,
            "qgname":9,
            "academicyear":0}

    qgid = {"2016-2017": {"Class 4 Assessment": 21,
                      "Class 5 Assessment": 22,
                      "Class 6 Assessment": 23},
            "2017-2018": {"Class 4 Assessment": 21,
                      "Class 5 Assessment": 22,
                      "Class 6 Assessment": 23},
            "2018-2019": {"Class 4 Assessment": 45,
                      "Class 5 Assessment": 46,
                      "Class 6 Assessment": 47}}

    def add_arguments(self, parser):
        parser.add_argument('--filename')

    def parseFile(self, csv_file):
        with open(csv_file, 'r+') as data_file:
            data = csv.reader(data_file,delimiter='|')
            header = 1
            anscount = 0
            ansgroupcount = 0
            for row in data:
                if header:
                    header = 0
                    continue
                disecode = row[self.cols["disecode"]]
                qgname = row[self.cols["qgname"]]
                acadyear = row[self.cols["academicyear"]]
                qgid = self.qgid[acadyear][qgname]
                startdate = datetime.date(int(acadyear[0:4]),6,1)
                enddate = datetime.date(int(acadyear[5:9]),4,30)

                answergroup = AnswerGroup_Institution.objects.filter(
                                questiongroup__id = qgid,
                                institution__dise__school_code=disecode,
                                date_of_visit__range=(startdate, enddate))
                if len(answergroup) > 0:
                    print(str(disecode)+", "+str(answergroup[0].institution_id)+", qgid:"+str(qgid)+", acadeyear: "+str(acadyear)+" :"+str(len(answergroup))+","+str(answergroup[0].questiongroup.id))
                    answergroup.delete()

    def handle(self, *args, **options):
        csv_file= options.get('filename', None)
        if csv_file == None:
            print("Pass the csv file --filename")
            return

        self.parseFile(csv_file)
