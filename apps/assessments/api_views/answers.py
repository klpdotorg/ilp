import logging
from django.http import Http404, QueryDict
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from common.views import (ILPViewSet)
from assessments.models import (AnswerGroup_Institution, 
                            AnswerInstitution,
                            AnswerStudent,
                            AnswerGroup_Student)
from common.mixins import (ILPStateMixin, 
                           CompensationLogMixin,
                           AnswerUpdateModelMixin)
from assessments.serializers import (AnswerSerializer,
                                     AnswerGroupInstSerializer,
                                     AnswerGroupStudentSerializer,
                                     AnswerGroupStudentCreateSerializer,
                                     StudentAnswerSerializer)
from assessments.filters import AnswersSurveyTypeFilter
import json
from rest_framework.renderers import JSONRenderer

logger = logging.getLogger(__name__)

class AnswersStudentViewSet(NestedViewSetMixin, 
                                ILPViewSet, CompensationLogMixin,
                                AnswerUpdateModelMixin):
    ''' Viewset handling answers for a student '''
    queryset = AnswerStudent.objects.all()
    serializer_class = StudentAnswerSerializer

    def filter_queryset_by_parents_lookups(self, queryset):
        parents_query_dict = self.get_parents_query_dict()
        print("Arguments passed into view is: %s", parents_query_dict)
        # Remove all the unwanted params
        parents_query_dict.pop('student')
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

    def create(self, request, *args, **kwargs):
        #Create answergroup. Check if it exists first?? How to do this?
        print("Inside AnswersStudentViewSet", kwargs)
        data = request.data
        response_json={}
        if 'parent_lookup_answergroup' in kwargs:
            answergroup_id = kwargs['parent_lookup_answergroup']
            #This route has answergroup already defined/created
            if answergroup_id is not None:
                try:
                    answergroup_obj = AnswerGroup_Student.objects.get(id = answergroup_id)
                    serialized = AnswerGroupStudentSerializer(answergroup_obj, partial=True)
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
            print("Creating new answergroup", data)
            print("Kwargs is: ", kwargs)
            data['questiongroup']=kwargs['parent_lookup_questiongroup']
            data['student']=kwargs['parent_lookup_student']
            serializer = AnswerGroupStudentSerializer(data=data, partial=True)
            print("Checking validity of data")
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
        print("Inside create_answers", bulk)
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
            print("Bulk creation...")
            for answer in data:
                answer['answergroup']=answergroup_obj.id
            print("Finished setting answergroup")
            serializer = self.get_serializer(data=data, many=True)
            serializer.is_valid(raise_exception=True)
            # Invokes the CompensationLogMixin which sets double_entry correctly
            self.perform_bulk_create(serializer)
            return serializer.data


    def perform_bulk_create(self, serializer):
        return self.perform_create(serializer)

class AnswerGroupStudentsViewSet(NestedViewSetMixin, ILPViewSet):
    queryset = AnswerGroup_Student.objects.all()
    serializer_class = AnswerGroupStudentSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        # Insert questiongroup and institution info from kwargs into the data to pass
        # to the serializer
        data['questiongroup']=kwargs['parent_lookup_questiongroup']
        data['student']=kwargs['parent_lookup_student']
        serializer = AnswerGroupStudentSerializer(data=data)
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
        parents_query_dict.pop('survey')
        questiongroup_id = parents_query_dict['questiongroup']
        student_id = parents_query_dict['student']
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
            print("Creating new answergroup", data)
            data['questiongroup']=kwargs['parent_lookup_questiongroup']
            data['institution']=kwargs['parent_lookup_institution']
            serializer = AnswerGroupInstSerializer(data=data)
            print("Checking validity of data")
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
        if parents_query_dict:
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