from common.mixins import ILPStateMixin
from common.views import ILPViewSet


from assessments.models import Survey
from assessments.serializers import SurveySerializer
from assessments.filters import SurveyTagFilter


class SurveysViewSet(ILPViewSet, ILPStateMixin):
    '''Returns all surveys'''
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    filter_class = SurveyTagFilter
