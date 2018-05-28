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
        queryset = ElectionBoundary.objects.filter(const_ward_type__char_id="MLA").order_by('id')
        if state:
            queryset = queryset.filter(state_id=state.id)
        mapped = self.request.query_params.get('mapped')
        if mapped:
            queryset = queryset.filter(institution_mla__isnull = False).distinct('id')
        return queryset


class ParliamentBoundariesViewSet(ILPStateMixin, viewsets.ModelViewSet):
    queryset = ElectionBoundary.objects.all()
    serializer_class = ElectionBoundarySerializer

    def get_queryset(self):
        state = self.get_state()
        queryset = ElectionBoundary.objects.filter(const_ward_type__char_id="MP").order_by('id')
        if state:
            queryset = queryset.filter(state_id=state.id)
        mapped = self.request.query_params.get('mapped')
        if mapped:
            queryset = queryset.filter(institution_mp__isnull = False).distinct('id')
        return queryset

