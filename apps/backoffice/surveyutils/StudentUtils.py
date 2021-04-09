from datetime import date
import xlwt
import csv
import os
import calendar
from assessments.models import Survey, QuestionGroup, QuestionGroup_Questions, Question, AnswerGroup_Student, AnswerStudent, SurveyBoundaryAgg
import shutil
import sys, traceback
from apps.backoffice.surveyutils.BaseUtils import BaseUtils


class studentAssessmentDataUtils(BaseUtils):

    def getQuestionGroups(self, surveyid, from_yearmonth, to_yearmonth):
        list_questiongroups = []
        if from_yearmonth is None and to_yearmonth is None:
            list_questiongroups = AnswerGroup_Student.objects.filter(
                questiongroup__survey=surveyid).distinct(
                    'questiongroup').values_list('questiongroup', flat=True)
        else:
            from_date, to_date = self.convertToDate(from_yearmonth, to_yearmonth)
            list_questiongroups = AnswerGroup_Student.objects.filter(
                questiongroup__survey=surveyid).filter( \
                date_of_visit__range=[from_date, to_date]) \
                    .distinct('questiongroup').values_list('questiongroup', flat=True)

        print("Questiongroups used for this range: ", list_questiongroups)
        return list_questiongroups

    def createXLS(self, surveyinfo, questioninfo, numquestions, questiongroup_id, assessmentdata, filename, skipxls, dest_folder):
        try:
            csvfile = filename+".csv"
            xlsfile = filename+".xlsx"
            book = xlwt.Workbook()
            sheet = book.add_sheet("AssessmentData")
            with open(csvfile, mode='w') as datafile:
                filewriter = csv.writer(datafile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                row = ['State', 'District','Block','Cluster','GPName', 'GP Id', 'Village', 'SchoolName','SchoolId','DiseCode','QuestionGroup Id','QuestionGroupName', 'Source Name', 'Student ID', 'Student Name', 'Fathers Name', 'Mothers Name', 'Date of Visit', 'Academic Year of Visit', 'Group Value', 'RespondentType', 'UserType','UserMobileNumber']
                #for i in range(1, numquestions+1):
                    #row = row+['QuestionText_'+str(i),'Answer_'+str(i)]
                questions_list = questioninfo[questiongroup_id]["questions"]
                for question in questions_list:
                    qn_text = question["display_text"]
                    if not qn_text:
                        qn_text = question["question_text"]
                    row = row + [qn_text]
                filewriter.writerow(row)
                for state in assessmentdata:
                    for district in assessmentdata[state]:
                        for block in assessmentdata[state][district]:
                            for schoolid in assessmentdata[state][district][block]:
                                schooldata = assessmentdata[state][district][block][schoolid]
                                for qgid in schooldata["questiongroups"]:
                                    for agid in schooldata["questiongroups"][qgid]["answergroups"]:
                                        answergroup = schooldata["questiongroups"][qgid]["answergroups"][agid]
                                        row = [state,district,block,schooldata["cluster"],schooldata["gpname"],schooldata["gpid"],schooldata["villagename"],schooldata["schoolname"],schoolid,schooldata["disecode"],qgid,questioninfo[qgid]["name"],questioninfo[qgid]["source"],answergroup["student_id"], answergroup["student_name"], answergroup["father_name"], answergroup["mother_name"], answergroup["dateofvisit"],answergroup["academicyear"],answergroup["groupvalue"],answergroup["respondenttype"],answergroup["usertype"],answergroup["usermobilenumber"]]
                                        for answer in answergroup["answers"]:
                                            # row = row+[answer["questiontext"],answer["answer"]]
                                            row = row+[answer["answer"]]

                                        filewriter.writerow(row)
                datafile.close()
        except Exception as e:
            datafile.close()
            traceback.print_exc(file=sys.stdout)
            print("Exception while creating CSV")
        else:
            # Create XLS files if required
            if not skipxls:
                import pandas as pd
                data = pd.read_csv(csvfile, low_memory=False)
                writer = pd.ExcelWriter(xlsfile, engine='xlsxwriter')
                data.to_excel(writer, 'AssessmentData')
                writer.save()
            # Move the CSV & XLS files to the proper location
            
            shutil.move(csvfile, dest_folder + "/" + csvfile)

            if not skipxls: # Move the XLS file if it was created
                shutil.move(xlsfile, dest_folder + "/" + xlsfile)    


    def getAssessmentData(self, surveyinfo, districts, questiongroup, from_yearmonth, to_yearmonth):
        from_date, to_date = self.convertToDate(from_yearmonth, to_yearmonth)
        assessmentdata = {}
        questioninfo, numquestions = self.getQuestionData(surveyinfo.id,questiongroup)
        for district in districts:
            answergroups = AnswerGroup_Student.objects.filter(student__institution__admin1__id=district, questiongroup=questiongroup)               
            if from_date is not None:
                answergroups = answergroups.filter(date_of_visit__gte=from_date)
            if to_date is not None:
                answergroups = answergroups.filter(date_of_visit__lte=to_date)

            answergroups = answergroups.values_list('student__institution__admin0__name','student__institution__admin1__name', 'student__institution__admin2__name', 'student__institution__admin3__name', 'student__institution__gp__const_ward_name', 'student__institution__gp__id','student__institution__name', 'student__institution__dise__school_code', 'questiongroup__id','date_of_visit','group_value', 'respondent_type', 'created_by__user_type','id','student__institution__id','created_by__mobile_no', 'student__institution__village','student__id', 'student__first_name', 'student__father_name', 'student__mother_name').distinct()
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
                village=answergroup[16]
                student_id=answergroup[17]
                student_name=answergroup[18]
                father_name=answergroup[19]
                mother_name=answergroup[20]
                if state not in assessmentdata:
                    assessmentdata[state] = {district:{block:{schoolid:{"schoolname":schoolname, "disecode":disecode,"cluster":cluster, "gpid":gpid, "gpname":gpname, "villagename":village, "questiongroups":{qgid:{"answergroups":{agid:{"dateofvisit":dateofvisit,"academicyear":academicyear,"groupvalue":groupvalue,"respondenttype":respondenttype,"usertype":usertype,"usermobilenumber":usermobilenumber, "answers":[]}}}}}}}}
                else:
                    if district not in assessmentdata[state]:
                        assessmentdata[state][district] = {block:{schoolid:{"schoolname":schoolname, "disecode":disecode, "cluster":cluster, "gpid":gpid, "gpname":gpname, "villagename":village, "questiongroups":{qgid:{"answergroups":{agid:{"dateofvisit":dateofvisit,"academicyear":academicyear,"groupvalue":groupvalue,"respondenttype":respondenttype,"usertype":usertype,"usermobilenumber":usermobilenumber, "answers":[]}}}}}}}
                    else:
                        if block not in assessmentdata[state][district]:
                            assessmentdata[state][district][block] = {schoolid:{"schoolname":schoolname, "disecode":disecode, "cluster":cluster, "gpid":gpid, "gpname":gpname, "villagename":village,"questiongroups":{qgid:{"answergroups":{agid:{"dateofvisit":dateofvisit,"academicyear":academicyear,"groupvalue":groupvalue,"respondenttype":respondenttype,"usertype":usertype,"usermobilenumber":usermobilenumber,"answers":[]}}}}}}
                        else:
                            if schoolid not in assessmentdata[state][district][block]:
                                assessmentdata[state][district][block][schoolid] = {"schoolname":schoolname, "disecode":disecode, "cluster":cluster, "gpid":gpid, "gpname":gpname, "villagename":village, "questiongroups":{qgid:{"answergroups":{agid:{"dateofvisit":dateofvisit,"academicyear":academicyear,"groupvalue":groupvalue,"respondenttype":respondenttype,"usertype":usertype,"usermobilenumber":usermobilenumber,"answers":[]}}}}}
                            else:
                                if qgid not in assessmentdata[state][district][block][schoolid]["questiongroups"]:
                                    assessmentdata[state][district][block][schoolid]["questiongroups"][qgid]={"answergroups":{agid:{"student_id": student_id, "student_name": student_name, "father_name": father_name, "mother_name": mother_name,"dateofvisit":dateofvisit,"academicyear":academicyear,"groupvalue":groupvalue,"respondenttype":respondenttype,"usertype":usertype,"usermobilenumber":usermobilenumber,"answers":[]}}}
                                else:
                                    assessmentdata[state][district][block][schoolid]["questiongroups"][qgid]["answergroups"][agid]={"student_id": student_id, "student_name": student_name, "father_name": father_name, "mother_name": mother_name,"dateofvisit":dateofvisit,"academicyear":academicyear,"groupvalue":groupvalue,"respondenttype":respondenttype,"usertype":usertype,"usermobilenumber":usermobilenumber,"answers":[]}
                answers = AnswerStudent.objects.filter(answergroup=agid).values('question__id','answer')
                for question in questioninfo[qgid]["questions"]:
                    found=0
                    for answer in answers:
                        if question['qid'] == answer['question__id']:
                            assessmentdata[state][district][block][schoolid]["questiongroups"][qgid]["answergroups"][agid]["answers"].append({"questiontext":question['question_text'],"answer":answer['answer']})
                            found=1
                            break
                    if found == 0:
                        assessmentdata[state][district][block][schoolid]["questiongroups"][qgid]["answergroups"][agid]["answers"].append({'questiontext':question['question_text'],'answer':''})
            #self.createXLS(surveyinfo, questioninfo, numquestions, assessmentdata, filename+ "_" + str(q_group_name))
        print("Finished putting in data")
        return assessmentdata, numquestions, questioninfo
