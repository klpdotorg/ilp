from common.models import Language
from rest_framework import generics
from common.serializers import LanguageSerializer


class LanguagesListView(generics.ListAPIView):
    serializer_class = LanguageSerializer
    paginator = None

    def get_queryset(self):
        return Language.objects.all()

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


