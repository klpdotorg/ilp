from django.db.models import Sum

from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from common.mixins import ILPStateMixin
from common.views import ILPViewSet

from assessments.models import (
    Survey, SurveySummaryAgg, SurveyDetailsAgg, 
    Source)
from assessments.serializers import SurveySerializer
from assessments.filters import SurveyFilter


class SurveysViewSet(ILPViewSet, ILPStateMixin):
    '''Returns all surveys'''
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    # filter_class = StudentGroupFilter


class SurveysSummaryAPIView(ListAPIView, ILPStateMixin):
    queryset = SurveySummaryAgg.objects.all()
    filter_backends = [SurveyFilter, ]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        qs_agg = queryset.aggregate(
            Sum('num_schools'), Sum('num_children'), Sum('num_assessments'))

        response = {
            "summary": {
                "total_school": qs_agg['num_schools__sum'],
                "schools_impacted": qs_agg['num_schools__sum'],
                "children_impacted": qs_agg['num_children__sum'],
                "total_assessments": qs_agg['num_assessments__sum'],
            }
        }
        res_surveys = []
        for sid in queryset.distinct('survey_id').values_list(
                'survey_id', flat=True
        ):
            survey = Survey.objects.get(id=sid)
            sources = survey.questiongroup_set.distinct(
                'source__name').values_list('source', flat=True)
            res_survey = {
                "id": sid,
                "name": survey.name,
                "source": sources
            }
            res_surveys.append(res_survey)
        response['surveys'] = res_surveys
        return Response(response)


class SurveysInfoSourceAPIView(ListAPIView, ILPStateMixin):
    queryset = SurveyDetailsAgg.objects.all()
    filter_backends = [SurveyFilter, ]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        source_ids = queryset.distinct(
            'source').values_list('source', flat=True)

        response = {}
        source_res = {}
        for source_id in source_ids:
            source_name = "None"
            if source_id:
                source_name = Source.objects.get(id=source_id).name

            qs_agg = queryset.filter(source=source_id).aggregate(
                Sum('num_schools'), Sum('num_assessments'),
                Sum('num_verified_assessment')
            )
            source_res[source_name] = {
                "schools_impacted": qs_agg['num_schools__sum'],
                "assessment_count": qs_agg['num_assessments__sum'],
                # Todo
                "last_assessment": None,
                "verified_assessment_count": qs_agg[
                    'num_verified_assessment__sum'
                ]
            }
        response['source'] = source_res
        return Response(response)
