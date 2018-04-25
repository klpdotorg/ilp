import logging
import json
import random

from PIL import Image
from base64 import b64decode

from django.http import Http404, QueryDict
from django.core.files.base import ContentFile
from django.conf import settings

from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework.generics import ListAPIView
from rest_framework.renderers import JSONRenderer

from common.views import (ILPViewSet)
from common.mixins import (
    ILPStateMixin, CompensationLogMixin, AnswerUpdateModelMixin
)
from common.mixins import (
    ILPStateMixin, CompensationLogMixin,
    AnswerUpdateModelMixin
)

from assessments.models import (
    Survey, AnswerStudentGroup,
    AnswerGroup_Institution, AnswerInstitution,
    AnswerStudent, AnswerGroup_Student,
    AnswerGroup_StudentGroup, InstitutionImages
)
from assessments.serializers import (
    AnswerSerializer, AnswerGroupStudentSerializer, 
    AnswerGroupStudentGroupSerializer, AnswerGroupInstSerializer,
    AnswerGroupInstitutionSerializer, AnswerInstitutionSerializer,
    AnswerStudentSerializer, AnswerStudentGroupSerializer
)

from permissions.permissions import AppPostPermissions
from users.models import User
from dateutil.parser import parse as date_parse

logger = logging.getLogger(__name__)


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


class ShareYourStoryAPIView(ILPViewSet, CompensationLogMixin):
    serializer_class = AnswerSerializer
    permission_classes = (AppPostPermissions,)
    
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['questiongroup'] = 6
        data['institution'] = kwargs['schoolid']        
        user = User.objects.get(mobile_no=request.user)
        date_of_visit = date_parse(
            request.POST.get('date_of_visit', ''), yearfirst=True)
        answergroup = {
            "institution": kwargs['schoolid'],
            "questiongroup": 6,
            "group_value": user.email,
            "created_by": user.id,
            "comments": data['comments'],
            "date_of_visit": date_of_visit,
            "respondent_type": "VR",
            "status": "AC"
        }
        serializer = AnswerGroupInstSerializer(data=answergroup)
        serializer.is_valid()
        answergroup_obj=serializer.save()
        response_json={}
        # Form the response JSON with AnwerGroup details
        for key, value in serializer.data.items():
            response_json[key] = value
        # Now work on Answers. Modify input data to suit serializer format
        answers=[]
        for key,value in data.items():
            answer={}
            if(key.startswith("question_")):
                qn, id = key.split("_")
                answer["question"]=int(id)
                answer["answer"]=value
                answers.append(answer)
        
        answergroup["answers"]=answers
                
        # Create answers
        answer_serializer_data = self.create_answers(request,answers, answergroup_obj)
        headers = self.get_success_headers(answer_serializer_data)
        response_json['answers'] = answer_serializer_data

        # Store images
        print("Storing images")
        images = request.POST.getlist('images[]')
        for image in images:
            image_type, data = image.split(',')
            image_data = b64decode(data)
            file_name = '{}_{}.png'.format(kwargs['schoolid'], random.randint(0, 9999))

            simage = InstitutionImages(
                answergroup=answergroup_obj,
                filename=file_name,
                image=ContentFile(image_data, file_name)
            )
            simage.save()

            try:
                import os
                pil_image = Image.open(simage.image)
                pil_image.thumbnail((128, 128), )

                thumb_path = os.path.join(
                    settings.MEDIA_ROOT, 'sys_images', 'thumb', file_name)
                pil_image.save(open(thumb_path, 'w'))
            except Exception as e:
                print(e)

        return Response(response_json, status=status.HTTP_201_CREATED, headers=headers)
      

    def create_answers(self, request, answers, answergroup_obj):
        bulk = isinstance(answers, list)
        if not bulk:
            data = answers
            data['answergroup'] = answergroup_obj
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            # Invokes the CompensationLogMixin which sets double_entry correctly
            print("Logged in user is: ", self.request.user)
            self.perform_create(serializer)
            return serializer.data
        else:
            data = answers
            for answer in data:
                answer['answergroup']=answergroup_obj.id
            serializer = self.get_serializer(data=data, many=True)
            serializer.is_valid(raise_exception=True)
            # Invokes the CompensationLogMixin which sets double_entry correctly
            self.perform_bulk_create(serializer)
            return serializer.data

    def perform_bulk_create(self, serializer):
        return self.perform_create(serializer)


class AnswerGroupViewSet(NestedViewSetMixin, viewsets.ModelViewSet):

    def get_model(self, survey_id):
        survey_on = Survey.objects.get(id=survey_id).survey_on.pk
        if survey_on == 'institution':
            return AnswerGroup_Institution
        elif survey_on == 'studentgroup':
            return AnswerGroup_StudentGroup
        return AnswerGroup_Student

    def create(self, request, *args, **kwargs):
        parent_query_dict = self.get_parents_query_dict()
        questiongroup_id = parent_query_dict['questiongroup_id']

        data = request.data
        data['questiongroup'] = questiongroup_id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)    

    def get_serializer_class(self):
        parent_query_dict = self.get_parents_query_dict()
        survey_id = parent_query_dict['survey_id']
        survey_on = Survey.objects.get(id=survey_id).survey_on.pk
        if survey_on == 'institution':
            return AnswerGroupInstitutionSerializer
        elif survey_on == 'studentgroup':
            return AnswerGroupStudentGroupSerializer
        return AnswerGroupStudentSerializer

    def get_queryset(self):
        parent_query_dict = self.get_parents_query_dict()
        survey_id = parent_query_dict['survey_id']
        questiongroup_id = parent_query_dict['questiongroup_id']
        AnswerGroupModel = self.get_model(survey_id)
        return AnswerGroupModel.objects.filter(
            questiongroup_id=questiongroup_id)


class AnswerViewSet(NestedViewSetMixin, viewsets.ModelViewSet):

    def get_model(self, survey_id):
        survey_on = Survey.objects.get(id=survey_id).survey_on.pk
        if survey_on == 'institution':
            return AnswerInstitution
        elif survey_on == 'studentgroup':
            return AnswerStudentGroup
        return AnswerStudent

    def get_serializer_class(self):
        parent_query_dict = self.get_parents_query_dict()
        survey_id = parent_query_dict['survey_id']
        survey_on = Survey.objects.get(id=survey_id).survey_on.pk
        if survey_on == 'institution':
            return AnswerInstitutionSerializer
        elif survey_on == 'studentgroup':
            return AnswerStudentGroupSerializer
        return AnswerStudentSerializer

    def get_queryset(self):
        parent_query_dict = self.get_parents_query_dict()
        survey_id = parent_query_dict['survey_id']
        answergroup_id = parent_query_dict['answergroup_id']
        AnswerModel = self.get_model(survey_id)
        return AnswerModel.objects.filter(answergroup_id=answergroup_id)

    def create(self, request, *args, **kwargs):
        parent_query_dict = self.get_parents_query_dict()
        answergroup_id = parent_query_dict['answergroup_id']
        data = request.data
        ans_data = []
        for datum in data:
            datum['answergroup'] = answergroup_id
            ans_data.append(datum)
        serializer = self.get_serializer(data=ans_data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(answergroup_id=answergroup_id)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def put(self, request, *args, **kwargs):
        parent_query_dict = self.get_parents_query_dict()
        survey_id = parent_query_dict['survey_id']
        answergroup_id = parent_query_dict['answergroup_id']
        data = request.data
        ans_data = []
        answer_ids = []
        for datum in data:
            answer_ids.append(datum['id'])
            datum['answergroup'] = answergroup_id
            ans_data.append(datum)
        ans_qset = self.get_model(survey_id).objects.filter(id__in=answer_ids)
        serializer = self.get_serializer(ans_qset, data=ans_data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(answergroup_id=answergroup_id)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)