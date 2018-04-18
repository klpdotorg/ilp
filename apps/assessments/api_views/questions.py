import logging

from django.http import Http404

from common.views import ILPListAPIView
from common.mixins import ILPStateMixin
from common.models import Status
from rest_framework.exceptions import ParseError

from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin

from django.db.models import Q

from assessments.models import (
    QuestionGroup, Question, QuestionGroup_Questions,
    AnswerGroup_Institution, QuestionGroup_Institution_Association,
    QuestionGroup_StudentGroup_Association, InstitutionImages
)
from assessments.serializers import (
    QuestionGroupSerializer, QuestionSerializer,
    QuestionGroupQuestionSerializer, QuestionGroupInstitutionSerializer,
    QuestionGroupInstitutionAssociationSerializer,
    QuestionGroupStudentGroupAssociationSerializer
)

from schools.models import (
    Institution,
    StudentGroup)

logger = logging.getLogger(__name__)


class QuestionGroupViewSet(
        NestedViewSetMixin, ILPStateMixin, viewsets.ModelViewSet
):
    '''Returns all questiongroups belonging to a survey'''
    queryset = QuestionGroup.objects.exclude(status=Status.DELETED)
    serializer_class = QuestionGroupSerializer

    def perform_destroy(self, instance):
        instance.status_id = Status.DELETED
        instance.save()


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

    queryset = Question.objects.all()

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
            'total_images': InstitutionImages.objects.filter(answergroup__questiongroup__survey=5).count()

        })


class QuestionGroupSchoolViewSet(viewsets.ModelViewSet):
    queryset = QuestionGroup_Institution_Association.objects.all()
    serializer_class = QuestionGroupInstitutionSerializer

class QuestionGroupInstitutionAssociationViewSet(viewsets.ModelViewSet):
    assessmentids = []
    institutionids = []
    boundaryids = []
    queryset = QuestionGroup_Institution_Association.objects.all()
    serializer_class = QuestionGroupInstitutionAssociationSerializer

    def create(self, request, *args, **kwargs):
        if not self.request.data.get('questiongroup_ids'):
            raise ParseError("Mandatory parameter questiongroup_ids not passed")
        self.assessmentids = self.request.data.get('questiongroup_ids').split(",")
        if self.request.data.get('boundary_ids'):
            self.boundaryids = self.request.data.get('boundary_ids').split(",")
        if self.request.data.get('institution_ids'):
            self.institutionids = self.request.data.get('institution_ids').split(",")
        if self.institutionids == [] and self.boundaryids == []:
            raise ParseError("Mandatory parameter institution_ids or boundary_ids not passed")
        response = self.createAssessmentInstitutionAssociation()

        return response

    def createAssessmentInstitutionAssociation(self):
        request = []
        for assessmentid in self.assessmentids:
            if self.institutionids == []:
                for boundaryid in self.boundaryids:
                    self.institutionids = Institution.objects.values_list(
                        'id', flat=True).filter(Q(admin1_id=boundaryid) |
                                                Q(admin2_id=boundaryid) |
                                                Q(admin3_id=boundaryid))
            for institutionid in self.institutionids:
                request.append({'questiongroup': assessmentid,
                                'institution': institutionid,
                                'status': 'AC'})
        print("JSON is: ", request)
        serializer = self.get_serializer(data=request, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)


class QuestionGroupStudentGroupAssociationViewSet(viewsets.ModelViewSet):
    queryset = QuestionGroup_StudentGroup_Association.objects.all()
    serializer_class = QuestionGroupStudentGroupAssociationSerializer

    def create(self, request, *args, **kwargs):
        assessment_ids, studentgroup_ids = [], []

        questiongroup_ids = self.request.data.get('questiongroup_ids', [])
        if questiongroup_ids:
            questiongroup_ids = assessment_ids.split(",")

        studentgroup_ids = self.request.data.get('studentgroup_ids', [])
        if studentgroup_ids:
            studentgroup_ids = studentgroup_ids.split(",")

        response = self.create_assessment_studentgroup_assocation(
            assessment_ids, studentgroup_ids
        )
        return response

    def create_assessment_studentgroup_assocation(
            self, assessment_ids, studentgroup_ids
    ):
        request = []
        for assessment_id in assessment_ids:
            for studentgroup_id in studentgroup_ids:
                request.append({
                    'questiongroup': assessment_id,
                    'studentgroup': studentgroup_id,
                    'status': 'AC'
                })
        serializer = self.get_serializer(data=request, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)
