import django_filters

from rest_framework.filters import BaseFilterBackend

from .models import (
    AnswerGroup_Institution, Survey
)


class AnswersSurveyTypeFilter(django_filters.FilterSet):
    survey_id = django_filters.CharFilter(field_name="questiongroup__survey__id")
    is_verified = django_filters.BooleanFilter(field_name='is_verified')

    class Meta:
        model = AnswerGroup_Institution
        fields = ['id', 'survey_id', 'is_verified']


class SurveyTagFilter(django_filters.FilterSet):
    survey_tag = django_filters.CharFilter(field_name="surveytagmapping__tag")

    class Meta:
        model = Survey
        fields = ['survey_tag']


class SurveyFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        survey_tag = request.query_params.get('survey_tag', None)
        survey_id = request.query_params.get('survey_id', None)
        institution_type = request.query_params.get('school_type', None)
        to_ = request.query_params.get('to', None)
        from_ = request.query_params.get('from', None)
        sources = request.query_params.getlist('source', [])

        if survey_id:
            queryset = queryset.filter(survey_id=survey_id)

        if survey_tag:
            queryset = queryset.filter(survey_tag=survey_tag)

        if institution_type:
            queryset = queryset.filter(institution_type=institution_type)

        if sources:
            source_ids = Source.objects.filter(name__in=sources).\
                values_list('id', flat=True)
            queryset = queryset.filter(source__in=source_ids)

        if to_:
            to_ = to_.split('-')
            to_year, to_month = to_[0], to_[1]
            yearmonth = int(to_year + to_month)
            queryset = queryset.filter(yearmonth__lte=yearmonth)

        if from_:
            from_ = from_.split('-')
            from_year, from_month = from_[0], from_[1]
            yearmonth = int(from_year + from_month)
            queryset = queryset.filter(yearmonth__gte=yearmonth)

        return queryset
