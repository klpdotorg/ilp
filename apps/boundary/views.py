from django.shortcuts import render
from boundary.serializers import BoundarySerializer
from boundary.models import Boundary, BoundaryType
from common import views, pagination
from common.models import InstitutionType
from common.mixins import CacheMixin
from django.db.models import Q

# Create your views here.

class Admin1sBoundary(views.KLPListAPIView):
    serializer_class=BoundarySerializer
    pagination_class=pagination.KLPPaginationSerializer
    def get_queryset(self):
        queryset = Boundary.objects.all()
        school_type = self.request.query_params.get('school_type', None)
        boundarytype=BoundaryType.SCHOOL_DISTRICT
        if school_type is not None:
            queryset = queryset.filter(type=school_type)
            if school_type == InstitutionType.PRESCHOOL:
                boundarytype=BoundaryType.PRESCHOOL_DISTRICT
            queryset = queryset.filter(boundary_type__exact=boundarytype)
        else:
            queryset = queryset.filter(Q(boundary_type=BoundaryType.SCHOOL_DISTRICT)| Q(boundary_type=BoundaryType.PRESCHOOL_DISTRICT))
        return queryset

class Admin2sBoundary(views.KLPListAPIView):
    serializer_class=BoundarySerializer
    pagination_class=pagination.KLPPaginationSerializer
    def get_queryset(self):
        queryset = Boundary.objects.all().filter(Q(boundary_type='SB')|Q(boundary_type='PP'))
        school_type = self.request.query_params.get('school_type', None)
        boundarytype=BoundaryType.SCHOOL_BLOCK
        if school_type is not None:
            queryset = queryset.filter(type=school_type)
            if school_type == InstitutionType.PRESCHOOL:
                boundarytype=BoundaryType.PRESCHOOL_PROJECT
            queryset = queryset.filter(boundary_type__exact=boundarytype)
        return queryset

class Admin3sBoundary(views.KLPListAPIView):
    serializer_class=BoundarySerializer
    pagination_class=pagination.KLPPaginationSerializer
    def get_queryset(self):
        queryset = Boundary.objects.all()
        school_type = self.request.query_params.get('school_type', None)
        boundarytype=BoundaryType.SCHOOL_CLUSTER
        if school_type is not None:
            queryset = queryset.filter(type=school_type)
            if school_type == InstitutionType.PRESCHOOL:
                boundarytype=BoundaryType.PRESCHOOL_CIRCLE
            queryset = queryset.filter(boundary_type__exact=boundarytype)
        else:
            queryset = queryset.filter(Q(boundary_type=BoundaryType.SCHOOL_CLUSTER)| Q(boundary_type=BoundaryType.PRESCHOOL_CIRCLE))
        return queryset
