import csv
import os
import json
from datetime import datetime
from django.conf import settings
from pytz import timezone
from dateutil import parser
import sys
from django.core.management.base import BaseCommand, CommandError
import argparse
from django.conf import settings
from assessments.models import AnswerGroup_Institution, AnswerInstitution, QuestionGroup_Questions, QuestionGroup
from schools.models import Institution
from boundary.models import Boundary, ElectionBoundary

class Command(BaseCommand):

    args = ""
    help = """python3 manage.py loadgpc [--filename=filename] [--grade=4] [--qgroup=47] """
    gender_qid = 291 
    grade_qid = 130
    q_seq_start = 3
    q_seq_end = 22
    validanswers = {"0", "1"}
    validgenders = {"male", "female"}
    rowcounter = 0
    
    def add_arguments(self, parser):
        parser.add_argument('--filename')
        parser.add_argument('--grade')
        parser.add_argument('--qgroup')


    def checkQuestionGroupValidity(self, qgroup):
        try:
            QuestionGroup.objects.get(id=qgroup)
            return True 
        except QuestionGroup.DoesNotExist:
            print("Invalid questiongroup id passed: "+qgroup)
            return False 

    def checkGPValidity(self, gpid, gpname):
        try:
            gp = ElectionBoundary.objects.get(id=gpid, const_ward_name=gpname,const_ward_type='GP')
            return True 
        except ElectionBoundary.DoesNotExist:
            print("["+str(self.rowcounter)+"] No valid GP found: "+str(gpid)+", "+gpname)
            return False 

    def checkInstitutionValidity(self, inst_id, schoolname, dise_code, gpid, district, block):
        try:
            inst = Institution.objects.filter(id=inst_id).values("name", "dise__school_code", "gp", "admin1__name", "admin2__name")
        except Institution.DoesNotExist:
            print("["+str(self.rowcounter)+"] Institution does not exist for id: "+str(inst_id))
            return False 
        if inst[0]["name"] != schoolname:
            print("["+str(self.rowcounter)+"] Institution id and name does not match  for id: "+str(inst_id)+" , name: "+schoolname)
            return False 
        if str(inst[0]["dise__school_code"]) != str(dise_code):
            print("["+str(self.rowcounter)+"] Institution id ("+str(inst_id)+") disecode :"+str(inst[0]["dise__school_code"])+" does not match disecode in the row :"+str(dise_code))
            return False 
        if str(inst[0]["gp"]) != str(gpid):
            print("["+str(self.rowcounter)+"] Institution id and gpid does not match  for id: "+str(inst_id)+" , gpid: "+str(gpid))
            return False 
        if str(inst[0]["admin1__name"]) != str(district):
            print("["+str(self.rowcounter)+"] Institution id ("+str(inst_id)+") district :"+str(inst[0]["admin1__name"])+" does not match district in the row :"+str(district))
            return False 
        if str(inst[0]["admin2__name"]) != str(block):
            print("["+str(self.rowcounter)+"] Institution id ("+str(inst_id)+") block :"+str(inst[0]["admin2__name"])+" does not match block in the row :"+str(block))
            return False 
        return True 

    def checkGradeValidity(self, passedgrade, csvgrade, qgroup):
        if passedgrade != csvgrade:
            print("["+str(self.rowcounter)+"] Grade in csv: "+csvgrade+" does not match grade argument passed: "+passedgrade) 
            return False 
        questiongroup = QuestionGroup.objects.get(id=qgroup)
        if passedgrade not in questiongroup.name:
            print("["+str(self.rowcounter)+"] Passed grade: "+passedgrade+" not associated with passed questiongroup: "+qgroup+"("+questiongroup.name+")")
            return False 
        return True 

    def checkGenderValidity(self, gender):
        if gender not in self.validgenders:
            print("["+str(self.rowcounter)+"] Invalid gender :"+gender+", it should have been: "+str(self.validgenders))
            return False 
        return True 

    def checkAnswerValidity(self, answer):
        if answer not in self.validanswers:
            print("["+str(self.rowcounter)+"] Incorrect answer type :"+answer+", it should have been in range: "+str(self.validanswers))
            return False 
        return True 

    def handle(self, *args, **options):
        csv_file = options.get('filename', None)
        grade = options.get('grade', None)
        qgroup= options.get('qgroup', None)

        with open(csv_file, 'r+') as data_file:
            data = csv.reader(data_file)
            header = 1
            for row in data:
                if header:
                    header = 0 
                    continue

                self.rowcounter += 1
                csv_grade = row[0].strip()
                district = row[1].strip().lower()
                block = row[2].strip().lower()
                ddmmyyyy = row[3]
                try:
                    parsed = datetime.strptime(ddmmyyyy, '%d/%m/%Y')
                except ValueError:
                    print("["+str(self.rowcounter)+"] Incorrect data format, should be DD/MM/YYYY")
                    continue
                date_string = parsed.strftime('%Y-%m-%d')
                dov = parser.parse(date_string)
                localtz = timezone(settings.TIME_ZONE)
                dov = localtz.localize(dov)
                inst_id = row[4].strip()
                dise_code = row[5].strip()
                schoolname = row[6].strip()
                gpid = row[7].strip()
                gpname = row[8].strip()
                group_value = row[10].strip()
                gender = row[11].strip().lower()
                enteredat = localtz.localize(datetime.now())

                #check values  
                if not self.checkQuestionGroupValidity(qgroup):
                    continue

                if not self.checkGradeValidity(grade, csv_grade, qgroup):
                    continue

                if not self.checkGPValidity(gpid, gpname):
                    continue

                if not self.checkInstitutionValidity(inst_id, schoolname, dise_code, gpid, district, block):
                    continue

                if not self.checkGenderValidity(gender):
                    continue

                answergroup = AnswerGroup_Institution.objects.create(
                                group_value = group_value,
                           	date_of_visit = dov,
                           	questiongroup_id = qgroup,
                       	        institution_id = inst_id,
                                entered_at = enteredat,
                       	        status_id = 'AC',
                       	        is_verified = True)

                answer = AnswerInstitution.objects.create(
                                answer = grade,
                                answergroup_id = answergroup.id,
                                question_id = self.grade_qid)
                
                answer = AnswerInstitution.objects.create(
                                answer = gender,
                                answergroup_id = answergroup.id,
                                question_id = self.gender_qid)


                ans_col_cnt = 12 #the answers to questions begin here

                for seq in range(self.q_seq_start, self.q_seq_end):
                    if not self.checkAnswerValidity(row[ans_col_cnt]):
                        ans_col_cnt += 1
                        continue
                    qgq = QuestionGroup_Questions.objects.get(questiongroup=qgroup,sequence=seq)
                    answer = AnswerInstitution.objects.create(
                                        answer = row[ans_col_cnt],
                                        answergroup_id = answergroup.id,
                                        question_id = qgq.question_id)
                    ans_col_cnt += 1
