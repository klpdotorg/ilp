import logging
from common.mixins import ILPStateMixin
from boundary.models import ElectionBoundary
from boundary.serializers import ElectionBoundarySerializer
from rest_framework import viewsets

class AssemblyBoundariesViewSet(ILPStateMixin, viewsets.ModelViewSet):
    queryset = ElectionBoundary.objects.all()
    serializer_class = ElectionBoundarySerializer

    def get_queryset(self):
        return ElectionBoundary.objects.filter(const_ward_type__char_id="MLA")

class ParliamentBoundariesViewSet(ILPStateMixin, viewsets.ModelViewSet):
    queryset = ElectionBoundary.objects.all()
    serializer_class = ElectionBoundarySerializer

    def get_queryset(self):
        return ElectionBoundary.objects.filter(const_ward_type__char_id="MP")