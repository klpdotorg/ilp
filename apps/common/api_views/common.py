from common.models import (
    Language,
    AcademicYear,
    RespondentType
)
from rest_framework import generics
from common.serializers import (
    LanguageSerializer,
    RespondentTypeSerializer
)
from rest_framework import viewsets
from django.http import Http404
from common.serializers import AcademicYearSerializer
from common.pagination import LargeResultsSetPagination
from common.views import ILPListAPIView
from common.mixins import ILPStateMixin
from django.db.models import Q

class LanguagesListView(generics.ListAPIView):
    serializer_class = LanguageSerializer
    paginator = None

    def get_queryset(self):
        return Language.objects.all().order_by('name')


class RespondentTypeView(ILPListAPIView, ILPStateMixin):
    serializer_class = RespondentTypeSerializer

    def get_queryset(self):
        state = self.get_state()
        return RespondentType.objects.filter(active='AC').filter(
            Q(state_code__boundary=state) |
            Q(state_code=None)
        )

class BaseSchoolAggView(object):
    def get_aggregations(self, active_schools, academic_year):
        # active_schools = active_schools.filter(schoolextra__academic_year=academic_year)
        agg = {
            'num_schools': active_schools.count(),
            'moi': active_schools.values('moi').annotate(num=Count('moi')),
            'cat': active_schools.values('category').annotate(
                num_schools=Count('category'),
                num_boys=Sum('schoolextra__num_boys'),
                num_girls=Sum('schoolextra__num_girls')
            ),
            'mgmt': active_schools.values('mgmt').annotate(num=Count('mgmt')),
            'gender': active_schools.values('sex').annotate(num=Count('sex'))
        }

        active_institutions = active_schools.filter(institutionagg__academic_year=academic_year)
        agg['mt'] = active_institutions.values('institutionagg__mt').annotate(
            num_students=Sum('institutionagg__num'),
            num_boys=SumCase('institutionagg__num', when="gender='male'"),
            num_girls=SumCase('institutionagg__num', when="gender='female'")
        )

        for mt in agg['mt']:
            mt['name'] = mt['institutionagg__mt']
            del mt['institutionagg__mt']

        agg['num_boys'] = active_schools.filter(
            schoolextra__academic_year=academic_year
        ).aggregate(
            num_boys=Sum('schoolextra__num_boys')
        ).get('num_boys', 0)

        agg['num_girls'] = active_schools.filter(
            schoolextra__academic_year=academic_year
        ).aggregate(
            num_girls=Sum('schoolextra__num_girls')
        ).get('num_girls', 0)

        return agg


class AcademicYearView(generics.ListAPIView): 
    serializer_class = AcademicYearSerializer
    paginator = None

    def get_queryset(self):
        queryset = AcademicYear.objects.filter(active='AC')
        return queryset
