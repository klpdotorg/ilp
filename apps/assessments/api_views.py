import logging

from common.views import ILPListAPIView
from common.utils import Date
from assessments.models import (Survey, QuestionGroup,
                                Question, QuestionGroup_Questions,
                                QuestionGroup_Institution_Association)
from assessments.serializers import (SurveySerializer,
                                     QuestionGroupSerializer,
                                     QuestionSerializer,
                                     QuestionGroupQuestionSerializer,
                                     AnswerSerializer)
from rest_framework import viewsets
from rest_framework.exceptions import APIException
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework_bulk import BulkCreateModelMixin
from rest_framework.response import Response
from common.mixins import ILPStateMixin
from common.views import ILPViewSet

logger = logging.getLogger(__name__)


class SurveysViewSet(ILPViewSet, ILPStateMixin):
    '''Returns all surveys'''
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    #filter_class = StudentGroupFilter


class QuestionGroupViewSet(NestedViewSetMixin, ILPStateMixin, 
                           viewsets.ModelViewSet):
    '''Returns all questiongroups belonging to a survey'''
    queryset = QuestionGroup.objects.all()
    serializer_class = QuestionGroupSerializer

    # M2M query returns duplicates. Overrode this function
    # from NestedViewSetMixin to implement the .distinct()
    def filter_queryset_by_parents_lookups(self, queryset):
        parents_query_dict = self.get_parents_query_dict()
        logger.debug("Arguments passed into view is: %s", parents_query_dict)
        if parents_query_dict:
            try:
                queryset = queryset.filter(
                    **parents_query_dict
                ).order_by().distinct('id')
            except ValueError:
                logger.exception(
                    ("Exception while filtering queryset based on dictionary."
                     "Params: %s, Queryset is: %s"),
                    parents_query_dict, queryset)
                raise Http404
        return queryset.order_by('id')


class QuestionViewSet(ILPStateMixin, viewsets.ModelViewSet):
    '''Return all questions'''
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class QuestionGroupQuestions(NestedViewSetMixin, ILPStateMixin,                                             viewsets.ModelViewSet):
    '''Returns all questions belonging to a questiongroup'''
    queryset = QuestionGroup_Questions.objects.all()
    serializer_class = QuestionGroupQuestionSerializer
    
    # M2M query returns duplicates. Overrode this function
    # from NestedViewSetMixin to implement the .distinct()
    def filter_queryset_by_parents_lookups(self, queryset):
        parents_query_dict = self.get_parents_query_dict()
        print("Arguments passed into QuestionGroupQuestions view is: %s",               parents_query_dict)
        questiongroup = parents_query_dict.get('questiongroup_id')
        print("Question group id is: ", questiongroup)
        if parents_query_dict:
            try:
                queryset = queryset.filter(
                    questiongroup_id=questiongroup
                ).order_by().distinct('id')
            except ValueError:
                logger.exception(
                    ("Exception while filtering queryset based on dictionary."
                     "Params: %s, Queryset is: %s"),
                    parents_query_dict, queryset)
                raise Http404
        return queryset.order_by('id')


class QuestionGroupAnswers(NestedViewSetMixin, ILPStateMixin,
                           viewsets.ModelViewSet):
    queryset = QuestionGroup.objects.all()
    serializer_class = AnswerSerializer
    
    # M2M query returns duplicates. Overrode this function
    # from NestedViewSetMixin to implement the .distinct()
    def filter_queryset_by_parents_lookups(self, queryset):
        parents_query_dict = self.get_parents_query_dict()
        try:
            questiongroup = parents_query_dict.get('questiongroup_id')
            print("Question group id is: ", questiongroup)
            qnGroup = QuestionGroup.objects.get(id=questiongroup)
            surveyon = qnGroup.survey_on;
            print('SurveyOnType object is: ', surveyon)
            if surveyon == 'institution':
                # Query the institution answergroup table
                print("Querying the institution answergroup table")
                answergroupinstitution = qnGroup.answergroup_institution
                queryset = answergroupinstitution.answerinstitution_set.all()
                print("Answers is: ", queryset.count())
            elif surveyon == 'studentgroup':
                pass
            
            elif surveyon == 'student':
                # Query the student answergroup table
                pass   
        except ValueError:
                logger.exception(
                    ("Exception while filtering queryset based on dictionary."
                     "Params: %s, Queryset is: %s"),
                    parents_query_dict, queryset)
                raise Http404  
        return queryset.order_by("id")
    

class StoryMetaView(ILPListAPIView):

    def get(self, request):
        survey = self.request.query_params.get('survey', None)
        source = self.request.query_params.get('source', None)
        versions = self.request.query_params.getlist('version', None)
        admin1_id = self.request.query_params.get('admin1', None)
        admin2_id = self.request.query_params.get('admin2', None)
        admin3_id = self.request.query_params.get('admin3', None)
        school_id = self.request.query_params.get('school_id', None)
        mp_id = self.request.query_params.get('mp_id', None)
        mla_id = self.request.query_params.get('mla_id', None)
        start_date = self.request.query_params.get('from', None)
        end_date = self.request.query_params.get('to', None)
        school_type = self.request.query_params.get(
            'school_type', 'Primary School'
        )
        top_summary = self.request.query_params.get('top_summary', None)
        date = Date()

        response_json = {}
        return Response(response_json)
