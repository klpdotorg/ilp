from django.shortcuts import render
from boundary.serializers import BoundarySerializer, BoundaryWithParentSerializer
from boundary.models import Boundary, BoundaryType
from common import views, pagination
from common.models import InstitutionType, Status
from common.mixins import CacheMixin
from django.db.models import Q
import pdb

# Create your views here.

class Admin1sBoundary(views.KLPListAPIView):
    serializer_class=BoundarySerializer
    pagination_class=pagination.KLPPaginationSerializer
    def get_queryset(self):
        state = self.kwargs.get('state','None');
        queryset = Boundary.objects.filter(Q(parent=state))
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
        queryset = Boundary.objects.all().filter(Q(boundary_type=BoundaryType.SCHOOL_BLOCK)|Q(boundary_type=BoundaryType.PRESCHOOL_PROJECT))
        school_type = self.request.query_params.get('school_type', None)
        if school_type is not None:
            boundarytype=BoundaryType.SCHOOL_BLOCK
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

class Admin2sInsideAdmin1(views.KLPListAPIView):
    ''' Returns a list of all blocks/projects inside a given district id '''
    serializer_class=BoundarySerializer

    def get_queryset(self):
        parent_district_id=self.kwargs.get('id',0)
        print("Parent district id is: ", parent_district_id)
        result= Boundary.objects.all().filter(
            parent=parent_district_id,status='AC'
        )
        print("REsult is: ", result)
        return result

class Admin3sInsideAdmin1(views.KLPListAPIView):
    '''Returns a list of all clusters/circles inside a given pre or primary district '''
    serializer_class=BoundarySerializer

    def get_queryset(self):
        parent_district_id=self.kwargs.get('id',0)
        return Boundary.objects.all().filter(parent__parent=parent_district_id,status='AC')

class Admin3sInsideAdmin2(views.KLPListAPIView):
    ''' Returns a list of all clusters/circles inside a given block/project id '''
    serializer_class=BoundarySerializer
    def get_queryset(self):
        admin2_id=self.kwargs.get('id',0)
        return Boundary.objects.all().filter(
            parent=admin2_id,status='AC'
        )

#Note: need to add cachemixin later in the params. COmmenting because of error in console about cache setting not enabled
class AdminDetails(views.KLPDetailAPIView):
    """Returns details for a particular admin level

    bbox -- Bounding box to search within e.g. 77.349415,12.822471,77.904224,14.130930
    """
    serializer_class = BoundaryWithParentSerializer
    bbox_filter_field = 'boundarycoord__coord'
    lookup_url_kwarg = 'id'

    def get_queryset(self):
        return Boundary.objects.all_active()