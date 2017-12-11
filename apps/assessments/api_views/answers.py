import logging
from django.http import Http404
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework.generics import ListAPIView

from common.views import (ILPViewSet)
from assessments.models import (
    AnswerGroup_Institution, AnswerGroup_StudentGroup,
    AnswerGroup_Student, AnswerInstitution
)
from common.mixins import (ILPStateMixin, 
                           CompensationLogMixin,
                           AnswerUpdateModelMixin)
from assessments.serializers import (
    AnswerGroupInstSerializer, AnswerGroupStudentGroupSerializer,
    AnswerGroupStudentSerializer, AnswerSerializer
)
from assessments.filters import AnswersSurveyTypeFilter
import json
from rest_framework.renderers import JSONRenderer

logger = logging.getLogger(__name__)


# TODO: The following three view sets have not been
# linked to any URLs

class AnswerGroupInstViewSet(ILPViewSet, ILPStateMixin):
    queryset = AnswerGroup_Institution.objects.all()
    serializer_class = AnswerGroupInstSerializer


class AnswerGroupStudentGroupViewSet(ILPViewSet, ILPStateMixin):
    queryset = AnswerGroup_StudentGroup.objects.all()
    serializer_class = AnswerGroupStudentGroupSerializer


class AnswerGroupStudentViewSet(ILPViewSet, ILPStateMixin):
    queryset = AnswerGroup_Student.objects.all()
    serializer_class = AnswerGroupStudentSerializer


class SharedAssessmentsView(ListAPIView):
    """
        This view returns recent 6 assessments from our three assesment groups.
        The data is consumed in the ILP home page "Shared Stories" section.
    """

    def list(self, request, *args, **kwargs):
        inst = AnswerGroup_Institution.objects.all().order_by('-pk')[:6]
        st_group = AnswerGroup_StudentGroup.objects.all().order_by('-pk')[:6]
        st = AnswerGroup_Student.objects.all().order_by('-pk')[:6]

        return Response({
            'institutions': AnswerGroupInstSerializer(inst, many=True).data,
            'student_groups': AnswerGroupStudentGroupSerializer(
                st_group, many=True).data,
            'students': AnswerGroupStudentSerializer(st, many=True).data
        })

# class AnswersInstitutionViewSet(ILPViewSet,
#                                 CompensationLogMixin,
#                                 AnswerUpdateModelMixin):
#     ''' Viewset handling answers for an institution '''
#     queryset = AnswerInstitution.objects.all()
#     serializer_class = AnswerSerializer

#     def get_queryset(self):
#         return AnswerInstitution.objects.filter(answergroup_id=self.kwargs['parent_lookup_answergroup'])


# class AnswerGroupInstitutionViewSet(NestedViewSetMixin, ILPViewSet):
#     queryset = AnswerGroup_Institution.objects.all()
#     serializer_class = AnswerGroupInstSerializer
    
#     def create(self, request, *args, **kwargs):
#         print("Inside AnswersInstitutionViewSet")
#         data = request.data
#         # Insert questiongroup and institution info from kwargs into the data to pass
#         # to the serializer
#         data['questiongroup']=kwargs['parent_lookup_questiongroup']
#         data['institution']=kwargs['parent_lookup_institution']
#         serializer = AnswerGroupInstSerializer(data=data)
#         serializer.is_valid(raise_exception=True)
#         answergroup = serializer.save()
#         # This invokes the CompensationLogMixin perform_create method
#         # self.perform_create(serializer)
#         # todo self._assign_permissions(serializer.instance)
#         headers = self.get_success_headers(serializer.data)
#         # print("Serializer returned DATA: ", serializer.data)
#         return Response(
#             serializer.data,
#             status=status.HTTP_201_CREATED, headers=headers
#         )


#     # M2M query returns duplicates. Overrode this function
#     # from NestedViewSetMixin to implement the .distinct()

#     def filter_queryset_by_parents_lookups(self, queryset):
#         parents_query_dict = self.get_parents_query_dict()
#         print("Arguments passed into view is: %s", parents_query_dict)
#         questiongroup_id = parents_query_dict['questiongroup']
#         institution_id = parents_query_dict['institution']
#         # answergroup_id = self.kwargs['pk']
#         # print("Answer group id is: ", answergroup_id)
#         if parents_query_dict:
#             # if answergroup_id is not None:
#             #     try:
#             #         queryset = queryset.get(id=int(answergroup_id))
#             #         print("got queryset", queryset.id)
#             #     except ValueError:
#             #         print(("Exception while filtering queryset based on dictionary.Params: %s, Queryset is: %s"),
#             #             parents_query_dict, queryset)
#             #         logger.exception(
#             #             ("Exception while filtering queryset based on dictionary."
#             #             "Params: %s, Queryset is: %s"),
#             #             parents_query_dict, queryset)
#             #         raise Http404
#             # else:
#             try:
#                 queryset = queryset.filter(institution=int(institution_id)
#                 ).filter(questiongroup=int(questiongroup_id)).filter(id=self.kwargs['pk']).order_by().distinct('id')
#             except ValueError:
#                 print(("Exception while filtering queryset based on dictionary.Params: %s, Queryset is: %s"),
#                     parents_query_dict, queryset)
#                 logger.exception(
#                     ("Exception while filtering queryset based on dictionary."
#                     "Params: %s, Queryset is: %s"),
#                     parents_query_dict, queryset)
#                 raise Http404
#         else:
#             print ("No query dict passed")
        
#         return queryset

class AnswersInstitutionViewSet( NestedViewSetMixin, 
                                ILPViewSet, CompensationLogMixin,
                                AnswerUpdateModelMixin):
    ''' Viewset handling answers for an institution '''
    queryset = AnswerInstitution.objects.all()
    serializer_class = AnswerSerializer

    def filter_queryset_by_parents_lookups(self, queryset):
        parents_query_dict = self.get_parents_query_dict()
        print("Arguments passed into view is: %s", parents_query_dict)
        # Remove all the unwanted params
        parents_query_dict.pop('institution')
        parents_query_dict.pop('questiongroup')
        parents_query_dict.pop('survey')
        if parents_query_dict:
            try:
                queryset = queryset.filter(**parents_query_dict).order_by().distinct('id')
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
    # def get_queryset(self):
    #     print("Kwargs is: ", self.kwargs)
    #     return AnswerInstitution.objects.filter(id=self.kwargs['pk'])

    def create(self, request, *args, **kwargs):
        #Create answergroup. Check if it exists first?? How to do this?
        print("Inside AnswersInstitutionViewSet", kwargs)
        data = request.data
        response_json={}
        if 'parent_lookup_answergroup' in kwargs:
            answergroup_id = kwargs['parent_lookup_answergroup']
            #This route has answergroup already defined/created
            if answergroup_id is not None:
                try:
                    answergroup_obj = AnswerGroup_Institution.objects.get(id = answergroup_id)
                    serialized = AnswerGroupInstSerializer(answergroup_obj)
                    for key, value in serialized.data.items():
                        print("Key is: ", key)
                        print("Value is: ", value)
                        response_json[key] = value
                    print(response_json)
                    print("Answer group already exists", response_json)
                except DoesNotExist:
                    print("Answergroup does not exist")
                    raise Http404
        else:
            # Create new answer group
            # Insert questiongroup and institution info from kwargs into the data to pass
            # to the serializer
            data['questiongroup']=kwargs['parent_lookup_questiongroup']
            data['institution']=kwargs['parent_lookup_institution']
            serializer = AnswerGroupInstSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            answergroup_obj=serializer.save()
            for key, value in serializer.data.items():
                print("Key is: ", key)
                print("Value is: ", value)
                response_json[key] = value
            print(response_json)
        # Create answers
        print("Creating answers", response_json)
        answer_serializer_data = self.create_answers(request, answergroup_obj)
        headers = self.get_success_headers(answer_serializer_data)
        response_json['answers'] = answer_serializer_data
        return Response(response_json, status=status.HTTP_201_CREATED, headers=headers)
        
    def create_answers(self, request, answergroup_obj):
        bulk = isinstance(request.data['answers'], list)
        if not bulk:
            data = request.data['answers']
            data['answergroup'] = answergroup_obj
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            # Invokes the CompensationLogMixin which sets double_entry correctly
            self.perform_create(serializer)
            return serializer.data
        else:
            data = request.data['answers']
            for answer in data:
                answer['answergroup']=answergroup_obj.id
            serializer = self.get_serializer(data=data, many=True)
            serializer.is_valid(raise_exception=True)
            # Invokes the CompensationLogMixin which sets double_entry correctly
            self.perform_bulk_create(serializer)
            return serializer.data


    def perform_bulk_create(self, serializer):
        return self.perform_create(serializer)

class AnswerGroupInstitutionViewSet(NestedViewSetMixin, ILPViewSet):
    queryset = AnswerGroup_Institution.objects.all()
    serializer_class = AnswerGroupInstSerializer
    
    def create(self, request, *args, **kwargs):
        data = request.data
        # Insert questiongroup and institution info from kwargs into the data to pass
        # to the serializer
        data['questiongroup']=kwargs['parent_lookup_questiongroup']
        data['institution']=kwargs['parent_lookup_institution']
        serializer = AnswerGroupInstSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        answergroup = serializer.save()
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
        # answergroup_id = self.kwargs['pk']
        # print("Answer group id is: ", answergroup_id)
        if parents_query_dict:
            # if answergroup_id is not None:
            #     try:
            #         queryset = queryset.get(id=int(answergroup_id))
            #         print("got queryset", queryset.id)
            #     except ValueError:
            #         print(("Exception while filtering queryset based on dictionary.Params: %s, Queryset is: %s"),
            #             parents_query_dict, queryset)
            #         logger.exception(
            #             ("Exception while filtering queryset based on dictionary."
            #             "Params: %s, Queryset is: %s"),
            #             parents_query_dict, queryset)
            #         raise Http404
            # else:
            try:
                queryset = queryset.filter(institution=int(institution_id)
                ).filter(questiongroup=int(questiongroup_id)).filter(id=self.kwargs['pk']).order_by().distinct('id')
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
