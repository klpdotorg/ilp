import logging
from django.http import Http404
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from common.views import (ILPViewSet)
from assessments.models import (AnswerGroup_Institution, 
                            AnswerInstitution)
from common.mixins import (ILPStateMixin, 
                           CompensationLogMixin,
                           AnswerUpdateModelMixin)
from assessments.serializers import (AnswerSerializer,
                                     AnswerGroupInstSerializer)
logger = logging.getLogger(__name__)

class AnswersViewSet(ILPViewSet):
    queryset = AnswerInstitution.objects.all()
    serializer_class = AnswerSerializer

    def create(self, request, *args, **kwargs):
        print("Inside AnswersCreate")
        pass

class AnswerGroupInstitutionViewSet(CompensationLogMixin, NestedViewSetMixin, ILPViewSet,
                                AnswerUpdateModelMixin):
    queryset = AnswerGroup_Institution.objects.all()
    serializer_class = AnswerGroupInstSerializer

    def create(self, request, *args, **kwargs):
        logger.info("Inside AnswersInstitutionViewSet")
        data = request.data
        # Insert questiongroup and institution info from kwargs into the data to pass
        # to the serializer
        data['questiongroup']=kwargs['parent_lookup_questiongroup']
        data['institution']=kwargs['parent_lookup_institution']
        serializer = AnswerGroupInstSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        # This invokes the CompensationLogMixin perform_create method
        self.perform_create(serializer)
        # todo self._assign_permissions(serializer.instance)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED, headers=headers
        )
    # M2M query returns duplicates. Overrode this function
    # from NestedViewSetMixin to implement the .distinct()

    def filter_queryset_by_parents_lookups(self, queryset):
        parents_query_dict = self.get_parents_query_dict()
        print("Arguments passed into view is: %s", parents_query_dict)
        questiongroup_id = parents_query_dict['questiongroup']
        institution_id = parents_query_dict['institution']
        answer_id = self.kwargs['pk']
        if parents_query_dict:
            if answer_id is not None:
                try:
                    print("Answer id is not none")
                    queryset = queryset.filter(institution=int(institution_id)
                    ).filter(questiongroup=int(questiongroup_id)).get(answers__id=answer_id)
                    print("Filtered via answer id: ")
                except ValueError:
                    print(("Exception while filtering queryset based on dictionary.Params: %s, Queryset is: %s"),
                        parents_query_dict, queryset)
                    logger.exception(
                        ("Exception while filtering queryset based on dictionary."
                        "Params: %s, Queryset is: %s"),
                        parents_query_dict, queryset)
                    raise Http404
            else:
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
        return queryset