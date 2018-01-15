from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from common.mixins import ILPStateMixin
from common.views import ILPViewSet

from assessments.models import (
    Survey, SurveySummaryAgg, SurveyDetailsAgg,
    Source, SurveyBoundaryAgg, SurveyUserTypeAgg,
    SurveyRespondentTypeAgg, SurveyInstitutionAgg,
    SurveyAnsAgg, Question, SurveyQuestionKeyAgg,
    SurveyElectionBoundaryAgg, SurveyClassGenderAgg,
    SurveyClassAnsAgg, SurveyClassQuestionKeyAgg,
    SurveyQuestionGroupQuestionKeyAgg, SurveyQuestionGroupGenderAgg,
    SurveyQuestionGroupGenderCorrectAnsAgg, SurveyClassGenderCorrectAnsAgg,
    SurveyQuestionKeyCorrectAnsAgg, SurveyClassQuestionKeyCorrectAnsAgg,
    SurveyQuestionGroupQuestionKeyCorrectAnsAgg,
    SurveyInstitutionQuestionGroupAnsAgg,
    QuestionGroup_Institution_Association,
    QuestionGroup_StudentGroup_Association
)
from assessments.serializers import SurveySerializer
from assessments.filters import SurveyTagFilter


class SurveysViewSet(ILPViewSet, ILPStateMixin):
    '''Returns all surveys'''
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    filter_class = SurveyTagFilter


class SurveyInstitutionDetailAPIView(ListAPIView, ILPStateMixin):

    def list(self, request, *args, **kwargs):
        survey_id = self.request.query_params.get('survey_id', None)
        survey_on = Survey.objects.get(id=survey_id).survey_on
        institution_id = self.request.query_params.get('institution_id', None)
        if survey_on == 'institution':
            res = {}
            qset = QuestionGroup_Institution_Association.objects.filter(
                institution_id=institution_id,
                questiongroup__survey_id=survey_id)
            for qgroup_inst in qset:
                res[qgroup_inst.questiongroup_id] = {
                    "id": qgroup_inst.questiongroup_id,
                    "name": qgroup_inst.questiongroup.name
                }
        else:
            res = {}
            sg_qset = QuestionGroup_StudentGroup_Association.\
                objects.filter(
                    studentgroup__institution_id=institution_id,
                )
            response = {}
            for sgroup_inst in sg_qset:
                sg_name = sgroup_inst.studentgroup.name
                sg_id = sgroup_inst.studentgroup.id
                res[sg_name] = {
                    "id": sg_id, "name": sg_name
                }
                for studgroup_qgroup in sg_qset.filter(
                        questiongroup__survey_id=survey_id):
                    qgroup = studgroup_qgroup.questiongroup
                    res[sg_name][qgroup.id] = {
                        "id": qgroup.id, "name": qgroup.name
                    }
                    response.update(res)
        return Response(response)

'''Returns all survey answers for a specific institution'''
class SurveyInstitutionAnsAggView(ListAPIView, ILPStateMixin):
    queryset = SurveyInstitutionQuestionGroupAnsAgg.objects.all()

    def list(self, request, *args, **kwargs):
        surveyid = self.request.query_params.get('survey_id', None)
        schoolid = self.request.query_params.get('school_id', None)
        questions_list=[]
        if surveyid is not None and schoolid is not None:
            question_answers = SurveyInstitutionQuestionGroupAnsAgg.objects.all().filter(survey_id=surveyid).filter(institution_id=schoolid).distinct('answer_option')
            distinct_questions = SurveyInstitutionQuestionGroupAnsAgg.objects.all().filter(survey_id=surveyid).filter(institution_id=schoolid).distinct('question_desc')
            for question in distinct_questions:
                answers=question_answers.values('answer_option', 'num_answers')
                answer_list={}
                for answer in answers:
                    answer_list[answer['answer_option']]= answer['num_answers']                    
                answer = {"display_text": question.question_desc,
                          "question_id": question.question_id.id,
                          "answers": answer_list,
                          }
                questions_list.append(answer)
                
        return Response(questions_list)



