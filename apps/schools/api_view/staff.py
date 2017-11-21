from rest_framework import viewsets

from schools.models import Staff
from schools.serializers import StaffSerializer


class StaffViewSet(viewsets.ModelViewSet):
    # permission_classes = (WorkUnderInstitutionPermission,)
    serializer_class = StaffSerializer
    # filter_class = TeacherFilter

    def get_queryset(self):
        institution = self.request.GET.get('institution', None)
        queryset = Staff.objects.filter(status="AC")

        if institution:
            queryset = queryset.filter(institution_id=institution)

        return queryset
