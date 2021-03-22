from datetime import date
import xlwt
import csv
import os
import calendar
from assessments.models import Survey, QuestionGroup, QuestionGroup_Questions, Question, AnswerGroup_Institution, AnswerInstitution, SurveyBoundaryAgg
import shutil
import sys, traceback
import apps.backoffice.surveyutils.BaseUtils


class institutionAssessmentDataUtils(BaseUtils):

    def getQuestionGroups(self, surveyid, from_yearmonth, to_yearmonth):
        list_questiongroups = []
        if from_yearmonth is None and to_yearmonth is None:
            list_questiongroups = AnswerGroup_Institution.objects.filter(
                questiongroup__survey=surveyid).distinct(
                    'questiongroup').values_list('questiongroup', flat=True)
        else:
            from_date, to_date = self.convertToDate(from_yearmonth, to_yearmonth)
            list_questiongroups = AnswerGroup_Institution.objects.filter(
                questiongroup__survey=surveyid).filter( \
                date_of_visit__range=[from_date, to_date]) \
                    .distinct('questiongroup').values_list('questiongroup', flat=True)

            # from_short_year = from_yearmonth[2:-2]
            # to_short_year = int(to_yearmonth[2:-2])
            # if int(to_short_year) == int(from_short_year):
            #     to_short_year = int(to_short_year) + 1
            # academic_year_id = from_short_year + str(to_short_year)
            # list_questiongroups = QuestionGroup.objects.filter(survey_id=surveyid).filter(academic_year_id=academic_year_id).distinct('id').values_list('id', flat=True)
        print("Questiongroups used for this range: ", list_questiongroups)
        return list_questiongroups

    def getAssessmentData(self, surveyinfo, districts, questiongroup, from_yearmonth, to_yearmonth):
        from_date, to_date = self.convertToDate(from_yearmonth, to_yearmonth)
        assessmentdata = {}
        questioninfo, numquestions = self.getQuestionData(surveyinfo.id,questiongroup)
        for district in districts:
            answergroups = AnswerGroup_Institution.objects.filter(institution__admin1__id=district, questiongroup=questiongroup)               
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
            #self.createXLS(surveyinfo, questioninfo, numquestions, assessmentdata, filename+ "_" + str(q_group_name))
        print("Finished putting in data")
        return assessmentdata, numquestions, questioninfo
