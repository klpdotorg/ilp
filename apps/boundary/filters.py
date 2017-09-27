import django_filters
from .models import (
    Boundary)


class BoundaryFilter(django_filters.FilterSet):
    type = django_filters.CharFilter(name="type__char_id")
    boundary_type = django_filters.CharFilter(name="boundary_type__char_id")
    class Meta:
        model = Boundary
        fields = ['type', 'parent', 'boundary_type']
