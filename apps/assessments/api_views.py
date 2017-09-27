import logging

from common.views import ILPListAPIView
from common.utils import Date
from assessments.models import ( Survey, QuestionGroup)
from assessments.serializers import (SurveySerializer,
    QuestionGroupSerializer)
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
