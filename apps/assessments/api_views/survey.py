import json

from django.conf import settings
from django.db.models import Sum

from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ParseError, APIException
from rest_framework import authentication, permissions

from common.mixins import ILPStateMixin
from common.views import ILPViewSet
from common.models import AcademicYear

from boundary.models import BasicBoundaryAgg, BoundaryStateCode

from schools.models import InstitutionClassYearStuCount

from assessments.models import (
    Survey, QuestionGroup_Institution_Association,
    QuestionGroup_StudentGroup_Association,
    SurveyInstitutionQuestionGroupAnsAgg,
    SurveyBoundaryQuestionGroupAgg, SurveyBoundaryQuestionGroupAnsAgg,
    SurveyInstitutionQuestionGroupAgg, SurveyTagMappingAgg,
    SurveyTagClassMapping, InstitutionImages
)
from assessments.serializers import SurveySerializer
from assessments.filters import SurveyTagFilter


class SurveysViewSet(ILPViewSet, ILPStateMixin):
    '''Returns all surveys'''
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    filter_class = SurveyTagFilter


class SurveyInstitutionDetailAPIView(ListAPIView, ILPStateMixin):

    def list(self, request, *args, **kwargs):
        survey_id = self.request.query_params.get('survey_id', None)
        survey_on = Survey.objects.get(id=survey_id).survey_on
        institution_id = self.request.query_params.get('institution_id', None)
        if survey_on == 'institution':
            res = {}
            qset = QuestionGroup_Institution_Association.objects.filter(
                institution_id=institution_id,
                questiongroup__survey_id=survey_id)
            for qgroup_inst in qset:
                res[qgroup_inst.questiongroup_id] = {
                    "id": qgroup_inst.questiongroup_id,
                    "name": qgroup_inst.questiongroup.name
                }
        else:
            res = {}
            sg_qset = QuestionGroup_StudentGroup_Association.\
                objects.filter(
                    studentgroup__institution_id=institution_id,
                )
            response = {}
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
                    response.update(res)
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


class SurveyQuestionGroupDetailsAPIView(APIView):
    response = {}

    def get_from_to(self, queryset, from_monthyear, to_monthyear):
        if from_monthyear:
            from_split = from_monthyear.split('-')
            from_year, from_month = from_split[0], from_split[1]
            queryset = queryset.filter(
                year__gte=from_year, month__gte=from_month)

        if to_monthyear:
            to_split = to_monthyear.split('-')
            to_year, to_month = to_split[0], to_split[1]
            queryset = queryset.filter(year__lte=to_year, month__lte=to_month)

        return queryset

    def get_boundary_data(
            self, boundary_id, questiongroup_id,
            year, from_monthyear, to_monthyear
    ):
        basicqueryset = BasicBoundaryAgg.objects.\
            filter(boundary_id=boundary_id, year=year).\
            values_list('num_schools', flat=True)
        if basicqueryset:
            self.response["summary"]["total_schools"] = basicqueryset[0]
        queryset = SurveyBoundaryQuestionGroupAgg.objects.\
            filter(boundary_id=boundary_id, questiongroup_id=questiongroup_id)
        queryset = self.get_from_to(queryset, from_monthyear, to_monthyear)

        qs_agg = queryset.aggregate(
            Sum('num_schools'), Sum('num_children'), Sum('num_assessments'))

        self.response["summary"] = {
            "schools_impacted": qs_agg['num_schools__sum'],
            "children_impacted": qs_agg['num_children__sum'],
            "num_assessments": qs_agg['num_assessments__sum']
        }

        queryset = self.get_from_to(
            SurveyBoundaryQuestionGroupAnsAgg.objects.filter(
                boundary_id=boundary_id, questiongroup_id=questiongroup_id),
            from_monthyear, to_monthyear)
        return queryset

    def get_institution_data(
            self, institution_id, questiongroup_id,
            year, from_monthyear, to_monthyear
    ):
        queryset = SurveyInstitutionQuestionGroupAgg.objects.filter(
            institution_id=institution_id, questiongroup_id=questiongroup_id)
        queryset = self.get_from_to(queryset, from_monthyear, to_monthyear)

        qs_agg = queryset.aggregate(
            Sum('num_children'), Sum('num_assessments'))

        self.response["summary"] = {
            "total_schools": 1,
            "schools_impacted": 1,
            "children_impacted": qs_agg['num_children__sum'],
            "num_assessments": qs_agg['num_assessments__sum']
        }
        queryset = self.get_from_to(
            SurveyInstitutionQuestionGroupAnsAgg.objects.filter(
                institution_id=institution_id,
                questiongroup_id=questiongroup_id),
            from_monthyear, to_monthyear)
        return queryset

    def get(self, request):
        if not self.request.GET.get('questiongroup'):
            raise ParseError("Mandatory parameter questiongroup not passed")
        questiongroup_id = self.request.GET.get('questiongroup')
        boundary_id = self.request.GET.get('boundary')
        institution_id = self.request.GET.get('institution')
        to_monthyear = self.request.GET.get('to')
        from_monthyear = self.request.GET.get('from')

        year = self.request.GET.get('year', settings.DEFAULT_ACADEMIC_YEAR)
        try:
            academic_year = AcademicYear.objects.get(char_id=year)
        except AcademicYear.DoesNotExist:
            raise APIException('Academic year is not valid.\
                    It should be in the form of 1112.', 404)

        state_id = BoundaryStateCode.objects.filter(
            char_id=settings.ILP_STATE_ID).\
            values("boundary_id")[0]["boundary_id"]

        self.response["summary"] = {}
        if boundary_id:
            queryset = self.get_boundary_data(
                boundary_id, questiongroup_id,
                year, from_monthyear, to_monthyear)
        elif institution_id:
            queryset = self.get_institution_data(
                institution_id, questiongroup_id,
                year, from_monthyear, to_monthyear)
        else:
            queryset = self.get_boundary_data(
                state_id, questiongroup_id,
                year, from_monthyear, to_monthyear)

        queryset = queryset.values(
            'question_desc', 'answer_option', 'num_answers'
        )

        self.response["questions"] = {}
        for row in queryset:
            if row["question_desc"] in self.response["questions"]:
                self.response["questions"][row["question_desc"]][
                    row["answer_option"]] = row["num_answers"]
            else:
                self.response["questions"][row["question_desc"]] = \
                    {"text": row["question_desc"],
                     row["answer_option"]: row["num_answers"]}
        return Response(self.response)


class SurveyTagAggAPIView(APIView):
    response = {}

    def get_boundary_data(self, boundary_id, survey_tag, year):
        print(boundary_id)
        print(survey_tag+" "+year)
        queryset = SurveyTagMappingAgg.objects.\
            filter(boundary_id=boundary_id, survey_tag=survey_tag,
                   academic_year_id=year).values("num_schools",
                                                 "num_students")
        if queryset:
            print(queryset)
            self.response["num_schools"] = queryset[0]["num_schools"]
            self.response["num_students"] = queryset[0]["num_students"]

        return

    def get_institution_data(self, institution_id, survey_tag, year):

        sg_names = SurveyTagClassMapping.objects.\
                filter(tag=survey_tag, academic_year=year).\
                values_list("sg_name", flat=True).distinct()

        queryset = InstitutionClassYearStuCount.objects.\
            filter(institution_id=institution_id, academic_year=year,
                   studentgroup__in=sg_names)
        qs_agg = queryset.aggregate(Sum('num'))
        if queryset:
            self.response["num_schools"] = 1
            self.response["num_students"] = qs_agg["num__sum"]

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

        state_id = BoundaryStateCode.objects.filter(
            char_id=settings.ILP_STATE_ID).\
            values("boundary_id")[0]["boundary_id"]

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
            print(e)
            response['error'] = 'Invalid JSON data'

        # if response['error'] is None:
        #     for story in stories.get('stories', []):
        #         timestamp = int(story.get('created_at')) / 1000
        #         sysid = None

        #         try:
        #             sysid = int(story.get('sysid'))
        #         except ValueError:
        #             sysid = None

        #         try:
        #             if story.get('respondent_type') not in dict(UserType.USER_TYPE_CHOICES).keys():
        #                 raise Exception("Invalid respondent type")
        #             user_type = UserType.objects.get(name__iexact=story.get('respondent_type'))
        #             new_story, created = Story.objects.get_or_create(
        #                 user=request.user,
        #                 school_id=story.get('school_id'),
        #                 group_id=story.get('group_id'),
        #                 user_type=user_type,
        #                 date_of_visit=datetime.datetime.fromtimestamp(timestamp)
        #             )

        #             if created:
        #                 new_story.sysid = sysid
        #                 new_story.is_verified = True
        #                 new_story.telephone = request.user.mobile_no
        #                 new_story.name = request.user.get_full_name()
        #                 new_story.email = request.user.email
        #                 new_story.save()

        #             # Save location info
        #             if story.get('lat', None) is not None and \
        #                     story.get('lng', None) is not None:
        #                 new_story.location = Point(
        #                     story.get('lat'), story.get('lng'))
        #                 new_story.save()

        #             # Save the answers
        #             for answer in story.get('answers', []):
        #                 new_answer, created = Answer.objects.get_or_create(
        #                     text=answer.get('text'),
        #                     story=new_story,
        #                     question=Question.objects.get(
        #                         pk=answer.get('question_id')
        #                     )
        #                 )

        #             # Save the image
        #             image = story.get('image', None)
        #             if image:
        #                 image_type, data = image.split(',')
        #                 image_data = b64decode(data)
        #                 file_name = '{}_{}.png'.format(
        #                     new_story.school.id, random.randint(0, 9999))

        #                 saved_image = StoryImage(
        #                     story=new_story,
        #                     filename=file_name,
        #                     image=ContentFile(image_data, file_name)
        #                 )
        #                 saved_image.save()

        #             response['success'][story.get('_id')] = new_story.id
        #         except Exception as e:
        #             print "Error saving stories and answers:", e
        #             response['failed'].append(story.get('_id'))
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
