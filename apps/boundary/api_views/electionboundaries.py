import logging
from common.mixins import ILPStateMixin
from boundary.models import ElectionBoundary
from boundary.serializers import ElectionBoundarySerializer
from rest_framework import viewsets


class AssemblyBoundariesViewSet(ILPStateMixin, viewsets.ModelViewSet):
    queryset = ElectionBoundary.objects.all()
    serializer_class = ElectionBoundarySerializer

    def get_queryset(self):
        state = self.get_state()
        queryset = ElectionBoundary.objects.filter(const_ward_type__char_id="MLA")
        if state:
            queryset = queryset.filter(state_id=state.id)
        return queryset


class ParliamentBoundariesViewSet(ILPStateMixin, viewsets.ModelViewSet):
    queryset = ElectionBoundary.objects.all()
    serializer_class = ElectionBoundarySerializer

    def get_queryset(self):
        state = self.get_state()
        queryset = ElectionBoundary.objects.filter(const_ward_type__char_id="MP")
        if state:
            queryset = queryset.filter(staet_id=state.id)
        return queryset

