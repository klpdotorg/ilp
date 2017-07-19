from common.views import KLPListAPIView

from schools.serializers import (
    InstitutionListSerializer, InstitutionInfoSerializer
)
from schools.models import Institution


class InstitutionListView(KLPListAPIView):
    queryset = Institution.objects.all()
    serializer_class = InstitutionListSerializer


class InstitutionInfoView(KLPListAPIView):
    queryset = Institution.objects.all()
    serializer_class = InstitutionInfoSerializer
