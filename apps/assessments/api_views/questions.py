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
    AnswerGroup_Institution
)
from assessments.serializers import (
    QuestionGroupSerializer, QuestionSerializer,
    QuestionGroupQuestionSerializer
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
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class QuestionGroupQuestions(
        NestedViewSetMixin, ILPStateMixin, viewsets.ModelViewSet
):
    '''Returns all questions belonging to a questiongroup'''
    queryset = QuestionGroup_Questions.objects.all()
    serializer_class = QuestionGroupQuestionSerializer

    def filter_queryset_by_parents_lookups(self, queryset):
        parents_query_dict = self.get_parents_query_dict()
        survey_id = parents_query_dict['survey']
        questiongroup_id = parents_query_dict['questiongroup']
        return queryset.filter(
            questiongroup__survey_id=survey_id,
            questiongroup_id=questiongroup_id
        )

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
