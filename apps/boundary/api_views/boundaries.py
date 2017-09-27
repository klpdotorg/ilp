import logging
from django.db.models import Q
from boundary.serializers import (
    BoundarySerializer, BoundaryWithParentSerializer, BoundaryTypeSerializer
)
from boundary.filters import BoundaryFilter
from boundary.models import Boundary, BoundaryType, BoundaryHierarchy
from common.views import ILPListAPIView, ILPDetailAPIView
from common.pagination import ILPPaginationSerializer
from common.models import InstitutionType, Status
from common.mixins import ILPStateMixin
from rest_framework import viewsets
from rest_framework.exceptions import APIException

logger = logging.getLogger(__name__)


class BoundaryViewSet(ILPStateMixin, viewsets.ModelViewSet):
    '''Boundary endpoint'''
    queryset = Boundary.objects.all()
    serializer_class = BoundarySerializer
    filter_class = BoundaryFilter
    def get_queryset(self):
        state = self.get_state()
        if state:
            boundaries = Boundary.objects.filter(Q(parent=state) |
                                             Q(parent__parent=state) |
                                             Q(parent__parent__parent=state))
        else:
            boundaries = Boundary.objects.all()
        return boundaries

class BoundaryTypeViewSet(viewsets.ModelViewSet):
    queryset = BoundaryType.objects.all()
    serializer_class = BoundaryTypeSerializer
