import django_filters

from rest_framework.filters import BaseFilterBackend

from assessments.models import SurveyBoundaryAgg

from .models import Boundary


class BoundaryFilter(django_filters.FilterSet):
    type = django_filters.CharFilter(name="type__char_id")
    boundary_type = django_filters.CharFilter(name="boundary_type__char_id")

    class Meta:
        model = Boundary
        fields = ['type', 'parent', 'boundary_type']


class BoundarySurveyFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        survey_id = request.query_params.get('survey_id', None)
        if survey_id:
            boundary_ids = SurveyBoundaryAgg.objects.filter(
                survey_id=survey_id).distinct('boundary_id')\
                .values_list('boundary_id', flat=True)
            return queryset.filter(id__in=boundary_ids)

        survey_tag = request.query_params.get('survey_tag', None)
        if survey_tag:
            boundary_ids = SurveyBoundaryAgg.objects.filter(
                survey_tag=survey_tag).distinct('boundary_id')\
                .values_list('boundary_id', flat=True)
            return queryset.filter(id__in=boundary_ids)
        return queryset
