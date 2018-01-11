import django_filters

from rest_framework.filters import BaseFilterBackend

from .models import (AnswerGroup_Institution,
                     Survey)


class AnswersSurveyTypeFilter(django_filters.FilterSet):
    survey_id = django_filters.CharFilter(name="questiongroup__survey__id")
    is_verified = django_filters.BooleanFilter(name='is_verified')

    class Meta:
        model = AnswerGroup_Institution
        fields = ['id', 'survey_id', 'is_verified']


class SurveyTagFilter(django_filters.FilterSet):
    tag = django_filters.CharFilter(name="surveytagmapping__tag")

    class Meta:
        model = Survey
        fields = ['tag']


class SurveyFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        survey_tag = request.query_params.get('survey_tag', None)
        survey_id = request.query_params.get('survey_id', None)
        institution_type = request.query_params.get('school_type', None)
        to_ = request.query_params.get('to', None)
        from_ = request.query_params.get('from', None)

        if survey_id:
            queryset = queryset.filter(survey_id=survey_id)
        elif survey_tag:
            queryset = queryset.filter(survey_tag=survey_tag)

        if institution_type:
            queryset = queryset.filter(institution_type=institution_type)

        if to_:
            to_ = to_.split('-')
            to_year, to_month = to_[0], to_[1]
            queryset = queryset.filter(year__lte=to_year, month__lte=to_month)

        if from_:
            from_ = from_.split('-')
            from_year, from_month = from_[0], from_[1]
            queryset = queryset.filter(
                year__gte=from_year, month__gte=from_month)

        return queryset


