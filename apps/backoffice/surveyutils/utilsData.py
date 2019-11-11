from datetime import date
import xlwt
import csv
import os
import calendar
from assessments.models import Survey, QuestionGroup, QuestionGroup_Questions, Question, AnswerGroup_Institution, AnswerInstitution, SurveyBoundaryAgg

class commonAssessmentDataUtils():

    def getAllQuestionGroupData(self, surveyid):
        questiondata = {}
        try:
            question_qs = QuestionGroup_Questions.objects.filter(questiongroup__survey_id=surveyid).values('questiongroup_id', 'questiongroup__name', 'question__id', 'question__question_text','question__display_text', 'sequence')
        except QuestionGroup_Questions.DoesNotExist:
            print("Did not find relevant question data for surveyid: "+str(surveyid))
            return None

        for qs in question_qs:
            if qs['questiongroup_id'] in questiondata:
                questiondata[qs['questiongroup_id']]['questions'][qs['sequence']] = {'question_text':qs['question_question_text'], 'qid': qs['question_id'], 'display_text': qs['question__display_text']}
            else:
                questiondata[qs['questiongroup_id']] = {'name':qs['questiongroup__name'], 'questions':[]}
                questiondata[qs['questiongroup_id']]['questions'][qs['sequence']] = {'question_text':qs['question_question_text'], 'qid': qs['question_id'], 'display_text': qs['question__display_text']}
        return questiondata

    def getQuestionData(self, surveyid):
        numquestions = 0
        questiondata = {}
        try:
            question_qs = QuestionGroup_Questions.objects.filter(questiongroup__survey_id=surveyid).values('questiongroup_id', 'questiongroup__name', 'question__id', 'question__question_text', 'question__display_text','questiongroup__source__name', 'sequence').order_by('sequence')
        except QuestionGroup_Questions.DoesNotExist:
            print("Did not find relevant question data for surveyid: "+str(surveyid))
            return None

        for qs in question_qs:
            if numquestions < qs['sequence']:
                numquestions = numquestions+1
            if qs['questiongroup_id'] in questiondata:
                questiondata[qs['questiongroup_id']]['questions'].append({'question_text':qs['question__question_text'], 'qid': qs['question__id'], 'display_text': qs['question__display_text'], 'sequence': qs['sequence']})
            else:
                questiondata[qs['questiongroup_id']] = {'name':qs['questiongroup__name'],'source':qs['questiongroup__source__name'], 'questions':[]}
                questiondata[qs['questiongroup_id']]['questions'].append({'question_text':qs['question__question_text'], 'qid': qs['question__id'], 'display_text': qs['question__display_text'], 'sequence': qs['sequence']})
        return questiondata, numquestions



    def validateSurvey(self, surveyid):
        if surveyid == None:
            print("Mandatory parameter surveyid not passed")
            return None
        try:
            survey = Survey.objects.get(id=surveyid)
        except Survey.DoesNotExist:
            print("Invalid Survey id passed: "+str(surveyid)+", please enter a valid one")
            return None
        return survey


    def createXLS(self, surveyinfo, questioninfo, numquestions, assessmentdata, filename):
        csvfile = filename+".csv"
        xlsfile = filename+".xlsx"
        book = xlwt.Workbook()
        sheet = book.add_sheet("AssessmentData")
        with open(csvfile, mode='w') as datafile:
            filewriter = csv.writer(datafile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            row = ['State', 'District','Block','Cluster','GPName', 'GP Id','SchoolName','SchoolId','DiseCode','QuestionGroup Id','QuestionGroupName', 'Source Name', 'Date of Visit', 'Academic Year of Visit', 'Group Value', 'RespondentType', 'UserType','UserMobileNumber']
            for i in range(1, numquestions+1):
                row = row+['QuestionText_'+str(i),'Answer_'+str(i)]
            filewriter.writerow(row)
            for state in assessmentdata:
                for district in assessmentdata[state]:
                    for block in assessmentdata[state][district]:
                        for schoolid in assessmentdata[state][district][block]:
                            schooldata = assessmentdata[state][district][block][schoolid]
                            for qgid in schooldata["questiongroups"]:
                                for agid in schooldata["questiongroups"][qgid]["answergroups"]:
                                    answergroup = schooldata["questiongroups"][qgid]["answergroups"][agid]
                                    row = [state,district,block,schooldata["cluster"],schooldata["gpname"],schooldata["gpid"],schooldata["schoolname"],schoolid,schooldata["disecode"],qgid,questioninfo[qgid]["name"],questioninfo[qgid]["source"],answergroup["dateofvisit"],answergroup["academicyear"],answergroup["groupvalue"],answergroup["respondenttype"],answergroup["usertype"],answergroup["usermobilenumber"]]
                                    for answer in answergroup["answers"]:
                                        row = row+[answer["questiontext"],answer["answer"]]
                                    filewriter.writerow(row)
            datafile.close()

        # For very big files, convert CSV to XLS. Changed from xlwt package
        # to pandas because xlwt was failing to write rows > 65536
        import pandas as pd
        data = pd.read_csv(csvfile, low_memory=False)
        writer = pd.ExcelWriter(xlsfile, engine='xlsxwriter')
        data.to_excel(writer, 'AssessmentData')
        writer.save()
        # Old code using xlwt package to write xls file
        # with open(csvfile, 'rt', encoding='utf8') as f:
        #     reader = csv.reader(f)
        #     for r, row in enumerate(reader):
        #         for c, col in enumerate(row):
        #             sheet.write(r, c, col)
        # book.save(xlsfile)

    def deleteTempFiles(self, tempFiles):
        for f in tempFiles:
            os.remove(f)

    def getAcademicYear(self, inputdate):
        year = inputdate[:4]
        month = inputdate[5:7]
        if int(month) >=6:
            academicyear = year+"-"+str(int(year)+1)
        else:
            academicyear = str(int(year)-1)+"-"+year
        return academicyear

    def convertToDate(self, from_yearmonth_string, to_yearmonth_string):
        from_date = None
        to_date = None
        if from_yearmonth_string is not None:
            year = int(from_yearmonth_string[0:4])
            month = int(from_yearmonth_string[4:])
            from_date = date(year=year, month=month, day=1)
        if to_yearmonth_string is not None:
            to_year = int(to_yearmonth_string[0:4])
            to_month = int(to_yearmonth_string[4:])
            to_date = date(year=to_year, month=to_month, day=calendar.monthrange(to_year, to_month)[1])
        return from_date, to_date

    def getAssessmentData(self, surveyinfo, questioninfo, from_yearmonth, to_yearmonth):
        assessmentdata = {}
        if from_yearmonth and to_yearmonth is not None:
            districts = SurveyBoundaryAgg.objects.filter(
                survey_id=surveyinfo.id, boundary_id__boundary_type_id='SD').filter(
                    yearmonth__range=[from_yearmonth, to_yearmonth]
                ).values_list('boundary_id', flat=True).distinct()
        else:
            districts = SurveyBoundaryAgg.objects.filter(
                survey_id=surveyinfo.id, boundary_id__boundary_type_id='SD').values_list('boundary_id', flat=True).distinct()
        print(districts)
        for district in districts:
            print(district)
            answergroups = AnswerGroup_Institution.objects.filter(institution__admin1__id=district, questiongroup__survey_id=surveyinfo.id)
            # If from and to dates are given filter based on that
            from_date, to_date = self.convertToDate(from_yearmonth, to_yearmonth)
            print(from_date, to_date)
            if from_date is not None:
                answergroups = answergroups.filter(date_of_visit__gte=from_date)
            if to_date is not None:
                answergroups = answergroups.filter(date_of_visit__lte=to_date)

            answergroups = answergroups.values_list('institution__admin0__name','institution__admin1__name', 'institution__admin2__name', 'institution__admin3__name', 'institution__gp__const_ward_name', 'institution__gp__id','institution__name', 'institution__dise__school_code', 'questiongroup__id','date_of_visit','group_value', 'respondent_type', 'created_by__user_type','id','institution__id','created_by__mobile_no').distinct()
            print("Got data")
            for answergroup in answergroups:
                state= answergroup[0]
                district=answergroup[1]
                block=answergroup[2]
                cluster=answergroup[3]
                gpname=answergroup[4]
                gpid=answergroup[5]
                schoolname=answergroup[6]
                disecode=answergroup[7]
                qgid=answergroup[8]
                dateofvisit=str(answergroup[9].date())
                academicyear=self.getAcademicYear(dateofvisit)
                groupvalue=answergroup[10]
                respondenttype=answergroup[11]
                usertype=answergroup[12]
                agid=answergroup[13]
                schoolid=answergroup[14]
                usermobilenumber=answergroup[15]
                if state not in assessmentdata:
                    assessmentdata[state] = {district:{block:{schoolid:{"schoolname":schoolname, "disecode":disecode,"cluster":cluster, "gpid":gpid, "gpname":gpname, "questiongroups":{qgid:{"answergroups":{agid:{"dateofvisit":dateofvisit,"academicyear":academicyear,"groupvalue":groupvalue,"respondenttype":respondenttype,"usertype":usertype,"usermobilenumber":usermobilenumber, "answers":[]}}}}}}}}
                else:
                    if district not in assessmentdata[state]:
                        assessmentdata[state][district] = {block:{schoolid:{"schoolname":schoolname, "disecode":disecode, "cluster":cluster, "gpid":gpid, "gpname":gpname, "questiongroups":{qgid:{"answergroups":{agid:{"dateofvisit":dateofvisit,"academicyear":academicyear,"groupvalue":groupvalue,"respondenttype":respondenttype,"usertype":usertype,"usermobilenumber":usermobilenumber, "answers":[]}}}}}}}
                    else:
                        if block not in assessmentdata[state][district]:
                            assessmentdata[state][district][block] = {schoolid:{"schoolname":schoolname, "disecode":disecode, "cluster":cluster, "gpid":gpid, "gpname":gpname, "questiongroups":{qgid:{"answergroups":{agid:{"dateofvisit":dateofvisit,"academicyear":academicyear,"groupvalue":groupvalue,"respondenttype":respondenttype,"usertype":usertype,"usermobilenumber":usermobilenumber,"answers":[]}}}}}}
                        else:
                            if schoolid not in assessmentdata[state][district][block]:
                                assessmentdata[state][district][block][schoolid] = {"schoolname":schoolname, "disecode":disecode, "cluster":cluster, "gpid":gpid, "gpname":gpname, "questiongroups":{qgid:{"answergroups":{agid:{"dateofvisit":dateofvisit,"academicyear":academicyear,"groupvalue":groupvalue,"respondenttype":respondenttype,"usertype":usertype,"usermobilenumber":usermobilenumber,"answers":[]}}}}}
                            else:
                                if qgid not in assessmentdata[state][district][block][schoolid]["questiongroups"]:
                                    assessmentdata[state][district][block][schoolid]["questiongroups"][qgid]={"answergroups":{agid:{"dateofvisit":dateofvisit,"academicyear":academicyear,"groupvalue":groupvalue,"respondenttype":respondenttype,"usertype":usertype,"usermobilenumber":usermobilenumber,"answers":[]}}}
                                else:
                                    assessmentdata[state][district][block][schoolid]["questiongroups"][qgid]["answergroups"][agid]={"dateofvisit":dateofvisit,"academicyear":academicyear,"groupvalue":groupvalue,"respondenttype":respondenttype,"usertype":usertype,"usermobilenumber":usermobilenumber,"answers":[]}



                answers = AnswerInstitution.objects.filter(answergroup=agid).values('question__id','answer')

                for question in questioninfo[qgid]["questions"]:
                    found=0
                    for answer in answers:
                        if question['qid'] == answer['question__id']:
                            assessmentdata[state][district][block][schoolid]["questiongroups"][qgid]["answergroups"][agid]["answers"].append({"questiontext":question['question_text'],"answer":answer['answer']})
                            found=1
                            break
                    if found == 0:
                        assessmentdata[state][district][block][schoolid]["questiongroups"][qgid]["answergroups"][agid]["answers"].append({'questiontext':question['question_text'],'answer':''})
            print("Finished putting in data")
        return assessmentdata
 
