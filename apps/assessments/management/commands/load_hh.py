import csv
from datetime import datetime
from pytz import timezone
from dateutil import parser
from django.core.management.base import BaseCommand
from django.conf import settings
from assessments.models import (AnswerGroup_Institution,
                                AnswerInstitution, QuestionGroup_Questions)
from schools.models import Institution
from boundary.models import ElectionBoundary


class Command(BaseCommand):

    args = ""
    help = """python3 manage.py load_hh --filename=filename --onlycheck True/False"""
    questiongroup_id = 20
    ans_col_start = 12
    validanswers = {"0", "1", "99", "88"}  # 99 -->dont know, 88 --> unknown
    validgenders = {"male", "female"}
    rowcounter = 0
    defaultmonthyear = datetime.today().strftime("%m/%Y")
    onlycheck = False

    def add_arguments(self, parser):
        parser.add_argument('--filename')
        parser.add_argument('--onlycheck',)

    def checkInstitutionValidity(self, inst_id, schoolname, dise_code):
        try:
            inst = Institution.objects.filter(id=inst_id).values(
                    "name", "dise__school_code")
        except Institution.DoesNotExist:
            print("["+str(self.rowcounter) +
                  "] Institution does not exist for id: "
                  + str(inst_id))
            return False
        if inst[0]["name"].lower() != schoolname:
            print("["+str(self.rowcounter)+"] Institution id ("+str(inst_id) +
                  ") name ("+inst[0]["name"].lower() +
                  ") does not match row  name ("+schoolname+")")
            return False
        if str(inst[0]["dise__school_code"]) != str(dise_code):
            print("["+str(self.rowcounter)+"] Institution id ("+str(inst_id) +
                  ") disecode :"+str(inst[0]["dise__school_code"]) +
                  " does not match disecode in the row :"+str(dise_code))
            return False
        return True

    def checkGPValidity(self, gpid, gpname):
        try:
            ElectionBoundary.objects.get(id=gpid,
                                         const_ward_name__iexact=gpname,
                                         const_ward_type='GP')
            return True
        except ElectionBoundary.DoesNotExist:
            print("["+str(self.rowcounter)+"] No valid GP found for id :"
                  + str(gpid)+", and name :"+gpname)
            return False

    def checkBoundaryValidity(self, inst_id, district, block, cluster, gp):
        inst = Institution.objects.filter(id=inst_id).values(
                    "admin1__name", "admin2__name", "admin3__name",
                    "gp")
        if str(inst[0]["admin1__name"]) != str(district):
            print("["+str(self.rowcounter)+"] Institution id ("+str(inst_id) +
                  ") district :"+str(inst[0]["admin1__name"]) +
                  " does not match district in the row :"+str(district))
            return False
        if str(inst[0]["admin2__name"]) != str(block):
            print("["+str(self.rowcounter)+"] Institution id ("+str(inst_id) +
                  ") block :"+str(inst[0]["admin2__name"]) +
                  " does not match block in the row :"+str(block))
            return False
        if str(inst[0]["admin3__name"]) != str(cluster):
            print("["+str(self.rowcounter)+"] Institution id ("+str(inst_id) +
                  ") cluster:"+str(inst[0]["admin3__name"]) +
                  " does not match cluster in the row :"+str(cluster))
            return False
        if str(inst[0]["gp"]) != str(gp):
            print("["+str(self.rowcounter)+"] Institution id ("+str(inst_id) +
                  ") gp:"+str(inst[0]["gp"]) +
                  " does not match gp in the row :"+str(gp))
            return False
        return True

    def checkAnswerValidity(self, answer):
        if answer not in self.validanswers:
            print("["+str(self.rowcounter)+"] Incorrect answer type :"+answer +
                  ", it should have been in range: "+str(self.validanswers))
            return False
        return True

    def checkVillageValidity(self, instid, village):
        if village == '':
            return True
        inst_village = Institution.objects.filter(id=instid).values(
                                    "village")[0]["village"].lower()
        if village != inst_village:
            print("["+str(self.rowcounter)+"] For Institution id: "+str(instid)+
                  ": DB village (" +inst_village+"), does not match row/xls village (" +
                  village+")")
            return True
        return True

    def handle(self, *args, **options):
        csv_file = options.get('filename', None)
        if csv_file is None:
            print("Pass the csv file --filename")
            return

        self.onlycheck = options.get('onlycheck', False)

        with open(csv_file, 'r+', encoding='utf-8') as data_file:
            data = csv.reader(data_file)
            header = 1
            anscount = 0
            ansgroupcount = 0
            for row in data:
                if header:
                    header = 0
                    continue

                self.rowcounter += 1

                district = row[1].strip().lower()
                block = row[2].strip().lower()
                cluster = row[3].strip().lower()
                inst_id = row[4].strip()
                school_name = row[5].strip().lower()
                dise_code = row[6].strip()
                village = row[7].strip().lower()
                gpname = row[8].strip().lower()
                gpid = row[9].strip()
                date = row[10].strip()
                if date == '':
                    date = '01/'+self.defaultmonthyear
                try:
                    parsed = datetime.strptime(date, '%d/%m/%Y')
                except ValueError:
                    print("["+str(self.rowcounter) +
                          "] Incorrect date format ("+str(date) +
                          ") should be of format DD/MM/YYYY")
                    continue
                date_string = parsed.strftime('%Y-%m-%d')
                dov = parser.parse(date_string)
                localtz = timezone(settings.TIME_ZONE)
                dov = localtz.localize(dov)
                group_value = row[11].strip()
                enteredat = localtz.localize(datetime.now())

                #  check values
                if not self.checkInstitutionValidity(inst_id, school_name,
                                                     dise_code):
                    print("invalid institution")
                    continue

                if not self.checkGPValidity(gpid, gpname):
                    print("invalid gp")
                    continue

                if not self.checkBoundaryValidity(inst_id, district, block,
                                                  cluster, gpid):
                    print("invalid boundary")
                    continue

                if not self.checkVillageValidity(inst_id, village):
                    print("invalid village")
                    continue

                if self.onlycheck:
                    continue 

                answergroup = AnswerGroup_Institution.objects.create(
                                group_value=group_value,
                                date_of_visit=dov,
                                questiongroup_id=self.questiongroup_id,
                                institution_id=inst_id,
                                status_id='AC',
                                is_verified=True,
                                entered_at=enteredat)
                ansgroupcount += 1

                qgq = QuestionGroup_Questions.objects.filter(
                      questiongroup=self.questiongroup_id).order_by('sequence')
                ans_col_cnt = self.ans_col_start
                for question in qgq:
                    question_id = question.question_id
                    ans = row[ans_col_cnt]
                    if not self.checkAnswerValidity(ans):
                        ans_col_cnt += 1
                        continue
                    AnswerInstitution.objects.create(
                                answer=ans,
                                answergroup_id=answergroup.id,
                                question_id=question_id)
                    anscount += 1
                    ans_col_cnt += 1

        if self.onlycheck:
            print("Check Done")
            return

        print("Number of AnswerGroups created :"+str(ansgroupcount) +
              ", Number of answers created :"+str(anscount))
        print("Number of Rows :"+str(self.rowcounter))
