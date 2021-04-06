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
from django.db.models import Q

class Command(BaseCommand):

    args = ""
    help = """python3 manage.py loadgpc [--filename=filename] [--grade=4] [--qgroup=47]"""
    gender_qid = 291
    grade_qid = 130
    '''SL NO	DEO NAME	CLASS	DISTRICT	BLOCK	CLUSTER NAME	DATE	KLP ID	DISE CODE	VILLAGE NAME	
    GP ID	GRAMA PANCHAYAT	STUDENT NAME	SEX ( MALE / FEMALE )	FATHER NAME 	MOTHER NAME	Q1	Q2	Q3	Q4	Q5	Q6	Q7	Q8	Q9	Q10	Q11	Q12	Q13	Q14	Q15	TOTAL	VOLUNTEER NAME	LOT DETAILS
    '''
    cols = {"grade":2, "district":3, "block":4, "ddmmyyyy":6,"instid":7,
            "disecode":8, "village": 9, "gpid":10, "gpname":11, 
            "childname": 12, "gender":13, "volunteername":32,
            "father_name": 14, "mother_name":15}
    q_seq_start = 3
    q_seq_end = 17
    ans_col_start = 16
    validanswers = {"0", "1"}
    validgenders = {"male", "female", "unknown"}
    rowcounter = 0
    gplist = {}
    datainserted = {}
    districtgpmap = {}
    onlycheck = False
    inst_village_map = {}
    inst_gp_mismatch = {}

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
            if inst_id not in self.inst_gp_mismatch:
                self.inst_gp_mismatch[inst_id] = {
                    "institution_id": inst_id,
                    "dise_code": dise_code,
                    "gp_id": gpid,
                    "district": district,
                    "block": block
                }
                print("["+str(self.rowcounter)+"] Institution does not exist for id :"
                        + str(inst_id)+", disecode :"+str(dise_code)+", gpid :"+str(gpid)+", district :"+district+", block :"+block)
            return False
        return True
    
    def checkInstitutionVillageValidity(self, inst_id, dise_code, gpid, village,
                                        district, block):
        try:
            inst = Institution.objects.get(id=inst_id, dise_id__school_code=dise_code,village__iexact=village, gp_id=gpid, admin1_id__name=district, admin2_id__name=block)
        except Institution.DoesNotExist:
            if inst_id not in self.inst_village_map:
                try:
                    inst = Institution.objects.get(id=inst_id, dise_id__school_code=dise_code)
                    village_lower=inst.village
                    if village_lower:
                        village_lower=village_lower.lower()
                    else:
                        village_lower=''
                    self.inst_village_map[inst_id]={"institution_id": inst_id, "dise_code": dise_code, "district": district, "block": block, "gp_id": gpid, "village": village, "db_village": village_lower}
                except Institution.DoesNotExist:
                    return False    
                # print("["+str(self.rowcounter)+"] Institution to VILLAGE mapping not matching for id :"
                #         + str(inst_id)+", disecode :"+str(dise_code)+", gpid :"+str(gpid)+", village: " + village + ",district :"+district+", block :"+block)
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
            print("["+str(self.rowcounter)+"] No gender entered. (ignoring row)")
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
        if not created:
            print("Child already exists name: %s, father: %s, mother: %s, institution_id: %s"%(child_name, father_name, mother_name, institution_id))
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
                    village = row[self.cols["gpname"]].strip().lower()
                    village = re.sub("[\(].*?[\)]", "", village)
                    #questionseries = row[self.cols["questionseries"]].strip()
                    child_name = row[self.cols["childname"]].strip()
                    father_name = row[self.cols["father_name"]].strip()
                    mother_name = row[self.cols["mother_name"]].strip()
                    volunteer_name = row[self.cols["volunteername"]].strip()
                    gender = row[self.cols["gender"]].strip().lower()
                    # If no gender entered, assign a gender so we don't lose
                    # the student
                    if(gender == ''):
                        gender = 'unknown'
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
                
                if village and self.onlycheck: 
                    self.checkInstitutionVillageValidity(schoolid,
                                                     dise_code, gpid, village,
                                                     district, block)
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
                try:
                    studentgroup = StudentGroup.objects.filter(institution_id=schoolid, name=grade).get(Q(section__isnull=True) | Q(section='')|Q(section=' '))
                except:
                    print("FIXIT: Error in getting student group because multiples returned for school ID" + str(schoolid))
                relation, c = StudentStudentGroupRelation.objects.get_or_create(student=student, student_group=studentgroup, academic_year_id='2021', status_id='AC')
                if not c:
                    print("WARNING: Student student group relation already exists. ")
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
                        self.datainserted[district]["gps"][gpid]= {"village": village, "gpname":gpname,"schools": {schoolid: {"disecode":dise_code,"grades":{grade:1}}}}
                else:
                    self.datainserted[district]={"gps":{gpid: {"village": village, "gpname":gpname,"schools": {schoolid: {"disecode":dise_code,"grades":{grade:1}}}}}}

        if self.onlycheck:
            print("Check Done")
            print("Mismatch of institution to village")
            with open('school_village_mismatch.csv', 'w') as f:
                f.write("institution_id, dise_code, district, block, gp_id, village, village in DB")
                for value in self.inst_village_map.values():
                    f.write("%s,%s,%s,%s,%s,%s,%s\n"%(value["institution_id"],value["dise_code"], value["district"], value["block"],value["gp_id"], value["village"], value["db_village"]))
        
        if self.onlycheck:
            print("Mistmatch of institution to GP")
            with open('school_gp_mismatch.csv', 'w') as f:
                f.write("institution_id, dise_code, district, block, gp_id")
                for value in self.inst_gp_mismatch.values():
                    f.write("%s,%s,%s,%s,%s\n"%(value["institution_id"],value["dise_code"], value["district"], value["block"],value["gp_id"]))
            return
           

        print("District, GPID, GPNAME, VILLAGE, SCHOOLID, DISE_CODE, GRADE COUNTS")
        gpinfo = {}
        for district in self.datainserted:
            for gpid in self.datainserted[district]["gps"]:
                gpname = self.datainserted[district]["gps"][gpid]["gpname"]
                villagename = self.datainserted[district]["gps"][gpid]["village"]
                gpinfo[gpid]={"name":gpname, "village": villagename, "grades":{}}
                for schoolid in self.datainserted[district]["gps"][gpid]["schools"]:
                    print(str(district)+", "+str(gpid)+", "+str(self.datainserted[district]["gps"][gpid]["gpname"])+", "+str(schoolid)+", "+str(self.datainserted[district]["gps"][gpid]["schools"][schoolid]["disecode"])+", "+str(self.datainserted[district]["gps"][gpid]["schools"][schoolid]["grades"]))
                    for grade in self.datainserted[district]["gps"][gpid]["schools"][schoolid]["grades"]:
                        if grade in gpinfo[gpid]["grades"]:
                            gpinfo[gpid]["grades"][grade] += self.datainserted[district]["gps"][gpid]["schools"][schoolid]["grades"][grade]
                        else:
                            gpinfo[gpid]["grades"][grade] = self.datainserted[district]["gps"][gpid]["schools"][schoolid]["grades"][grade]


        print("\n\nGPID, GPNAME, VILLAGE, GRADE, ENTRY")
        for gpid in gpinfo:
            row_str = str(gpid)+","+gpinfo[gpid]["name"]+"," + gpinfo[gpid]["village"] + ","
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
