from rest_framework import viewsets
from schools.models import Staff
from schools.serializers import StaffSerializer
from rest_framework.response import Response

class StaffViewSet(viewsets.ModelViewSet):
    # permission_classes = (WorkUnderInstitutionPermission,)
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    # filter_class = TeacherFilter

    def list(self, request):
        queryset = Staff.objects.filter(
            status='AC',
            institution__pk=request.GET.get('institution', 0)
        )
        serializer = StaffSerializer(queryset, many=True)
        return Response(serializer.data)
