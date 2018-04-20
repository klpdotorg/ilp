from rest_framework import viewsets
from django.http import Http404

from schools.models import Student
from schools.models import Institution

from schools.serializers import StudentSerializer

class ClusterStudentsViewSet(viewsets.ModelViewSet):
    serializer_class = StudentSerializer

    def get_queryset(self):
        cluster_id = self.request.GET.get('cluster_id', None)
        print("cluster:", cluster_id)
        #cluster_id = 718
        #print("cluster:", cluster_id)
        if cluster_id:
            cluster_institutions = Institution.objects.filter(admin3= cluster_id)
            institution_ids = cluster_institutions.values_list('id', flat=True)
            print(institution_ids)
            queryset = Student.objects.filter(institution_id__in=institution_ids)
            print(queryset)
        else:
            raise Http404
        return queryset
