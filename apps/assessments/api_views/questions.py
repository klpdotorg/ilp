import logging

from django.http import Http404

from common.views import ILPListAPIView
from common.mixins import ILPStateMixin

from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin

from assessments.models import (
    QuestionGroup, Question, QuestionGroup_Questions,
    AnswerGroup_Institution, QuestionGroup_Institution_Association
)
from assessments.serializers import (
    QuestionGroupSerializer, QuestionSerializer,
    QuestionGroupQuestionSerializer, QuestionGroupInstitutionSerializer
)

logger = logging.getLogger(__name__)


class QuestionGroupViewSet(
        NestedViewSetMixin, ILPStateMixin, viewsets.ModelViewSet
):
    '''Returns all questiongroups belonging to a survey'''
    queryset = QuestionGroup.objects.all()
    serializer_class = QuestionGroupSerializer


class QuestionViewSet(ILPStateMixin, viewsets.ModelViewSet):
    '''Return all questions'''
    serializer_class = QuestionSerializer

    def get_queryset(self):
        queryset = Question.objects.all()
        survey_id = self.request.query_params.get('survey_id', None)
        if survey_id:
            questiongroups = QuestionGroup.objects.filter(survey_id=survey_id)
            question_ids = QuestionGroup_Questions.objects.filter(
                questiongroup__in=questiongroups).values_list(
                    'question_id', flat=True)
            return queryset.filter(id__in=question_ids)
        return queryset


class QuestionGroupQuestions(
        NestedViewSetMixin, ILPStateMixin, viewsets.ModelViewSet
):
    '''Returns all questions belonging to a questiongroup'''

    queryset = Question.objects.all()

    def get_queryset(self):
        parents_query_dict = self.get_parents_query_dict()
        questiongroup_id = parents_query_dict['questiongroup']
        question_list = QuestionGroup_Questions.objects\
            .filter(questiongroup_id=questiongroup_id)\
            .values_list('question', flat=True)
        return Question.objects.filter(id__in=question_list)

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return QuestionSerializer
        return QuestionGroupQuestionSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['questiongroup'] = \
            self.kwargs['parent_lookup_questiongroup']
        return context


class QGroupStoriesInfoView(ILPListAPIView):
    """
    Returns total number of stories for the home page
    """
    def get(self, request, *args, **kwargs):
        return Response({
            'total_stories': AnswerGroup_Institution.objects.filter(
                questiongroup__survey__id=5).count(),
            'total_verified_stories': AnswerGroup_Institution.objects.filter(
                questiongroup__survey__id=5).filter(is_verified=True).count(),
            'total_images': 0
        })


class QuestionGroupSchoolViewSet(viewsets.ModelViewSet):
    queryset = QuestionGroup_Institution_Association.objects.all()
    serializer_class = QuestionGroupInstitutionSerializer
