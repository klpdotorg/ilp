import django_filters

from rest_framework.filters import BaseFilterBackend

from assessments.models import SurveyInstitutionAgg
from schools.models import Student, StudentGroup


class StudentFilter(django_filters.FilterSet):

    class Meta:
        model = Student
        fields = ['first_name', 'middle_name', 'last_name', 'status']


class StudentGroupFilter(django_filters.FilterSet):

    class Meta:
        model = StudentGroup
        fields = ['name', 'section', 'status', 'group_type']


class InstitutionSurveyFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        survey_id = request.query_params.get('survey_id', None)
        survey_tag = request.query_params.get('survey_tag', None)

        if survey_id:
            institution_ids = SurveyInstitutionAgg.objects\
                .filter(survey_id=survey_id)\
                .distinct('institution_id')\
                .values_list('institution_id', flat=True)
            return queryset.filter(id__in=institution_ids)

        if survey_tag:
            institution_ids = SurveyInstitutionAgg.objects\
                .filter(survey_tag=survey_tag)\
                .distinct('institution_id')\
                .values_list('institution_id', flat=True)
            return queryset.filter(id__in=institution_ids)
        return queryset
