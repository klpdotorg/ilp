import logging
from django.http import Http404
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from common.views import (ILPViewSet)
from assessments.models import (AnswerGroup_Institution, 
                            AnswerInstitution)
from common.mixins import ILPStateMixin
from assessments.serializers import (AnswerSerializer,
                                     AnswerGroupInstSerializer)
logger = logging.getLogger(__name__)

class AnswersInstitutionViewSet(NestedViewSetMixin, ILPViewSet):
    queryset = AnswerGroup_Institution.objects.all()
    serializer_class = AnswerGroupInstSerializer

    # M2M query returns duplicates. Overrode this function
    # from NestedViewSetMixin to implement the .distinct()

    def filter_queryset_by_parents_lookups(self, queryset):
        parents_query_dict = self.get_parents_query_dict()
        print("Arguments passed into view is: %s", parents_query_dict)
        questiongroup_id = parents_query_dict['questiongroup']
        institution_id = parents_query_dict['institution']
        if parents_query_dict:
            try:
                queryset = queryset.filter(institution=int(institution_id)
                ).filter(questiongroup=int(questiongroup_id)).order_by().distinct('id')
            except ValueError:
                print(("Exception while filtering queryset based on dictionary.Params: %s, Queryset is: %s"),
                     parents_query_dict, queryset)
                logger.exception(
                    ("Exception while filtering queryset based on dictionary."
                     "Params: %s, Queryset is: %s"),
                    parents_query_dict, queryset)
                raise Http404
        else:
            print ("No query dict passed")
        return queryset.order_by('id')