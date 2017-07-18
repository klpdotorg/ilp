from rest_framework.generics import ListAPIView
from schools.serializers import InstitutionListSerializer
from schools.models import Institution


class InstitutionListView(ListAPIView):
    serializer_class = InstitutionListSerializer

    def get_queryset(self):
        qset = Institution.objects.all()
        return qset
