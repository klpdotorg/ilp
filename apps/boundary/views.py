from django.shortcuts import render
from boundary.serializers import BoundarySerializer
from boundary.models import Boundary
from common import views
from common import pagination
from common.mixins import CacheMixin

# Create your views here.

class Admin1sBoundary(views.KLPListAPIView):
    serializer_class=BoundarySerializer
    pagination_class=pagination.KLPPaginationSerializer
    def get_queryset(self):
        queryset = Boundary.objects.all()
        school_type = self.request.query_params.get('type', None)
        boundarytype='SD'
        if school_type is not None:
            queryset = queryset.filter(type=school_type)
        if school_type == 'pre':
            boundarytype='PD'
        queryset = queryset.filter(boundary_type=boundarytype).order_by()
        return queryset

'''class Admin1s(KLPListAPIView, CacheMixin):
    serializer_class=BoundarySerializer

    def get_queryset(self):
        institution_type = self.request.GET.get('school_type', 'all')
        qset = Boundary.objects.all_active()
        if institution_type == 'preschools':
            qset = qset.filter(hierarchy_id=13)'''
