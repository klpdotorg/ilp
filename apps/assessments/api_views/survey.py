from django.db.models import Sum

from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from common.mixins import ILPStateMixin
from common.views import ILPViewSet

from boundary.models import BoundaryType

from assessments.models import (
    Survey, SurveySummaryAgg, SurveyDetailsAgg,
    Source, SurveyBoundaryAgg, SurveyUserTypeAgg,
    SurveyRespondentTypeAgg, SurveyInstitutionAgg
)
from assessments.serializers import SurveySerializer
from assessments.filters import SurveyFilter


class SurveysViewSet(ILPViewSet, ILPStateMixin):
    '''Returns all surveys'''
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    # filter_class = StudentGroupFilter


class SurveySummaryAPIView(ListAPIView, ILPStateMixin):
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


class SurveyInfoSourceAPIView(ListAPIView, ILPStateMixin):
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


class SurveyInfoBoundarySourceAPIView(ListAPIView, ILPStateMixin):
    queryset = SurveyBoundaryAgg.objects.all()
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

            boundary_type_ids = queryset.filter(source=source_id)\
                .distinct('boundary_id__boundary_type')\
                .values_list('boundary_id__boundary_type', flat=True)
            
            boundary_list = []
            for b_type_id in boundary_type_ids:
                boundary_qs_agg = queryset\
                    .filter(
                        source=source_id,
                        boundary_id__boundary_type=b_type_id)\
                    .aggregate(
                        Sum('num_schools'),
                        Sum('num_children'),
                        Sum('num_assessments'),
                    )
                boundary_res = {
                    "id": b_type_id,
                    "name": BoundaryType.objects.get(char_id=b_type_id).name,
                    "schools_impacted": boundary_qs_agg['num_schools__sum'],
                    "children_impacted": boundary_qs_agg['num_children__sum'],
                    "assessment_count": boundary_qs_agg['num_assessments__sum']
                }
                boundary_list.append({b_type_id: boundary_res})
            source_res[source_name] = boundary_list
        response['boundaries'] = source_res
        return Response(response)


class SurveyInfoUserAPIView(ListAPIView, ILPStateMixin):
    queryset = SurveyUserTypeAgg.objects.all()
    filter_backends = [SurveyFilter, ]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        response = {}
        user_response = {}
        user_types = queryset.distinct('user_type')\
            .values_list('user_type', flat=True)
        for user_type in user_types:
            user_type_agg = queryset.filter(user_type=user_type)\
                .aggregate(Sum('num_assessments'))
            user_response[user_type] = user_type_agg['num_assessments__sum']
        response['users'] = user_response
        return Response(response)


class SurveyInfoRespondentAPIView(ListAPIView, ILPStateMixin):
    queryset = SurveyRespondentTypeAgg.objects.all()
    filter_backends = [SurveyFilter, ]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        response = {}
        respondent_res = {}
        respondent_types = queryset.distinct('respondent_type')\
            .values_list('respondent_type', flat=True)
        for respondent_type in respondent_types:
            respondent_type_agg = queryset\
                .filter(respondent_type=respondent_type)\
                .aggregate(Sum('num_assessments'))
            respondent_res[respondent_type] = respondent_type_agg[
                'num_assessments__sum']
        response['respondents'] = respondent_res
        return Response(response)


class SurveyInfoSchoolAPIView(ListAPIView, ILPStateMixin):
    serializer_class = SurveySerializer

    def get_queryset(self):
        queryset = SurveyInstitutionAgg.objects.all()
        institution_id = self.request.query_params.get('school_id', None)
        survey_ids = queryset\
            .filter(institution_id=institution_id).distinct('survey_id')\
            .values_list('survey_id', flat=True)
        return Survey.objects.filter(id__in=survey_ids)


class SurveyInfoBoundaryAPIView(ListAPIView, ILPStateMixin):
    serializer_class = SurveySerializer

    def get_queryset(self):
        queryset = SurveyBoundaryAgg.objects.all()
        boundary_id = self.request.query_params.get('boundary_id', None)
        survey_ids = queryset\
            .filter(boundary_id=boundary_id).distinct('survey_id')\
            .values_list('survey_id', flat=True)
        return Survey.objects.filter(id__in=survey_ids)
