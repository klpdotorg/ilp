import logging

from common.views import ILPListAPIView
from common.mixins import ILPStateMixin
from common.models import Status
from rest_framework.exceptions import ParseError, ValidationError

from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin

from django.db.models import Q
from django.db import IntegrityError
from django.shortcuts import get_object_or_404

from permissions.permissions import (
    HasAssignPermPermission
)
from assessments.models import (
    QuestionGroup, Question, QuestionGroup_Questions,
    AnswerGroup_Institution, QuestionGroup_Institution_Association,
    QuestionGroup_StudentGroup_Association, InstitutionImages,
    Survey, SurveyInstitutionAgg, QuestionType, SurveyType
)

from schools.models import (
    Institution, StudentGroup
)

from assessments.serializers import (
    QuestionGroupSerializer, QuestionSerializer,
    QuestionGroupQuestionSerializer,
    QuestionGroupInstitutionAssociationSerializer,
    QuestionGroupStudentGroupAssociationSerializer,
    QuestionGroupStudentGroupAssociationCreateSerializer,
    QuestionTypeSerializer,
    QuestionGroupInstitutionAssociationCreateSerializer,
    SurveyTypeSerializer
)


logger = logging.getLogger(__name__)


class QuestionViewSet(ILPStateMixin, viewsets.ModelViewSet):
    '''Return all questions'''
    queryset = Question.objects.exclude(status=Status.DELETED)
    serializer_class = QuestionSerializer
    permission_classes = (HasAssignPermPermission,)

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


class QuestionTypeListView(ILPListAPIView):
    serializer_class = QuestionTypeSerializer

    def get_queryset(self):
        return QuestionType.objects.all()


class SurveyTypeListView(ILPListAPIView):
    serializer_class = SurveyTypeSerializer

    def get_queryset(self):
        return SurveyType.objects.all()


class QuestionGroupQuestions(
        NestedViewSetMixin, ILPStateMixin, viewsets.ModelViewSet
):
    '''Returns all questions belonging to a questiongroup'''
    serializer_class = QuestionGroupQuestionSerializer
    permission_classes = (HasAssignPermPermission,)

    def get_queryset(self):
        """ 
        Returns QuestionGroup_Question object in sequence order.
        """
        parents_query_dict = self.get_parents_query_dict()
        questiongroup_id = parents_query_dict['questiongroup']
        return QuestionGroup_Questions.objects\
            .filter(questiongroup_id=questiongroup_id)\
            .order_by('sequence')

    def get_object(self):
        """
        Returns QuestionGroup_Question object.
        When PUT returns QuestionGroup_Question.question
        """
        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(queryset, question=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        if self.request.method in ['PUT', ]:
            return obj.question
        return obj

    def list(self, request, *args, **kwargs):
        """
        Makes question list from QuestionGroup_Question and
        returns question objects. Ideally it should return QG_question objects.
        But can't change it now(Konnect uses).
        """
        question_list = self.get_queryset().values_list('question', flat=True)
        queryset = Question.objects.filter(id__in=question_list).order_by('key')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer_class()(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def sequence(self, request, *args, **kwargs):
        """
        Returns QuestionGroup_Question object order by sequence.
        """
        queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = QuestionGroupQuestionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = QuestionGroupQuestionSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer_class(self):
        """
        GET all & PUT uses QuestionSerializer by default.
        For GET all - use /sequences/ endpoint, if you need sequence field.
        GET /:id/ see retrive method.
        POST uses QuestionGroupQuestionSerializer.
        """
        if self.request.method in ['PUT', 'GET', ]:
            return QuestionSerializer
        return QuestionGroupQuestionSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = QuestionGroupQuestionSerializer(instance)
        return Response(serializer.data)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['questiongroup'] = \
            self.kwargs['parent_lookup_questiongroup']
        return context


class BoundaryQuestionGroupMapping(ILPListAPIView):
    ''' Returns all questiongroups under boundary ids. Boundary ids
    can be a comma separated list passed as params'''
    
    def list(self, request, *args, **kwargs):
        boundary_ids = self.request.query_params.getlist('boundary_ids', [])
        result = []
        qg_inst_qs = QuestionGroup_Institution_Association.objects.exclude(
            status=Status.DELETED
        ).filter(
            questiongroup__status=Status.ACTIVE
        ).filter(
            Q(institution__admin0_id__in=boundary_ids) |
            Q(institution__admin1_id__in=boundary_ids) |
            Q(institution__admin2_id__in=boundary_ids) |
            Q(institution__admin3_id__in=boundary_ids)
        ).distinct('questiongroup__id')
        qg_stud_qs = QuestionGroup_StudentGroup_Association.objects.exclude(
            status=Status.DELETED
        ).filter(
            questiongroup__status=Status.ACTIVE
        ).filter(
            Q(studentgroup__institution__admin0_id__in=boundary_ids) |
            Q(studentgroup__institution__admin1_id__in=boundary_ids) |
            Q(studentgroup__institution__admin2_id__in=boundary_ids) |
            Q(studentgroup__institution__admin3_id__in=boundary_ids)
        ).distinct('questiongroup__id')
        qg_inst_data = QuestionGroupInstitutionAssociationSerializer(
            qg_inst_qs, many=True
        )
        qg_stud_data = QuestionGroupStudentGroupAssociationSerializer(
            qg_stud_qs, many=True
        )
        result += qg_inst_data.data
        result += qg_stud_data.data
        return Response(result)


class QuestionGroupViewSet(
        NestedViewSetMixin, ILPStateMixin, viewsets.ModelViewSet
):
    '''Returns all questiongroups belonging to a survey'''
    serializer_class = QuestionGroupSerializer
    permission_classes = (HasAssignPermPermission,)

    def get_queryset(self):
        queryset = QuestionGroup.objects.exclude(status=Status.DELETED)
        survey_id = self.get_parents_query_dict()['survey']
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

    def get_institution_studentgroup_ids(self, institution):
        studentgroup_ids = StudentGroup.objects.filter(
            Q(institution_id=institution)
        ).distinct().values_list('id', flat=True)
        return studentgroup_ids

    def format_input_data(self, questiongroup_id, institution_id):
        return {
            'questiongroup': questiongroup_id,
            'institution': institution_id,
            'status': 'AC'
            }

    @action(methods=['post'], detail=False, url_path='map-institution')
    def map_institution(self, request, *args, **kwargs):
        survey_id = self.get_parents_query_dict()['survey']
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

        for questiongroup_id in questiongroup_ids:
            data = [self.format_input_data(questiongroup_id,institution_id) for institution_id in list_of_institutions]
        
        serializer = QuestionGroupInstitutionAssociationCreateSerializer(
            data=data, many=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
       
    @action(methods=['post'], detail=False, url_path='map-studentgroup')
    def map_studentgroup(self, request, *args, **kwargs):
        survey_id = self.get_parents_query_dict()['survey']
        survey_on = Survey.objects.get(id=survey_id).survey_on.pk
        if not survey_on == 'studentgroup' and not survey_on == 'student':
            raise ParseError('This survey is not a studengroup or student survey')
        questiongroup_ids = request.data.get('questiongroup_ids', [])
        studentgroup_ids = request.data.get('studentgroup_ids', [])
        institution_ids = request.data.get('institution_ids', [])
        if not studentgroup_ids and not institution_ids:
            raise ParseError('Please pass studentgroup_ids OR institution_ids')
        # Make a copy of the institution_ids param.
        list_of_studentgroups = list(studentgroup_ids)
        # Fetch all studentgroups under a institution and append to the list
        for institution in institution_ids:
            studentgroups_under_institution = self.get_institution_studentgroup_ids(
                institution)
            for studentgroup in studentgroups_under_institution:
                list_of_studentgroups.append(studentgroup)
        data = []
        for questiongroup_id in questiongroup_ids:
            for studentgroup_id in list_of_studentgroups:
                data.append({
                    'questiongroup': questiongroup_id,
                    'studentgroup': studentgroup_id,
                    'status': 'AC'
                })
        serializer = QuestionGroupStudentGroupAssociationCreateSerializer(
            data=data, many=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(methods=['get'], detail=False, url_path='mappings')
    def mappings(self, request, *args, **kwargs):
        survey_id = self.get_parents_query_dict()['survey']
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
                    questiongroup__status='AC'
                ).filter(
                institution_id__in=institution_ids,
                questiongroup__survey_id=survey_id)
            for qgroup_inst in qset:
                res = {
                    "id": qgroup_inst.institution_id,
                    "name": qgroup_inst.institution.name,
                    "assessment-type": "institution",
                    "assessment": {
                        "id": qgroup_inst.questiongroup_id,
                        "name": qgroup_inst.questiongroup.name,
                    }
                }
                response.append(res)
        else:
            res = {}
            sg_qset = QuestionGroup_StudentGroup_Association.\
                objects.filter(
                        questiongroup__status='AC'
                    ).filter(
                    studentgroup__institution_id__in=institution_ids,
                    questiongroup__survey_id=survey_id
                )
            for sgroup_inst in sg_qset:
                sg_name = sgroup_inst.studentgroup.name
                sg_id = sgroup_inst.studentgroup.id
                qgroup = sgroup_inst.questiongroup
                res = {
                   "id": sg_id,
                   "name": sg_name,
                   "assessment-type": "studentgroup",
                   "assessment": {
                       "id": qgroup.id, "name": qgroup.name
                   }
                }
                response.append(res)
        return Response(response)


class QGroupStoriesInfoView(ILPListAPIView, ILPStateMixin):
    """
    Returns total number of stories for the home page
    """
    def get(self, request, *args, **kwargs):
        state = self.get_state()
        return Response({
            'total_stories': AnswerGroup_Institution.objects.filter(
                questiongroup__survey__id=5).filter(
                    questiongroup__survey__admin0=state
                    ).count(),
            'total_verified_stories': AnswerGroup_Institution.objects.filter(
                questiongroup__survey__id=5).filter(
                    is_verified=True
                    ).filter(
                    questiongroup__survey__admin0=state
                    ).count(),
            'total_images': InstitutionImages.objects.filter(
                answergroup__questiongroup__survey=5).filter(
                    answergroup__questiongroup__survey__admin0=state
                    ).count()
        })
