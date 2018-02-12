import json
import datetime
import random
from base64 import b64decode

from django.conf import settings
from django.db.models import Sum
from django.contrib.gis.geos import Point
from django.core.files.base import ContentFile

from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ParseError, APIException
from rest_framework import authentication, permissions

from common.mixins import ILPStateMixin
from common.views import ILPViewSet
from common.models import AcademicYear, Status

from boundary.models import (
    BasicBoundaryAgg, BoundaryStateCode, Boundary,
    BoundarySchoolCategoryAgg, BoundaryNeighbours
)

from schools.models import InstitutionClassYearStuCount
from assessments.models import (
    Survey, QuestionGroup_Institution_Association,
    QuestionGroup_StudentGroup_Association,
    SurveyInstitutionQuestionGroupAnsAgg,
    SurveyBoundaryQuestionGroupAgg, SurveyBoundaryQuestionGroupAnsAgg,
    SurveyInstitutionQuestionGroupAgg, SurveyTagMappingAgg,
    SurveyTagClassMapping, InstitutionImages,
    AnswerGroup_Institution, AnswerInstitution,
    Question, SurveyBoundaryAgg
)
from common.models import RespondentType
from assessments.serializers import (
    SurveySerializer, RespondentTypeSerializer
)
from assessments.filters import (
    SurveyFilter, SurveyTagFilter
)


class SurveysViewSet(ILPViewSet, ILPStateMixin):
    '''Returns all surveys'''
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    filter_class = SurveyTagFilter


class SurveyInstitutionDetailAPIView(ListAPIView, ILPStateMixin):

    def list(self, request, *args, **kwargs):
        survey_id = self.request.query_params.get('survey_id', None)
        survey_on = Survey.objects.get(id=survey_id).survey_on.pk
        institution_id = self.request.query_params.get('institution_id', None)
        response = []
        if survey_on == 'institution':
            res = {}
            qset = QuestionGroup_Institution_Association.objects.filter(
                institution_id=institution_id,
                questiongroup__survey_id=survey_id)
            for qgroup_inst in qset:
                res = {
                    "id": qgroup_inst.questiongroup_id,
                    "name": qgroup_inst.questiongroup.name,
                    "type": qgroup_inst.questiongroup.type.char_id
                }
                response.append(res)
        else:
            res = {}
            sg_qset = QuestionGroup_StudentGroup_Association.\
                objects.filter(
                    studentgroup__institution_id=institution_id,
                )
            for sgroup_inst in sg_qset:
                sg_name = sgroup_inst.studentgroup.name
                sg_id = sgroup_inst.studentgroup.id
                res[sg_name] = {
                    "id": sg_id, "name": sg_name
                }
                for studgroup_qgroup in sg_qset.filter(
                        questiongroup__survey_id=survey_id):
                    qgroup = studgroup_qgroup.questiongroup
                    res[sg_name][qgroup.id] = {
                        "id": qgroup.id, "name": qgroup.name
                    }
                    response.append(res)
        return Response(response)


class SurveyInstitutionAnsAggView(ListAPIView, ILPStateMixin):
    '''Returns all survey answers for a specific institution'''
    queryset = SurveyInstitutionQuestionGroupAnsAgg.objects.all()

    def list(self, request, *args, **kwargs):
        surveyid = self.request.query_params.get('survey_id', None)
        schoolid = self.request.query_params.get('school_id', None)
        questions_list = []
        if surveyid and schoolid:
            queryset = SurveyInstitutionQuestionGroupAnsAgg.objects.\
                filter(survey_id=surveyid).filter(institution_id=schoolid)
            question_answers = queryset.distinct('answer_option')
            distinct_questions = queryset.distinct('question_desc')
            for question in distinct_questions:
                answers = question_answers.values(
                    'answer_option', 'num_answers'
                )
                answer_list = {}
                for answer in answers:
                    answer_list[answer['answer_option']] =\
                        answer['num_answers']
                answer = {
                    "display_text": question.question_desc,
                    "question_id": question.question_id.id,
                    "answers": answer_list,
                }
                questions_list.append(answer)
        return Response(questions_list)


class SurveyQuestionGroupDetailsAPIView(ListAPIView):
    filter_backends = [SurveyFilter, ]

    def get(self, request):
        questiongroup_id = self.request.query_params.get('questiongroup_id', None)
        boundary_id = self.request.query_params.get('boundary_id', None)
        institution_id = self.request.query_params.get('institution_id', None)
        year = self.request.GET.get('year', settings.DEFAULT_ACADEMIC_YEAR)

        state_id = BoundaryStateCode.objects.filter(
            char_id=settings.ILP_STATE_ID).\
            values("boundary_id")[0]["boundary_id"]

        if institution_id:
            queryset = SurveyInstitutionQuestionGroupAgg.objects.filter(
                institution_id=institution_id
            )
            queryset = self.filter_queryset(queryset)
            if questiongroup_id:
                queryset = queryset.filter(questiongroup_id=questiongroup_id)

            qs_agg = queryset.aggregate(
                Sum('num_children'), Sum('num_assessments'))

            summary_res = {
                "total_schools": 1,
                "schools_impacted": 1,
                "children_impacted": qs_agg['num_children__sum'],
                "num_assessments": qs_agg['num_assessments__sum']
            }

            ans_queryset = SurveyInstitutionQuestionGroupAnsAgg.objects.filter(
                institution_id=institution_id
            )
            ans_queryset = self.filter_queryset(ans_queryset)
            if questiongroup_id:
                ans_queryset = ans_queryset.filter(
                    questiongroup_id=questiongroup_id)
        else:
            if not boundary_id:
                boundary_id = state_id
            queryset = SurveyBoundaryQuestionGroupAgg.objects.\
                filter(boundary_id=boundary_id)
            queryset = self.filter_queryset(queryset)
            if questiongroup_id:
                queryset = queryset.filter(questiongroup_id=questiongroup_id)

            qs_agg = queryset.aggregate(
                Sum('num_schools'), Sum('num_children'), Sum('num_assessments')
            )

            summary_res = {
                "schools_impacted": qs_agg['num_schools__sum'],
                "children_impacted": qs_agg['num_children__sum'],
                "num_assessments": qs_agg['num_assessments__sum']
            }

            basicqueryset = BasicBoundaryAgg.objects.\
                filter(boundary_id=boundary_id, year=year).\
                values_list('num_schools', flat=True)
            if basicqueryset:
                summary_res["total_schools"] = basicqueryset[0]

            ans_queryset = SurveyBoundaryQuestionGroupAnsAgg.objects.filter(
                    boundary_id=boundary_id)
            ans_queryset = self.filter_queryset(ans_queryset)
            if questiongroup_id:
                ans_queryset = ans_queryset.filter(
                    questiongroup_id=questiongroup_id)       

        ans_queryset = ans_queryset.values(
            'question_desc', 'answer_option', 'num_answers', 'question_id'
        )

        response = {}
        response['summary'] = summary_res
        questiongroup_ids = ans_queryset.distinct('questiongroup_id').\
            values_list('questiongroup_id', 'questiongroup_id__name')
        survey_ids = ans_queryset.distinct('survey_id').\
            values_list('survey_id', flat=True)

        survey_res = {'surveys': {}}
        for s_id in survey_ids:
            questiongroup_res = {}
            for qg_id, qg_name in questiongroup_ids:
                qgroup_ans_queryset = ans_queryset.filter(
                    survey_id=s_id, questiongroup_id=qg_id)
                question_dict = {}
                for row in qgroup_ans_queryset:
                    if (
                        row["question_desc"] in question_dict
                    ):
                        question_dict[row["question_desc"]][
                            row["answer_option"]] = row["num_answers"]
                    else:
                        question_dict[row["question_desc"]] = \
                            {
                                "text": row["question_desc"],
                                row["answer_option"]: row["num_answers"]
                            }
                        question_dict[row["question_desc"]]['id'] = row['question_id']
                if question_dict:
                    questiongroup_res[qg_name] = {}
                    questiongroup_res[qg_name]['questions'] = question_dict
            survey_res['surveys'][s_id] = {}
            survey_res['surveys'][s_id]['questiongroups'] = questiongroup_res
        response.update(survey_res)
        return Response(response)


class SurveyTagAggAPIView(APIView):
    response = {}

    def get_boundary_data(self, boundary_id, survey_tag, year):
        self.response = {"total_schools": 0,
                         "num_schools": 0,
                         "num_students": 0}

        queryset = BoundarySchoolCategoryAgg.objects.\
            filter(boundary_id=boundary_id, cat_ac_year=year,
                   institution_type='primary')

        if queryset:
            qs_agg = queryset.aggregate(Sum('num_schools'))
            self.response["total_schools"] = qs_agg["num_schools__sum"]

        queryset = SurveyTagMappingAgg.objects.\
            filter(boundary_id=boundary_id, survey_tag=survey_tag,
                   academic_year_id=year).values("num_schools",
                                                 "num_students")
        if queryset:
            self.response["num_schools"] = queryset[0]["num_schools"]
            self.response["num_students"] = queryset[0]["num_students"]

        return

    def get_institution_data(self, institution_id, survey_tag, year):
        self.response = {"total_schools": 1,
                         "num_schools": 1,
                         "num_students": 0}

        sg_names = SurveyTagClassMapping.objects.\
            filter(tag=survey_tag, academic_year=year).\
            values_list("sg_name", flat=True).distinct()

        queryset = InstitutionClassYearStuCount.objects.\
            filter(institution_id=institution_id, academic_year=year,
                   studentgroup__in=sg_names)
        if queryset:
            qs_agg = queryset.aggregate(Sum('num'))
            self.response["num_students"] = qs_agg["num__sum"]
        else:
            self.response["num_students"] = 0

        return

    def get(self, request):
        if not self.request.GET.get('survey_tag'):
            raise ParseError("Mandatory parameter survey_tag not passed")
        survey_tag = self.request.GET.get('survey_tag')
        boundary_id = self.request.GET.get('boundary')
        institution_id = self.request.GET.get('institution')

        year = self.request.GET.get('year', settings.DEFAULT_ACADEMIC_YEAR)
        try:
            academic_year = AcademicYear.objects.get(char_id=year)
        except AcademicYear.DoesNotExist:
            raise APIException('Academic year is not valid.\
                    It should be in the form of 1112.', 404)

        state_id = BoundaryStateCode.objects.\
            get(char_id=settings.ILP_STATE_ID).boundary_id

        if boundary_id:
            self.get_boundary_data(boundary_id, survey_tag, year)
        elif institution_id:
            self.get_institution_data(institution_id, survey_tag, year)
        else:
            self.get_boundary_data(state_id, survey_tag, year)

        return Response(self.response)


class AssessmentSyncView(APIView):
    """
        Syncs a set of assessments from Konnect app
    """
    authentication_classes = (authentication.TokenAuthentication,
                              authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        response = {
            'success': dict(),
            'failed': [],
            'error': None
        }
        try:
            stories = json.loads(request.body.decode('utf-8'))
            print(stories)
        except ValueError as e:
            response['error'] = 'Invalid JSON data'

        if response['error'] is None:
            for story in stories.get('stories', []):
                timestamp = int(story.get('created_at')) / 1000
                sysid = None

                try:
                    sysid = int(story.get('sysid'))
                except ValueError:
                    sysid = None

                try:

                    try:
                        respondent_type = RespondentType.objects.get(
                            char_id__iexact=story.get('respondent_type')
                        )
                    except RespondentType.DoesNotExist:
                        raise Exception("Invalid respondent type")

                    new_story, created = AnswerGroup_Institution.objects.get_or_create(
                        created_by=request.user,
                        institution_id=story.get('school_id'),
                        questiongroup_id=story.get('group_id'),
                        respondent_type=respondent_type,
                        date_of_visit=datetime.datetime.fromtimestamp(
                            timestamp
                        ),
                        # TODO: Check with Shivangi if the below is okay.
                        status=Status.objects.get(char_id='AC')
                    )

                    if created:
                        new_story.sysid = sysid
                        new_story.is_verified = True
                        new_story.mobile = request.user.mobile_no
                        new_story.save()

                    # Save location info
                    if story.get('lat', None) is not None and \
                            story.get('lng', None) is not None:
                        new_story.location = Point(
                            story.get('lat'), story.get('lng'))
                        new_story.save()

                    # Save the answers
                    for answer in story.get('answers', []):
                        new_answer, created = AnswerInstitution.objects.get_or_create(
                            answer=answer.get('text'),
                            answergroup=new_story,
                            question=Question.objects.get(
                                pk=answer.get('question_id')
                            )
                        )

                    # Save the image
                    image = story.get('image', None)
                    if image:
                        image_type, data = image.split(',')
                        image_data = b64decode(data)
                        file_name = '{}_{}_{}.png'.format(
                            new_story.created_by.id,
                            new_story.institution.id,
                            random.randint(0, 9999)
                        )

                        InstitutionImages.objects.create(
                            answergroup=new_story,
                            filename=file_name,
                            image=ContentFile(image_data, file_name)
                        )

                    response['success'][story.get('_id')] = new_story.id
                except Exception as e:
                    print("Error saving stories and answers:", e)
                    response['failed'].append(story.get('_id'))
        return Response(response)


class AssessmentsImagesView(APIView):
    """
        Returns all images synced for a school
    """

    def get(self, request):
        school_id = request.GET.get('school_id', 0)
        from_date = request.GET.get('from', '')
        to_date = request.GET.get('to', '')

        images = InstitutionImages.objects.filter(
            answergroup__institution__id=school_id
        )
        if from_date and to_date:
            try:
                images = images.filter(
                    answergroup__date_of_visit__range=[from_date, to_date])
            except Exception as e:
                print(e)

        images = [
            {'url': '/media/' + str(i.image),
                'date': i.answergroup.date_of_visit,
                'school_id': school_id} for i in images
        ]
        return Response({'images': images})


class RespondentTypeList(ListAPIView):
    queryset = RespondentType.objects.all()
    serializer_class = RespondentTypeSerializer


class SurveyUserSummary(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        questiongroup_id = request.GET.get('questiongroup_id', None)
        institution_id = request.GET.get('institution_id', None)
        from_date = request.GET.get('from', '')
        to_date = request.GET.get('to', '')
        response = {}

        queryset = AnswerGroup_Institution.objects.filter(
            created_by=request.user
        )

        if questiongroup_id is not None:
            queryset = queryset.filter(questiongroup__id=questiongroup_id)

        if institution_id is not None:
            queryset = queryset.filter(institution__id=institution_id)

        if from_date and to_date:
            try:
                queryset = queryset.filter(
                    entered_at__range=[from_date, to_date])
            except Exception as e:
                print(e)

        response['assessments'] = queryset.count()
        response['schools_covered'] = queryset.values(
            'institution_id').distinct().count()

        return Response(response)


class SurveyBoundaryNeighbourInfoAPIView(ListAPIView):
    """
    TODO:
    only survey_name and total assessments,
    if boundary not passed, look into surveytagmapping, get the boundaries do the rest.
    add surveyFilter.

    """
    queryset = BoundaryNeighbours.objects.all()

    def get(self, request):
        boundary_id = request.GET.get('boundary_id', None)
        if not boundary_id:
            raise APIException("Please pass boundary_id as param.")
        response = []
        neighbour_ids = BoundaryNeighbours.objects.filter(
            boundary_id=boundary_id).\
            values_list('neighbour_id', flat=True)
        for n_id in neighbour_ids:
            n_boundary = Boundary.objects.get(id=n_id)
            neighbour_res = {}
            neighbour_res['name'] = n_boundary.name
            neighbour_res['surveys'] = {}

            survey_ids = SurveyBoundaryAgg.objects.filter(boundary_id=n_id).\
                distinct('survey_id').values_list('survey_id', flat=True)
            for survey_id in survey_ids:
                qset = SurveyBoundaryAgg.objects.filter(
                    survey_id=survey_id, boundary_id=n_id)
                b_agg = qset.aggregate(
                    Sum('num_schools'), Sum('num_children'),
                    Sum('num_assessments'), Sum('num_users')
                )
                neighbour_res['surveys'][survey_id] = {
                    "total_school": b_agg['num_schools__sum'],
                    "num_users": b_agg['num_users__sum'],
                    "schools_impacted": b_agg['num_schools__sum'],
                    "children_impacted": b_agg['num_children__sum'],
                    "total_assessments": b_agg['num_assessments__sum'],
                }
            response.append(neighbour_res)
        return Response(response)


class SurveyBoundaryNeighbourDetailAPIView(ListAPIView):
    queryset = BoundaryNeighbours.objects.all()

    def get(self, request, format=None):
        boundary_id = request.GET.get('boundary_id', None)
        if not boundary_id:
            raise APIException("Please pass boundary_id as param.")
        response = {}
        neighbour_res = {}
        neighbour_ids = BoundaryNeighbours.objects.filter(
            boundary_id=boundary_id).\
            values_list('neighbour_id', flat=True)
        for n_id in neighbour_ids:
            qset = SurveyBoundaryAgg.objects.filter(boundary_id=n_id)
            b_agg = qset.aggregate(
                Sum('num_schools'), Sum('num_children'),
                Sum('num_assessments'), Sum('num_users')
            )
            neighbour_res[n_id] = {
                "total_school": b_agg['num_schools__sum'],
                "num_users": b_agg['num_users__sum'],
                "schools_impacted": b_agg['num_schools__sum'],
                "children_impacted": b_agg['num_children__sum'],
                "total_assessments": b_agg['num_assessments__sum'],
            }
            response[boundary_id] = neighbour_res
        return Response(response)