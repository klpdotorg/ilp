import django_filters

from rest_framework.filters import BaseFilterBackend

from .models import AnswerGroup_Institution


class AnswersSurveyTypeFilter(django_filters.FilterSet):
    survey_id = django_filters.CharFilter(name="questiongroup__survey__id")
    is_verified = django_filters.BooleanFilter(name='is_verified')

    class Meta:
        model = AnswerGroup_Institution
        fields = ['survey_id', 'is_verified']


class SurveyFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        survey_tag = request.query_params.get('survey_tag', None)
        survey_ids = request.query_params.getlist('survey_ids', None)
        institution_type = request.query_params.get('school_type', None)

        if survey_ids:
            queryset = queryset.filter(survey_id__in=survey_ids)
        if survey_tag:
            queryset = queryset.filter(survey_tag=survey_tag)
        if institution_type:
            queryset = queryset.filter(institution_type=institution_type)

        return queryset
