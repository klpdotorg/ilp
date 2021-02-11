import csv
import xlrd
import os
import re
from datetime import datetime
from django.conf import settings
from pytz import timezone
from dateutil import parser
from django.core.management.base import BaseCommand
from assessments.models import (AnswerGroup_Student, AnswerStudent,
                                QuestionGroup_Questions, QuestionGroup)
from schools.models import Institution
from schools.models import Student, StudentStudentGroupRelation, StudentGroup
from boundary.models import ElectionBoundary
from common.models import Language, Gender

class Command(BaseCommand):

    args = ""
    help = """python3 manage.py loadgpc [--filename=filename] [--grade=4] [--qgroup=47]"""
    gender_qid = 291
    grade_qid = 130
    cols = {"grade":1, "district":2, "block":3, "ddmmyyyy":5,"instid":6,
            "disecode":7, "gpid":9, "gpname":10, 
            "childname": 11, "gender":12, "volunteername":31,
            "father_name": 13, "mother_name":14}
    q_seq_start = 3
    q_seq_end = 17
    ans_col_start = 15
    validanswers = {"0", "1"}
    validgenders = {"male", "female", "unknown"}
    rowcounter = 0
    gplist = {}
    datainserted = {}
    districtgpmap = {}
    onlycheck = False

    def add_arguments(self, parser):
        parser.add_argument('--filename')
        parser.add_argument('--grade')
        parser.add_argument('--qgroup')
        parser.add_argument('--onlycheck')

    def checkDistrictGPMapValidity(self, gpid, district):
        if gpid in self.districtgpmap:
            if district not in self.districtgpmap[gpid]:
                print("["+str(self.rowcounter)+"] Invalid District GP mapping for district: "+str(district)+"! Another district "+str(self.districtgpmap[gpid])+" is already associated with this GPID "+str(gpid))
                return False
        else:
            self.districtgpmap[gpid]=district
        return True


    def checkDoVValidity(self, gpid, dov):
        if gpid in self.gplist:
            if dov != self.gplist[gpid]["date"]:
                print("["+str(self.rowcounter) +
                      "] Multiple dates associated with same gpid: " +
                      str(gpid)+"; "+str(self.gplist[gpid]["date"]) +
                      ","+str(dov))
                return False
        else:
            self.gplist[gpid] = {"date": dov}
        return True


    def checkQuestionGroupValidity(self, qgroup):
        try:
            QuestionGroup.objects.get(id=qgroup)
            return True
        except QuestionGroup.DoesNotExist:
            print("Invalid questiongroup id passed: "+qgroup)
            return False

    def checkGPValidity(self, gpid, gpname):
        try:
            ElectionBoundary.objects.get(id=gpid,
                                         const_ward_name__istartswith=gpname,
                                         const_ward_type='GP')
            return True
        except ElectionBoundary.DoesNotExist:
            print("["+str(self.rowcounter)+"] No valid GP found for id :"
                  + str(gpid)+", and name :"+gpname)
            return False

    def checkInstitutionValidity(self, inst_id, dise_code, gpid,
                                 district, block):
        try:
            inst = Institution.objects.get(id=inst_id, dise_id__school_code=dise_code,gp_id=gpid, admin1_id__name=district, admin2_id__name=block)
        except Institution.DoesNotExist:
            print("["+str(self.rowcounter)+"] Institution does not exist for id :"
                    + str(inst_id)+", disecode :"+str(dise_code)+", gpid :"+str(gpid)+", district :"+district+", block :"+block)
            return False
        return True

    def checkGradeValidity(self, passedgrade, csvgrade, qgroup):
        if passedgrade != csvgrade:
            print("["+str(self.rowcounter)+"] Grade in csv: "+csvgrade +
                  " does not match grade argument passed: "+passedgrade)
            return False
        questiongroup = QuestionGroup.objects.get(id=qgroup)
        if passedgrade not in questiongroup.name:
            print("["+str(self.rowcounter)+"] Passed grade: "+passedgrade +
                  " not associated with passed questiongroup: "+qgroup +
                  "("+questiongroup.name+")")
            return False
        return True

    def checkChildNameValidity(self, childname):
        if childname == '':
            print("["+str(self.rowcounter)+"] No childname entered (ignoring row)")
            return False
        return True

    def checkGenderValidity(self, gender):
        if gender == '':
            print("["+str(self.rowcounter)+"] No gender entered (ignoring row)")
            return False
        if gender not in self.validgenders:
            print("["+str(self.rowcounter)+"] Invalid gender :"+gender +
                  ", it should have been: "+str(self.validgenders))
            return False
        return True

    def checkAnswerValidity(self, answer):
        if answer not in self.validanswers:
            print("["+str(self.rowcounter)+"] Incorrect answer type :"+answer +
                  ", it should have been in range: "+str(self.validanswers))
            return False
        return True
    
    def createStudent(self, child_name, father_name, mother_name, institution_id, gender, mt):
        ''' Check if the student already exists '''
        gender = Gender.objects.get(char_id=gender)
        mt = Language.objects.get(char_id=mt)
        s, created = Student.objects.get_or_create(first_name=child_name, father_name=father_name, mother_name=mother_name, institution_id=institution_id, gender=gender,mt=mt, status_id='AC');
        return s

    def convertxlstocsv(self, inputfile):
        with xlrd.open_workbook(inputfile) as wb:
            sh = wb.sheet_by_index(0) 
            csv_file = os.path.dirname(inputfile)+"/"+os.path.splitext(os.path.split(inputfile)[1])[0]+".csv"
            with open(csv_file, 'w') as f:
                c = csv.writer(f)
                for r in range(sh.nrows):
                    row = sh.row_values(r)
                    c.writerow(row)
                f.close()
        return csv_file

    def parseFile(self, csv_file, grade, qgroup):
        with open(csv_file, 'r+') as data_file:
            data = csv.reader(data_file)
            header = 1
            anscount = 0
            ansgroupcount = 0
            for row in data:
                if header:
                    header = 0
                    continue

                self.rowcounter += 1
                csv_grade = str(int(float(row[self.cols["grade"]].strip())))
                district = row[self.cols["district"]].strip().lower()
                block = row[self.cols["block"]].strip().lower()
                ddmmyyyy = row[self.cols["ddmmyyyy"]]
                try:
                    parsed = datetime.strptime(ddmmyyyy, '%d/%m/%Y')
                except ValueError:
                    print("["+str(self.rowcounter) +
                            "] Incorrect date format: "+str(ddmmyyyy)+", should be DD/MM/YYYY")
                    continue
                date_string = parsed.strftime('%Y-%m-%d')
                dov = parser.parse(date_string)
                localtz = timezone(settings.TIME_ZONE)
                dov = localtz.localize(dov)
                
                try:
                    schoolid = int(float(row[self.cols["instid"]].strip()))
                    dise_code = int(float(row[self.cols["disecode"]].strip()))
                    gpid = int(float(row[self.cols["gpid"]].strip()))
                    gpname = row[self.cols["gpname"]].strip().lower()
                    gpname = re.sub("[\(].*?[\)]", "", gpname)
                    #questionseries = row[self.cols["questionseries"]].strip()
                    child_name = row[self.cols["childname"]].strip()
                    father_name = row[self.cols["father_name"]].strip()
                    mother_name = row[self.cols["mother_name"]].strip()
                    volunteer_name = row[self.cols["volunteername"]].strip()
                    gender = row[self.cols["gender"]].strip().lower()
                    enteredat = localtz.localize(datetime.now())
                except ValueError as e:
                    print("["+str(self.rowcounter)+"] "+str(e)+" : "+str(row))
                    continue

                # check values
                if not self.checkQuestionGroupValidity(qgroup) and not self.onlycheck:
                    continue

                if not self.checkGradeValidity(grade, csv_grade, qgroup) and not self.onlycheck:
                    continue

                if not self.checkGPValidity(gpid, gpname) and not self.onlycheck:
                    continue

                if not self.checkInstitutionValidity(schoolid,
                                                     dise_code, gpid,
                                                     district, block) and not self.onlycheck:
                    continue

                if not self.checkChildNameValidity(child_name) and not self.onlycheck:
                    continue

                if not self.checkGenderValidity(gender) and not self.onlycheck:
                    continue

                # if not self.checkDoVValidity(gpid, dov) and not self.onlycheck:
                #     continue


                if not self.checkDistrictGPMapValidity(gpid, district) and not self.onlycheck:
                    continue

                if self.onlycheck:
                    continue
                
                student = self.createStudent(child_name, father_name, mother_name, schoolid, gender, 'kan')
                # Map student to studentgroup
                studentgroup = StudentGroup.objects.get(institution_id=schoolid, name=grade)
                StudentStudentGroupRelation.objects.get_or_create(student=student, student_group=studentgroup, academic_year_id='2021', status_id='AC')
                #Create answer group row
                answergroup = AnswerGroup_Student.objects.create(
                                student=student,
                                group_value=volunteer_name,
                                date_of_visit=dov,
                                questiongroup_id=qgroup,
                                entered_at=enteredat,
                                #comments=questionseries,
                                status_id='AC',
                                is_verified=True)
                ansgroupcount += 1
                # Create the grade answer for this student
                AnswerStudent.objects.create(
                                answer=grade,
                                answergroup_id=answergroup.id,
                                question_id=self.grade_qid)
                anscount += 1
                # Set the gender answer for this student
                AnswerStudent.objects.create(
                                answer=gender,
                                answergroup_id=answergroup.id,
                                question_id=self.gender_qid)
                anscount += 1

                ans_col_cnt = self.ans_col_start # the answers to questions begin here

                for seq in range(self.q_seq_start, self.q_seq_end+1):
                    if not self.checkAnswerValidity(row[ans_col_cnt]):
                        ans_col_cnt += 1
                        continue
                    qgq = QuestionGroup_Questions.objects.get(
                            questiongroup=qgroup, sequence=seq)
                    AnswerStudent.objects.create(
                                        answer=row[ans_col_cnt],
                                        answergroup_id=answergroup.id,
                                        question_id=qgq.question_id)
                    anscount += 1
                    ans_col_cnt += 1

                if district in self.datainserted:
                    if gpid in self.datainserted[district]["gps"]:
                        if schoolid in self.datainserted[district]["gps"][gpid]["schools"]:
                            if grade in self.datainserted[district]["gps"][gpid]["schools"][schoolid]["grades"]:
                                self.datainserted[district]["gps"][gpid]["schools"][schoolid]["grades"][grade]+=1
                            else:
                                self.atainserted[district]["gps"][gpid]["schools"][schoolid]["grades"][grade]=1
                        else:
                            self.datainserted[district]["gps"][gpid]["schools"][schoolid] = {"disecode":dise_code,"grades":{grade:1}}
                    else:
                        self.datainserted[district]["gps"][gpid]= {"gpname":gpname,"schools": {schoolid: {"disecode":dise_code,"grades":{grade:1}}}}
                else:
                    self.datainserted[district]={"gps":{gpid: {"gpname":gpname,"schools": {schoolid: {"disecode":dise_code,"grades":{grade:1}}}}}}

        if self.onlycheck:
            print("Check Done")
            return
           

        print("District, GPID, GPNAME, SCHOOLID, DISE_CODE, GRADE COUNTS")
        gpinfo = {}
        for district in self.datainserted:
            for gpid in self.datainserted[district]["gps"]:
                gpname = self.datainserted[district]["gps"][gpid]["gpname"]
                gpinfo[gpid]={"name":gpname,"grades":{}}
                for schoolid in self.datainserted[district]["gps"][gpid]["schools"]:
                    print(str(district)+", "+str(gpid)+", "+str(self.datainserted[district]["gps"][gpid]["gpname"])+", "+str(schoolid)+", "+str(self.datainserted[district]["gps"][gpid]["schools"][schoolid]["disecode"])+", "+str(self.datainserted[district]["gps"][gpid]["schools"][schoolid]["grades"]))
                    for grade in self.datainserted[district]["gps"][gpid]["schools"][schoolid]["grades"]:
                        if grade in gpinfo[gpid]["grades"]:
                            gpinfo[gpid]["grades"][grade] += self.datainserted[district]["gps"][gpid]["schools"][schoolid]["grades"][grade]
                        else:
                            gpinfo[gpid]["grades"][grade] = self.datainserted[district]["gps"][gpid]["schools"][schoolid]["grades"][grade]


        print("\n\nGPID, GPNAME, GRADE, ENTRY")
        for gpid in gpinfo:
            row_str = str(gpid)+","+gpinfo[gpid]["name"]+","
            for grade in gpinfo[gpid]["grades"]:
                row_str = row_str+str(grade)+","+str(gpinfo[gpid]["grades"][grade])
            print(row_str)

        print("\n\nNumber of AnswerGroups created :"+str(ansgroupcount) +
              ", Number of answers created :"+str(anscount))
        print("Number of Rows :"+str(self.rowcounter))


    def handle(self, *args, **options):
        csv_file= options.get('filename', None)
        if csv_file == None:
            print("Pass the csv file --filename")
            return
        grade = options.get('grade', None)
        if grade == None:
            print("Pass grade argument --grade")
            return
        qgroup = options.get('qgroup', None)
        if qgroup == None:
            print("Pass qgroup argument --qgroup")
            return
         
        self.onlycheck = options.get('onlycheck', False)

        #csv_file = self.convertxlstocsv(inputfile)

        self.parseFile(csv_file, grade, qgroup)
