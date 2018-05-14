import logging

from common.views import ILPListAPIView
from common.mixins import ILPStateMixin
from common.models import Status
from rest_framework.exceptions import ParseError

from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin

from django.db.models import Q
from django.db import IntegrityError

from assessments.models import (
    QuestionGroup, Question, QuestionGroup_Questions,
    AnswerGroup_Institution, QuestionGroup_Institution_Association,
    QuestionGroup_StudentGroup_Association, InstitutionImages,
    Survey, SurveyInstitutionAgg
)

from schools.models import (
    Institution, StudentGroup
)

from assessments.serializers import (
    QuestionGroupSerializer, QuestionSerializer,
    QuestionGroupQuestionSerializer,
    QuestionGroupInstitutionAssociationSerializer,
    QuestionGroupStudentGroupAssociationSerializer
)

logger = logging.getLogger(__name__)


class QuestionViewSet(ILPStateMixin, viewsets.ModelViewSet):
    '''Return all questions'''
    queryset = Question.objects.exclude(status=Status.DELETED)
    serializer_class = QuestionSerializer

    def get_queryset(self):
        survey_id = self.request.query_params.get('survey_id', None)
        if survey_id:
            questiongroups = QuestionGroup.objects.filter(
                survey_id=survey_id)
            question_ids = QuestionGroup_Questions.objects.filter(
                questiongroup__in=questiongroups).values_list(
                    'question_id', flat=True)
            return self.queryset.filter(id__in=question_ids)
        return self.queryset


class QuestionGroupQuestions(
        NestedViewSetMixin, ILPStateMixin, viewsets.ModelViewSet
):
    '''Returns all questions belonging to a questiongroup'''

    def get_queryset(self):
        parents_query_dict = self.get_parents_query_dict()
        questiongroup_id = parents_query_dict['questiongroup']
        question_list = QuestionGroup_Questions.objects\
            .filter(questiongroup_id=questiongroup_id)\
            .order_by('sequence')\
            .values_list('question', flat=True)
        return Question.objects.filter(id__in=question_list).order_by('key')

    def get_serializer_class(self):
        if self.request.method in ['GET', 'PUT']:
            return QuestionSerializer
        return QuestionGroupQuestionSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['questiongroup'] = \
            self.kwargs['parent_lookup_questiongroup']
        return context


class BoundaryQuestionGroupMapping(ILPListAPIView):
    ''' Returns all questiongroups under boundary ids. Boundary ids
    can be a comma separated list passed as params'''
    serializer_class = QuestionGroupInstitutionAssociationSerializer

    def get_queryset(self):
        boundary_ids = self.request.query_params.getlist('boundary_ids', [])
        print("boundary_ids received is: ", boundary_ids)
        queryset = QuestionGroup_Institution_Association.objects.exclude(
            status=Status.DELETED)
        result = queryset.filter(
                Q(institution__admin0_id__in=boundary_ids) |
                Q(institution__admin1_id__in=boundary_ids) |
                Q(institution__admin2_id__in=boundary_ids) |
                Q(institution__admin3_id__in=boundary_ids)
            )
        return result


class QuestionGroupViewSet(
        NestedViewSetMixin, ILPStateMixin, viewsets.ModelViewSet
):
    '''Returns all questiongroups belonging to a survey'''
    serializer_class = QuestionGroupSerializer

    def get_queryset(self):
        queryset = QuestionGroup.objects.exclude(status=Status.DELETED)
        survey_id = self.get_parents_query_dict()['survey_id']
        queryset = queryset.filter(survey_id=survey_id)
        return queryset

    def perform_destroy(self, instance):
        instance.status_id = Status.DELETED
        instance.save()

    def get_boundary_institution_ids(self, boundary_id):
        institution_ids = Institution.objects.filter(
            Q(admin0_id=boundary_id) |
            Q(admin1_id=boundary_id) |
            Q(admin2_id=boundary_id) |
            Q(admin3_id=boundary_id)
        ).distinct().values_list('id', flat=True)
        return institution_ids

    def get_boundary_studentgroup_ids(self, boundary_id):
        studentgroup_ids = StudentGroup.objects.filter(
            Q(institution_id__admin0_id=boundary_id) |
            Q(institution_id__admin1_id=boundary_id) |
            Q(institution_id__admin2_id=boundary_id) |
            Q(institution_id__admin3_id=boundary_id)
        ).distinct().values_list('id', flat=True)
        return studentgroup_ids

    @action(methods=['post'], detail=False, url_path='map-institution')
    def map_institution(self, request, *args, **kwargs):
        survey_id = self.get_parents_query_dict()['survey_id']
        survey_on = Survey.objects.get(id=survey_id).survey_on.pk
        if not survey_on == 'institution':
            raise ParseError('This survey is not an institution survey')
        questiongroup_ids = request.data.get('questiongroup_ids', [])
        institution_ids = request.data.get('institution_ids', [])
        boundary_ids = request.data.get('boundary_ids', [])
        if not institution_ids and not boundary_ids:
            raise ParseError('Please pass institution_ids OR boundary_ids')
        # Make a copy of the institution_ids param.
        list_of_institutions = list(institution_ids)
        # Fetch all institutions if a boundary_id is passed
        # and append to the list of institutions
        for boundary in boundary_ids:
            institutions_under_boundary = self.get_boundary_institution_ids(
                boundary
            )
            for institution in institutions_under_boundary:
                list_of_institutions.append(institution)
        data = []
        for questiongroup_id in questiongroup_ids:
            for institution_id in list_of_institutions:
                data.append({
                    'questiongroup': questiongroup_id,
                    'institution': institution_id,
                    'status': 'AC'
                })
        try:
            serializer = QuestionGroupInstitutionAssociationSerializer(
                data=data, many=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except IntegrityError as e:
            print("Integrity error")
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(methods=['post'], detail=False, url_path='map-studentgroup')
    def map_studentgroup(self, request, *args, **kwargs):
        survey_id = self.get_parents_query_dict()['survey_id']
        survey_on = Survey.objects.get(id=survey_id).survey_on.pk
        if not survey_on == 'studentgroup':
            raise ParseError('This survey is not a studengroup survey')
        questiongroup_ids = request.data.get('questiongroup_ids', [])
        studentgroup_ids = request.data.get('studentgroup_ids', [])
        boundary_ids = request.data.get('boundary_ids', [])
        if not studentgroup_ids and not boundary_ids:
            raise ParseError('Please pass studentgroup_ids OR boundary_ids')
        # Make a copy of the institution_ids param.
        list_of_studentgroups = list(studentgroups_ids)
        # Fetch all institutions if a boundary_id is passed and
        # append to the list of institutions
        for studentgroups in studentgroups_ids:
            studentgroups_under_boundary = self.get_boundary_studentgroup_ids(
                boundary)
            for studentgroup in studentgroups_under_boundary:
                list_of_studentgroups.append(studentgroup)
        data = []
        for questiongroup_id in questiongroup_ids:
            for studentgroup_id in list_of_studentgroups:
                data.append({
                    'questiongroup': questiongroup_id,
                    'studentgroup': studentgroup_id,
                    'status': 'AC'
                })
        serializer = QuestionGroupStudentGroupAssociationSerializer(
            data=data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(methods=['get'], detail=False, url_path='mappings')
    def mappings(self, request, *args, **kwargs):
        survey_id = self.get_parents_query_dict()['survey_id']
        survey_on = Survey.objects.get(id=survey_id).survey_on.pk
        institution_id = request.query_params.get('institution_id', None)

        if institution_id:
            institution_ids = [institution_id, ]
        else:
            boundary_id = request.query_params.get('boundary_id', None)
            institution_ids = self.get_boundary_institution_ids(boundary_id)

        response = []
        if survey_on == 'institution':
            res = {}
            qset = QuestionGroup_Institution_Association.objects.filter(
                institution_id__in=institution_ids,
                questiongroup__survey_id=survey_id)
            for qgroup_inst in qset:
                res = {
                    "id": qgroup_inst.institution_id,
                    "name": qgroup_inst.institution.name,
                    "assessment": {
                        "id": qgroup_inst.questiongroup_id,
                        "name": qgroup_inst.questiongroup.name,
                        "assessment-type": "institution"
                    }
                }
                response.append(res)
        else:
            res = {}
            sg_qset = QuestionGroup_StudentGroup_Association.\
                objects.filter(
                    studentgroup__institution_id__in=institution_ids,
                )
            for sgroup_inst in sg_qset:
                sg_name = sgroup_inst.studentgroup.name
                sg_id = sgroup_inst.studentgroup.id
                res[sg_name] = {
                    "id": sg_id,
                    "name": sg_name,
                    "assessment-type": "studentgroup"
                }
                for studgroup_qgroup in sg_qset.filter(
                        questiongroup__survey_id=survey_id):
                    qgroup = studgroup_qgroup.questiongroup
                    res[sg_name][qgroup.id] = {
                        "id": qgroup.id, "name": qgroup.name
                    }
                    response.append(res)
        return Response(response)


class QGroupStoriesInfoView(ILPListAPIView):
    """
    Returns total number of stories for the home page
    """
    def get(self, request, *args, **kwargs):
        return Response({
            'total_stories': AnswerGroup_Institution.objects.filter(
                questiongroup__survey__id=5).count(),
            'total_verified_stories': AnswerGroup_Institution.objects.filter(
                questiongroup__survey__id=5).filter(is_verified=True).count(),
            'total_images': InstitutionImages.objects.filter(
                answergroup__questiongroup__survey=5).count()
        })
