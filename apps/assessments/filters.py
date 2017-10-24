import django_filters
from .models import (
    AnswerGroup_Institution, AnswerGroup_Student,
    AnswerGroup_StudentGroup)


class AnswersSurveyTypeFilter(django_filters.FilterSet):
    survey_id = django_filters.CharFilter(name="questiongroup__survey__id")
    is_verified = django_filters.BooleanFilter(name='is_verified')
    class Meta:
        model = AnswerGroup_Institution
        fields = ['survey_id', 'is_verified']
