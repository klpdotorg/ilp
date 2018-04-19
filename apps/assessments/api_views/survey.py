import json
import datetime
import random
from base64 import b64decode

from django.conf import settings
from django.db.models import Sum, Q
from django.contrib.gis.geos import Point
from django.core.files.base import ContentFile

from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ParseError, APIException
from rest_framework import authentication, permissions
from rest_framework import status as HttpStatus

from common.mixins import ILPStateMixin
from common.views import ILPViewSet
from common.models import (
    AcademicYear, Status, InstitutionType
)
from permissions.permissions import AppPostPermissions
from boundary.models import (
    BasicBoundaryAgg, BoundaryStateCode, Boundary,
    BoundarySchoolCategoryAgg, BoundaryNeighbours,
    BoundaryType
)
from boundary.serializers import BoundarySerializer

from schools.models import (
    Institution, InstitutionClassYearStuCount
)
from schools.serializers import InstitutionSerializer

from assessments.models import (
    Survey, QuestionGroup_Institution_Association,
    QuestionGroup_StudentGroup_Association,
    SurveyInstitutionQuestionGroupAnsAgg,
    SurveyBoundaryQuestionGroupAgg, SurveyBoundaryQuestionGroupAnsAgg,
    SurveyInstitutionQuestionGroupAgg, SurveyTagMappingAgg,
    SurveyTagClassMapping, InstitutionImages,
    AnswerGroup_Institution, AnswerInstitution,
    Question, SurveyBoundaryAgg, QuestionGroup,
    SurveyBoundaryQuestionGroupQuestionKeyCorrectAnsAgg,
    SurveyBoundaryQuestionGroupQuestionKeyAgg, SurveyInstitutionAgg,
    SurveyTagMapping, AnswerGroup_Student, SurveyElectionBoundaryAgg,
    SurveyBoundaryUserTypeAgg, SurveyBoundaryElectionTypeCount,
    SurveyTagInstitutionMapping
)
from common.models import RespondentType, Status
from assessments.serializers import (
    SurveySerializer, RespondentTypeSerializer,
    SurveyCreateSerializer
)
from assessments.filters import (
    SurveyFilter, SurveyTagFilter
)


class SurveysViewSet(ILPViewSet, ILPStateMixin):
    '''Returns all surveys'''
    queryset = Survey.objects.exclude(status__in=[
        Status.DELETED, Status.INACTIVE])
    filter_class = SurveyTagFilter

    def get_serializer_class(self):
        if self.request.method in ['POST', ]:
            return SurveyCreateSerializer
        return SurveySerializer

    def get_queryset(self):
        # Filer based on state
        state = self.get_state()
        queryset = self.queryset.filter(admin0=state)

        # TODO: IMPROVE: Can we combine status filtering with
        # SurveyTagFilter or use a new filter altogether
        # Filter status
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status__char_id=status)

        return queryset

    def perform_destroy(self, instance):
        instance.status_id = Status.DELETED
        instance.save()


class SurveyBoundaryAPIView(ListAPIView, ILPStateMixin):
    queryset = SurveyTagMappingAgg.objects.all()

    def list(self, request, *args, **kwargs):
        survey_tag = self.request.query_params.get('survey_tag', None)
        boundary_id = self.request.query_params.get(
            'boundary_id', self.get_state().id
        )
        qs = self.get_queryset()
        if survey_tag:
            qs = qs.filter(survey_tag=survey_tag)
        qs = qs.filter(boundary_id__parent_id=boundary_id)
        boundary_ids = qs.values_list('boundary_id', flat=True)
        boundaries = Boundary.objects.filter(id__in=boundary_ids)
        response = BoundarySerializer(boundaries, many=True).data
        return Response(response)


class SurveyInstitutionAPIView(ListAPIView, ILPStateMixin):
    queryset = SurveyTagInstitutionMapping.objects.all()

    def list(self, request, *args, **kwargs):
        survey_tag = self.request.query_params.get('survey_tag', None)
        boundary_id = self.request.query_params.get(
            'boundary_id', self.get_state().id
        )
        qset = self.get_queryset()
        if survey_tag:
            qset = qset.filter(tag=survey_tag)
        qset = qset.filter(
            Q(institution_id__admin0_id=boundary_id) |
            Q(institution_id__admin1_id=boundary_id) |
            Q(institution_id__admin2_id=boundary_id) |
            Q(institution_id__admin3_id=boundary_id)
        )
        institution_ids = qset.values_list('institution_id', flat=True)
        institutions = Institution.objects.filter(id__in=institution_ids)
        response = InstitutionSerializer(institutions, many=True).data
        return Response(response)


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
            num_stories = AnswerGroup_Institution.objects.filter(institution_id=schoolid).filter(questiongroup_id__in=(1,6)).count()
            comments = AnswerGroup_Institution.objects.filter(institution_id=schoolid).filter(questiongroup_id__in=(1,6)).values('comments', 'group_value')
            
            question_answers = queryset.distinct('answer_option')
            distinct_questions = queryset.distinct('question_desc')
            
            for question in distinct_questions:
                answers = question_answers.values(
                    'answer_option')
                answer_list = {}
                for answer in answers:
                    # There may be multiple rows with "Yes" for the same question. We need to calculate sum of all answers with "Yes".
                    # Get all rows from the queryset which have "Yes" and do a SUM (num_answers) on this distinct answer_option
                    filter_queryset = queryset.filter(answer_option=answer['answer_option'])
                    sum = queryset.filter(question_desc=question.question_desc).filter(answer_option=answer['answer_option']).aggregate(total_answers=Sum('num_answers'))
                    if sum['total_answers'] is None:
                        sum['total_answers']=0
                    answer_list[answer['answer_option']] =\
                        sum['total_answers']
                answer = {
                    "display_text": question.question_desc,
                    "question_id": question.question_id.id,
                    "answers": answer_list,
                }
                questions_list.append(answer)
        return Response({
            'num_stories': num_stories,
            'results': questions_list,
            'comments': comments
        })


class SurveyQuestionGroupDetailsAPIView(ListAPIView):
    filter_backends = [SurveyFilter, ]
    queryset = SurveyInstitutionQuestionGroupAgg.objects.all()

    def institution_qs(self):
        return self.filter_queryset(self.queryset)

    def get(self, request, *args, **kwargs):
        survey_id = self.request.query_params.get('survey_id', None)
        boundary_id = self.request.query_params.get('boundary_id', None)
        institution_id = self.request.query_params.get('institution_id', None)
        state_id = BoundaryStateCode.objects.filter(
            char_id=settings.ILP_STATE_ID).\
            values("boundary_id")[0]["boundary_id"]
        if not survey_id:
            return ParseError("Mandatory param survey_id is not passed.")
        questiongroup_ids = Survey.objects.get(id=survey_id).\
            questiongroup_set.values_list('id', flat=True)

        if institution_id:
            queryset = SurveyInstitutionQuestionGroupAgg.objects.filter(
                institution_id=institution_id
            )
            queryset = self.filter_queryset(queryset)
            if questiongroup_ids:
                queryset = queryset.filter(
                    questiongroup_id__in=questiongroup_ids)

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
            if questiongroup_ids:
                ans_queryset = ans_queryset.filter(
                    questiongroup_id__in=questiongroup_ids)
        else:
            if not boundary_id:
                boundary_id = state_id
            queryset = SurveyBoundaryQuestionGroupAgg.objects.\
                filter(boundary_id=boundary_id)
            queryset = self.filter_queryset(queryset)
            if questiongroup_ids:
                queryset = queryset.filter(
                    questiongroup_id__in=questiongroup_ids)

            qs_agg = queryset.aggregate(
                Sum('num_schools'), Sum('num_children'), Sum('num_assessments')
            )
            
            institution_qs = self.institution_qs()
            institution_qs = institution_qs.filter(
                Q(institution_id__admin0_id=boundary_id) |
                Q(institution_id__admin1_id=boundary_id) |
                Q(institution_id__admin2_id=boundary_id) |
                Q(institution_id__admin3_id=boundary_id)
            )
            institution_qs = institution_qs.filter(
                questiongroup_id__in=questiongroup_ids)
            summary_res = {
                "schools_impacted": institution_qs.distinct(
                    'institution_id').count(),
                "children_impacted": qs_agg['num_children__sum'],
                "num_assessments": qs_agg['num_assessments__sum']
            }
            inst_count = Institution.objects.filter(
                institution_type_id=InstitutionType.PRIMARY_SCHOOL
            ).filter(
                Q(admin0_id=boundary_id) |
                Q(admin1_id=boundary_id) |
                Q(admin2_id=boundary_id) |
                Q(admin3_id=boundary_id)
            ).count()
            summary_res["total_schools"] = inst_count

            ans_queryset = SurveyBoundaryQuestionGroupAnsAgg.objects.filter(
                    boundary_id=boundary_id)
            ans_queryset = self.filter_queryset(ans_queryset)
            if questiongroup_ids:
                ans_queryset = ans_queryset.filter(
                    questiongroup_id__in=questiongroup_ids)

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
                    if (row["question_desc"] in question_dict):
                        if (
                            row["answer_option"] in question_dict[row["question_desc"]]
                        ):
                            question_dict[row["question_desc"]][
                                row["answer_option"]] += row["num_answers"]
                        else:
                            question_dict[row["question_desc"]][
                                row["answer_option"]] = row["num_answers"]
                    else:
                        question_dict[row["question_desc"]] = \
                            {
                                "text": row["question_desc"],
                                row["answer_option"]: row["num_answers"]
                            }
                        question_dict[row["question_desc"]]['id'] = \
                            row['question_id']

                if question_dict:
                    questiongroup_res[qg_name] = {}
                    questiongroup_res[qg_name]['id'] = qg_id
                    questiongroup_res[qg_name]['questions'] = question_dict
            survey_res['surveys'][s_id] = {}
            survey_res['surveys'][s_id]['questiongroups'] = questiongroup_res
        response.update(survey_res)
        return Response(response)


class SurveyTagAggAPIView(APIView):

    def get_boundary_data(self, boundary_id, survey_tag, year):
        response = {
            "total_schools": 0,
            "num_schools": 0,
            "num_students": 0
        }

        queryset = BoundarySchoolCategoryAgg.objects.\
            filter(boundary_id=boundary_id, cat_ac_year=year,
                   institution_type='primary')

        if queryset:
            inst_count = Institution.objects.filter(
                institution_type_id=InstitutionType.PRIMARY_SCHOOL
            ).filter(
                Q(admin0_id=boundary_id) | Q(admin1_id=boundary_id) |
                Q(admin2_id=boundary_id) | Q(admin3_id=boundary_id)
            ).count()
            response["total_schools"] = inst_count

        queryset = SurveyTagMappingAgg.objects.\
            filter(boundary_id=boundary_id, survey_tag=survey_tag,
                   academic_year_id=year).values("num_students")
        num_schools = SurveyTagInstitutionMapping.objects.\
            filter(academic_year_id=year, tag__char_id=survey_tag).\
            filter(
                Q(institution__admin0_id=boundary_id) |
                Q(institution__admin1_id=boundary_id) |
                Q(institution__admin2_id=boundary_id) |
                Q(institution__admin3_id=boundary_id)
            ).count()
        response["num_schools"] = num_schools

        if queryset:
            response["num_students"] = queryset[0]["num_students"]

        return response

    def get_institution_data(self, institution_id, survey_tag, year):
        response = {
            "total_schools": 1,
            "num_schools": 1,
            "num_students": 0
        }

        sg_names = SurveyTagClassMapping.objects.\
            filter(tag=survey_tag, academic_year=year).\
            values_list("sg_name", flat=True).distinct()

        queryset = InstitutionClassYearStuCount.objects.\
            filter(institution_id=institution_id, academic_year=year,
                   studentgroup__in=sg_names)
        if queryset:
            qs_agg = queryset.aggregate(Sum('num'))
            response["num_students"] = qs_agg["num__sum"]
        else:
            response["num_students"] = 0
        return response

    def get(self, request):
        if not self.request.GET.get('survey_tag'):
            raise ParseError("Mandatory parameter survey_tag not passed")
        survey_tag = self.request.GET.get('survey_tag')
        boundary_id = self.request.GET.get('boundary_id')
        institution_id = self.request.GET.get('institution_id')

        year = self.request.GET.get('year', settings.DEFAULT_ACADEMIC_YEAR)
        try:
            academic_year = AcademicYear.objects.get(char_id=year)
        except AcademicYear.DoesNotExist:
            raise APIException('Academic year is not valid.\
                    It should be in the form of 1112.', 404)

        state_id = BoundaryStateCode.objects.\
            get(char_id=settings.ILP_STATE_ID).boundary_id

        if boundary_id:
            response = self.get_boundary_data(boundary_id, survey_tag, year)
        elif institution_id:
            response = self.get_institution_data(
                institution_id, survey_tag, year)
        else:
            response = self.get_boundary_data(state_id, survey_tag, year)

        return Response(response)


class AssessmentSyncView(APIView):
    """
        Syncs a set of assessments from Konnect app
    """
    authentication_classes = (authentication.TokenAuthentication,
                              authentication.SessionAuthentication,)
    permission_classes = (AppPostPermissions,)

    def post(self, request, format=None):
        response = {
            'success': dict(),
            'failed': [],
            'error': None
        }
        try:
            stories = json.loads(request.body.decode('utf-8'))
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

                    # See if the question group has a default respondent type
                    # If yes, use it instead of the one sent by Konnect
                    try:
                        question_group = QuestionGroup.objects.get(
                            pk=story.get('group_id')
                        )
                    except QuestionGroup.DoesNotExist:
                        raise Exception("Invalid question group")
                    else:
                        if question_group.default_respondent_type:
                            respondent_type = question_group \
                                .default_respondent_type
                        else:
                            try:
                                respondent_type = RespondentType.objects.get(
                                    char_id__iexact=story.get(
                                        'respondent_type'
                                    )
                                )
                            except RespondentType.DoesNotExist:
                                raise Exception("Invalid respondent type")

                    print(respondent_type.char_id)

                    new_story, created = AnswerGroup_Institution.objects \
                        .get_or_create(
                            created_by=request.user,
                            institution_id=story.get('school_id'),
                            questiongroup_id=story.get('group_id'),
                            respondent_type=respondent_type,
                            date_of_visit=datetime.datetime.fromtimestamp(
                                timestamp
                            ),
                            comments=story.get('comments'),
                            group_value=story.get('group_value'),
                            status=Status.objects.get(char_id='AC'),
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
                        new_answer, created = AnswerInstitution.objects \
                            .get_or_create(
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
    filter_backends = [SurveyFilter, ]
    queryset = SurveyBoundaryAgg.objects.all()

    def get_neighbour_boundaries(self):
        boundary_id = self.request.GET.get('boundary_id', None)
        survey_tag = self.request.GET.get('survey_tag', None)
        if boundary_id:
            neighbour_ids = BoundaryNeighbours.objects.filter(
                boundary_id=boundary_id).\
                values_list('neighbour_id', flat=True)
        else:
            _sd = BoundaryType.SCHOOL_DISTRICT
            btype = {
                "boundary_id__boundary_type__char_id": _sd
            }
            neighbour_ids = SurveyTagMappingAgg.objects.\
                filter(survey_tag=survey_tag).\
                filter(**btype).\
                values_list('boundary_id', flat=True)
        return neighbour_ids

    def get_electionboundary(
            self, boundary_id, survey_id, to_yearmonth, from_yearmonth
    ):
        queryset = SurveyBoundaryElectionTypeCount.objects.filter(
            boundary_id=boundary_id, survey_id=survey_id)
        if to_yearmonth:
            queryset = queryset.filter(yearmonth__lte=to_yearmonth)
        if from_yearmonth:
            queryset = queryset.filter(yearmonth__gte=from_yearmonth)

        electioncount_agg = queryset.values('const_ward_type').annotate(
            Sum('electionboundary_count'))
        res = {}
        for electioncount in electioncount_agg:
            res[electioncount['const_ward_type']] = \
                electioncount['electionboundary_count__sum']
        return res

    def get(self, request, *args, **kwargs):
        survey_tag = self.request.GET.get('survey_tag', None)
        to_ = request.query_params.get('to', None)
        from_ = request.query_params.get('from', None)
        to_yearmonth, from_yearmonth = None, None

        if to_:
            to_ = to_.split('-')
            to_year, to_month = to_[0], to_[1]
            to_yearmonth = int(to_year + to_month)

        if from_:
            from_ = from_.split('-')
            from_year, from_month = from_[0], from_[1]
            from_yearmonth = int(from_year + from_month)

        survey_tag_dict = {}
        if survey_tag:
            survey_tag_dict = {'survey_tag': survey_tag}

        neighbour_ids = set(self.get_neighbour_boundaries())
        response = []
        for n_id in neighbour_ids:
            n_boundary = Boundary.objects.get(id=n_id)
            neighbour_res = {}
            neighbour_res['name'] = n_boundary.name
            neighbour_res['type'] = n_boundary.type.name
            neighbour_res['schools'] = Institution.objects.filter(
                institution_type_id=InstitutionType.PRIMARY_SCHOOL
            ).filter(
                Q(admin0_id=n_id) | Q(admin1_id=n_id) |
                Q(admin2_id=n_id) | Q(admin3_id=n_id)
            ).count()
            neighbour_res['surveys'] = {}

            survey_ids = self.queryset.filter(boundary_id=n_id)
            survey_ids = self.filter_queryset(survey_ids).\
                distinct('survey_id').values_list('survey_id', flat=True)
            for survey_id in survey_ids:
                qset = self.filter_queryset(
                    self.queryset.filter(
                        survey_id=survey_id, boundary_id=n_id)
                )
                b_agg = qset.aggregate(Sum('num_assessments'))

                usertype_res = {}
                usertypes = SurveyBoundaryUserTypeAgg.objects.filter(
                    boundary_id=n_id, survey_id=survey_id, **survey_tag_dict
                )
                if to_yearmonth:
                    usertypes = usertypes.filter(yearmonth__lte=to_yearmonth)
                if from_yearmonth:
                    usertypes = usertypes.filter(yearmonth__gte=from_yearmonth)
                usertypes = usertypes.values(
                    'user_type').annotate(Sum('num_assessments'))

                for usertype in usertypes:
                    usertype_res[usertype['user_type']] = usertype[
                        'num_assessments__sum']
                neighbour_res['surveys'][survey_id] = {
                    "total_assessments": b_agg['num_assessments__sum'],
                    "users": usertype_res,
                    "electioncount": self.get_electionboundary(
                        n_id, survey_id, to_yearmonth, from_yearmonth
                    )
                }
            response.append(neighbour_res)
        return Response(response)


class SurveyBoundaryNeighbourDetailAPIView(ListAPIView):
    filter_backends = [SurveyFilter, ]
    queryset = SurveyBoundaryQuestionGroupQuestionKeyAgg.\
        objects.all()
    ans_queryset = SurveyBoundaryQuestionGroupQuestionKeyCorrectAnsAgg.\
        objects.all()

    def get_neighbour_boundaries(self):
        boundary_id = self.request.GET.get('boundary_id', None)
        survey_tag = self.request.GET.get('survey_tag', 'gka')
        if boundary_id:
            neighbour_ids = BoundaryNeighbours.objects.filter(
                boundary_id=boundary_id).\
                values_list('neighbour_id', flat=True)
        else:
            _sd = BoundaryType.SCHOOL_DISTRICT
            btype = {
                "boundary_id__boundary_type__char_id": _sd
            }
            neighbour_ids = SurveyTagMappingAgg.objects.\
                filter(survey_tag=survey_tag).\
                filter(**btype).\
                distinct('boundary_id').\
                values_list('boundary_id', flat=True)
        return neighbour_ids

    def get(self, request, *args, **kwargs):
        survey_ids = self.request.GET.getlist('survey_ids', [])
        if not survey_ids:
            raise ParseError("Mandatory parameter survey_ids not passed")

        neighbour_ids = self.get_neighbour_boundaries()
        response = []
        neighbour_res = {}
        for n_id in neighbour_ids:
            boundary = Boundary.objects.get(id=n_id)
            neighbour_res = {}
            neighbour_res['name'] = boundary.name
            neighbour_res['type'] = boundary.boundary_type.name

            qs = self.queryset.filter(boundary_id=n_id)
            qs = self.filter_queryset(qs)
            survey_res = {}

            surveys = qs.filter(survey_id__in=survey_ids).\
                distinct('survey_id').\
                values_list('survey_id', flat=True)

            for survey_id in surveys:
                survey_name = Survey.objects.get(id=survey_id).name
                survey_qs = qs.values('survey_id').filter(survey_id=survey_id)
                qgroups = survey_qs.distinct('questiongroup_id')\
                    .values_list('questiongroup_id', flat=True)
                qgroup_res = {}
                for qgroup_id in qgroups:
                    qgroup_name = QuestionGroup.objects.get(id=qgroup_id).name
                    qgroup_qs = survey_qs.values('questiongroup_id').\
                        filter(questiongroup_id=qgroup_id)
                    question_keys = qs.values('questiongroup_id')\
                        .filter(questiongroup_id=qgroup_id)\
                        .distinct('question_key')\
                        .values_list('question_key', flat=True)
                    qkey_res = {}
                    for key in question_keys:
                        qkey_res[key] = {
                            "score": qgroup_qs.values('question_key').filter(
                                question_key=key).aggregate(
                                    Sum('num_assessments')
                                )['num_assessments__sum'],
                            "totol": self.ans_queryset.filter(
                                    boundary_id=n_id, survey_id=survey_id,
                                    questiongroup_id=qgroup_id,
                                    question_key=key
                                ).aggregate(
                                    Sum('num_assessments')
                                )['num_assessments__sum']
                        }
                    qgroup_res[qgroup_id] = {
                        'name': qgroup_name, 'question_keys': qkey_res
                    }
                survey_res[survey_id] = {
                    'name': survey_name, 'questiongroups': qgroup_res
                }
            neighbour_res['surveys'] = survey_res
            response.append(neighbour_res)
        return Response(response)


class SurveyUsersCountAPIView(ListAPIView, ILPStateMixin):

    def get(self, request, *args, **kwargs):
        to_ = request.query_params.get('to', None)
        from_ = request.query_params.get('from', None)
        survey_tag = self.request.GET.get('survey_tag', None)
        boundary_id = self.request.GET.get(
            'boundary_id', self.get_state().id)
        institution_id = self.request.GET.get(
            'institution_id', None
        )

        survey_ids = SurveyTagMapping.objects.filter(
            tag__char_id=survey_tag
        ).values_list('survey_id', flat=True)

        questiongroup_ids = QuestionGroup.objects.filter(
            survey_id__in=survey_ids).values_list('id', flat=True)

        queryset = AnswerGroup_Institution.objects.\
            filter(questiongroup_id__in=questiongroup_ids)
        
        queryset = queryset.filter(
            Q(institution_id__admin0_id=boundary_id) |
            Q(institution_id__admin1_id=boundary_id) |
            Q(institution_id__admin2_id=boundary_id) |
            Q(institution_id__admin3_id=boundary_id)
        )

        if institution_id:
            queryset = queryset.filter(institution_id=institution_id)

        if to_:
            queryset = queryset.filter(date_of_visit__lte=to_)

        if from_:
            queryset = queryset.filter(date_of_visit__gte=from_)

        count = queryset.distinct('created_by_id').count()
        return Response({"count": count})
