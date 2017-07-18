from common.views import KLPListAPIView

from schools.serializers import InstitutionListSerializer
from schools.models import Institution


class InstitutionListView(KLPListAPIView):
    queryset = Institution.objects.all()
    serializer_class = InstitutionListSerializer
