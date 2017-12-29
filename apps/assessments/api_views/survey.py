from django.db.models import Sum

from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from common.mixins import ILPStateMixin
from common.views import ILPViewSet

from boundary.models import BoundaryType

from assessments.models import (
    Survey, SurveySummaryAgg, SurveyDetailsAgg,
    Source, SurveyBoundaryAgg, SurveyUserTypeAgg,
    SurveyRespondentTypeAgg, SurveyInstitutionAgg,
    SurveyAnsAgg, Question, SurveyQuestionKeyAgg,
    SurveyElectionBoundaryAgg, SurveyClassGenderAgg,
    SurveyClassAnsAgg, SurveyClassQuestionKeyAgg,
    SurveyQuestionGroupQuestionKeyAgg, SurveyQuestionGroupGenderAgg,
    SurveyQuestionGroupGenderCorrectAnsAgg, SurveyClassGenderCorrectAnsAgg,
    SurveyQuestionKeyCorrectAnsAgg, SurveyClassQuestionKeyCorrectAnsAgg,
    SurveyQuestionGroupQuestionKeyCorrectAnsAgg
)
from assessments.serializers import SurveySerializer
from assessments.filters import SurveyFilter


class SurveysViewSet(ILPViewSet, ILPStateMixin):
    '''Returns all surveys'''
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    # filter_class = StudentGroupFilter


class SurveySummaryAPIView(ListAPIView, ILPStateMixin):
    queryset = SurveySummaryAgg.objects.all()
    filter_backends = [SurveyFilter, ]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        qs_agg = queryset.aggregate(
            Sum('num_schools'), Sum('num_children'), Sum('num_assessments'))

        response = {
            "summary": {
                "total_school": qs_agg['num_schools__sum'],
                "schools_impacted": qs_agg['num_schools__sum'],
                "children_impacted": qs_agg['num_children__sum'],
                "total_assessments": qs_agg['num_assessments__sum'],
            }
        }
        res_surveys = []
        for sid in queryset.distinct('survey_id').values_list(
                'survey_id', flat=True
        ):
            survey = Survey.objects.get(id=sid)
            sources = survey.questiongroup_set.distinct(
                'source__name').values_list('source', flat=True)
            res_survey = {
                "id": sid,
                "name": survey.name,
                "source": sources
            }
            res_surveys.append(res_survey)
        response['surveys'] = res_surveys
        return Response(response)


class SurveyVolumeAPIView(ListAPIView, ILPStateMixin):
    queryset = SurveySummaryAgg.objects.all()
    filter_backends = [SurveyFilter, ]

    def list(self, request, *args, **kwargs):
        years = range(2009, 2020)
        months = {
            "01": "Jan", "02": "Feb", "03": "Mar",
            "04": "APR", "05": "MAY", "06": "JUN",
            "07": "JUL", "08": "AUG", "09": "SEP",
            "10": "OCT", "11": "NOV", "12": "DEC"
        }
        volume_res = {}
        for year in years:
            year_res = {}
            y_agg = self.queryset.filter(year_month__startswith=year)
            for month in months:
                year_res[months[month]] = \
                    y_agg.filter(year_month__endswith=month).count()
            volume_res[year] = year_res
        return Response(volume_res)


class SurveyInfoSourceAPIView(ListAPIView, ILPStateMixin):
    queryset = SurveyDetailsAgg.objects.all()
    filter_backends = [SurveyFilter, ]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        source_ids = queryset.distinct(
            'source').values_list('source', flat=True)

        response = {}
        source_res = {}
        for source_id in source_ids:
            source_name = "None"
            if source_id:
                source_name = Source.objects.get(id=source_id).name

            qs_agg = queryset.filter(source=source_id).aggregate(
                Sum('num_schools'), Sum('num_assessments'),
            )
            source_res[source_name] = {
                "schools_impacted": qs_agg['num_schools__sum'],
                "assessment_count": qs_agg['num_assessments__sum'],
                # Todo
                "last_assessment": None,
            }
        response['source'] = source_res
        return Response(response)


class SurveyInfoBoundarySourceAPIView(ListAPIView, ILPStateMixin):
    queryset = SurveyBoundaryAgg.objects.all()
    filter_backends = [SurveyFilter, ]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        source_ids = queryset.distinct(
            'source').values_list('source', flat=True)

        response = {}
        source_res = {}
        for source_id in source_ids:
            source_name = "None"
            if source_id:
                source_name = Source.objects.get(id=source_id).name

            boundary_type_ids = queryset.filter(source=source_id)\
                .distinct('boundary_id__boundary_type')\
                .values_list('boundary_id__boundary_type', flat=True)
            
            boundary_list = []
            for b_type_id in boundary_type_ids:
                boundary_qs_agg = queryset\
                    .filter(
                        source=source_id,
                        boundary_id__boundary_type=b_type_id)\
                    .aggregate(
                        Sum('num_schools'),
                        Sum('num_children'),
                        Sum('num_assessments'),
                    )
                boundary_res = {
                    "id": b_type_id,
                    "name": BoundaryType.objects.get(char_id=b_type_id).name,
                    "schools_impacted": boundary_qs_agg['num_schools__sum'],
                    "children_impacted": boundary_qs_agg['num_children__sum'],
                    "assessment_count": boundary_qs_agg['num_assessments__sum']
                }
                boundary_list.append({b_type_id: boundary_res})
            source_res[source_name] = boundary_list
        response['boundaries'] = source_res
        return Response(response)


class SurveyInfoUserAPIView(ListAPIView, ILPStateMixin):
    queryset = SurveyUserTypeAgg.objects.all()
    filter_backends = [SurveyFilter, ]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        response = {}
        user_response = {}
        user_types = queryset.distinct('user_type')\
            .values_list('user_type', flat=True)
        for user_type in user_types:
            user_type_agg = queryset.filter(user_type=user_type)\
                .aggregate(Sum('num_assessments'))
            user_response[user_type] = user_type_agg['num_assessments__sum']
        response['users'] = user_response
        return Response(response)


class SurveyInfoRespondentAPIView(ListAPIView, ILPStateMixin):
    queryset = SurveyRespondentTypeAgg.objects.all()
    filter_backends = [SurveyFilter, ]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        response = {}
        respondent_res = {}
        respondent_types = queryset.distinct('respondent_type')\
            .values_list('respondent_type', flat=True)
        for respondent_type in respondent_types:
            respondent_type_agg = queryset\
                .filter(respondent_type=respondent_type)\
                .aggregate(Sum('num_assessments'))
            respondent_res[respondent_type] = respondent_type_agg[
                'num_assessments__sum']
        response['respondents'] = respondent_res
        return Response(response)


class SurveyInfoSchoolAPIView(ListAPIView, ILPStateMixin):
    serializer_class = SurveySerializer

    def get_queryset(self):
        queryset = SurveyInstitutionAgg.objects.all()
        institution_id = self.request.query_params.get('school_id', None)
        survey_ids = queryset\
            .filter(institution_id=institution_id).distinct('survey_id')\
            .values_list('survey_id', flat=True)
        return Survey.objects.filter(id__in=survey_ids)


class SurveyInfoBoundaryAPIView(ListAPIView, ILPStateMixin):
    serializer_class = SurveySerializer

    def get_queryset(self):
        queryset = SurveyBoundaryAgg.objects.all()
        boundary_id = self.request.query_params.get('boundary_id', None)
        survey_ids = queryset\
            .filter(boundary_id=boundary_id).distinct('survey_id')\
            .values_list('survey_id', flat=True)
        return Survey.objects.filter(id__in=survey_ids)


class SurveyDetailSourceAPIView(ListAPIView, ILPStateMixin):
    queryset = SurveyAnsAgg.objects.all()
    filter_backends = [SurveyFilter, ]

    def list(self, request, *args, **kwargs):
        source_id = self.request.query_params.get('source', None)
        queryset = self.filter_queryset(self.get_queryset())

        source_ids = Source.objects.all()
        if source_id:
            source_ids = Source.objects.filter(id=source_id)
        source_ids = source_ids.values_list('id', flat=True)

        response = {}
        sources_res = {}
        for s_id in source_ids:
            source = Source.objects.get(id=s_id)
            source_agg = queryset.filter(source=s_id)
            question_ids = source_agg\
                .distinct('question_id').values_list('question_id', flat=True)
            question_list = []
            for q_id in question_ids:
                question = Question.objects.get(id=q_id)
                question_agg = source_agg.filter(question_id=q_id)
                question_res = {
                    "question": {}, "question_type": None, "answers": {}
                }

                question_res['question'] = {
                    "display_text": question.display_text,
                    "text": question.question_text,
                    "key": question.key
                }

                if question.question_type:
                    question_res["question_type"] = \
                        question.question_type.display.char_id

                ans_options = \
                    question_agg.distinct('answer_option')\
                    .values_list('answer_option', flat=True)
                for ans in ans_options:
                    question_res['answers'][ans] = \
                        question_agg.filter(answer_option=ans)\
                        .aggregate(Sum('num_answers'))['num_answers__sum']

                question_list.append(question_res)
            sources_res[source.name] = question_list
        response["source"] = sources_res
        return Response(response)


class SurveyDetailKeyAPIView(ListAPIView, ILPStateMixin):
    filter_backends = [SurveyFilter, ]

    def get_queryset(self):
        return SurveyQuestionKeyAgg.objects.all()

    def get_answer_queryset(self):
        return SurveyQuestionKeyCorrectAnsAgg.objects.all()

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        ans_qs = self.filter_queryset(self.get_answer_queryset())
        response = {}
        scores_res = {}
        question_keys = qs.distinct('question_key')\
            .values_list('question_key', flat=True)
        for q_key in question_keys:
            key_agg = qs.filter(question_key=q_key)\
                .aggregate(Sum('num_assessments'))
            key_ans_agg = ans_qs.filter(question_key=q_key)\
                .aggregate(Sum('num_assessments'))
            scores_res[q_key] = {
                "total": key_agg['num_assessments__sum'],
                "score": key_ans_agg['num_assessments__sum']
            }
        response['scores'] = scores_res
        return Response(response)


class SurveyClassQuestionKeyAPIView(ListAPIView, ILPStateMixin):
    filter_backends = [SurveyFilter, ]

    def get_queryset(self):
        return SurveyClassQuestionKeyAgg.objects.all()

    def get_answer_queryset(self):
        return SurveyClassQuestionKeyCorrectAnsAgg.objects.all()

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        ans_qs = self.filter_queryset(self.get_answer_queryset())
        classes_res = {}

        classess = qs.distinct('sg_name')\
            .values_list('sg_name', flat=True)
        question_keys = qs.distinct('question_key')\
            .values_list('question_key', flat=True)

        for sg_name in classess:
            q_res = {}
            for q_key in question_keys:
                key_agg = qs.filter(sg_name=sg_name, question_key=q_key)\
                    .aggregate(Sum('num_assessments'))
                key_ans_agg = ans_qs.filter(
                    sg_name=sg_name, question_key=q_key
                ).aggregate(Sum('num_assessments'))

                q_res[q_key] = {
                    "total": key_agg['num_assessments__sum'],
                    "score": key_ans_agg['num_assessments__sum']
                }
            classes_res[sg_name] = q_res
        return Response(classes_res)


class SurveyQuestionGroupQuestionKeyAPIView(ListAPIView, ILPStateMixin):
    filter_backends = [SurveyFilter, ]

    def get_queryset(self):
        return SurveyQuestionGroupQuestionKeyAgg.objects.all()

    def get_answer_queryset(self):
        return SurveyQuestionGroupQuestionKeyCorrectAnsAgg.objects.all()

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        ans_qs = self.filter_queryset(self.get_answer_queryset())
        qgroup_res = {}

        qgroup_ids = qs.distinct('questiongroup_id')\
            .values_list('questiongroup_id', flat=True)
        question_keys = qs.distinct('question_key')\
            .values_list('question_key', flat=True)

        for qgroup_id in qgroup_ids:
            q_res = {}
            for q_key in question_keys:
                key_agg = qs.filter(
                    questiongroup_id=qgroup_id, question_key=q_key)\
                    .aggregate(Sum('num_assessments'))
                key_ans_agg = ans_qs.filter(
                    questiongroup_id=qgroup_id, question_key=q_key)\
                    .aggregate(Sum('num_assessments'))

                q_res[q_key] = {
                    "total": key_agg['num_assessments__sum'],
                    "score": key_ans_agg['num_assessments__sum']
                }
            qgroup_res[qgroup_id] = q_res
        return Response(qgroup_res)


class SurveyInfoClassGenderAPIView(ListAPIView, ILPStateMixin):
    filter_backends = [SurveyFilter, ]

    def get_survey_type(self):
        survey_id = self.request.query_params.get('survey_id', None)
        return Survey.objects.get(id=survey_id).survey_on.char_id

    def get_queryset(self):
        survey_type = self.get_survey_type()
        if survey_type == 'institution':
            return SurveyQuestionGroupGenderAgg.objects.all()
        return SurveyClassGenderAgg.objects.all()

    def get_answer_queryset(self):
        survey_type = self.get_survey_type()
        if survey_type == 'institution':
            return SurveyQuestionGroupGenderCorrectAnsAgg.objects.all()
        return SurveyClassGenderCorrectAnsAgg.objects.all()
    
    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        ans_qs = self.filter_queryset(self.get_answer_queryset())

        group_field = 'sg_name'
        if self.get_survey_type() == 'institution':
            group_field = 'questiongroup_name'

        group_res = {}
        group_names = qs\
            .distinct(group_field).values_list(group_field, flat=True)
        genders = qs.distinct('gender').values_list('gender', flat=True)

        for group_name in group_names:
            gender_res = {}
            for gender in genders:
                group_param = {'sg_name': group_name}
                if group_field == 'questiongroup_name':
                    group_param = {'questiongroup_name': group_name}

                gender_agg = qs.filter(gender=gender, **group_param)\
                    .aggregate(Sum('num_assessments'))
                gender_ans_agg = ans_qs.filter(gender=gender, **group_param)\
                    .aggregate(Sum('num_assessments'))

                gender_res[gender] = {
                    "total_count": gender_agg['num_assessments__sum'],
                    "perfect_score_count": gender_ans_agg[
                        'num_assessments__sum']
                }
            group_res[group_name] = {
                "gender": gender_res
            }
        return Response(group_res)


class SurveyDetailClassAPIView(ListAPIView, ILPStateMixin):
    queryset = SurveyClassAnsAgg.objects.all()
    filter_backends = [SurveyFilter, ]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        response = {}
        sg_res = {}
        sg_names = queryset.distinct('sg_name')\
            .values_list('sg_name', flat=True)
        for sg_name in sg_names:
            sg_agg = queryset.filter(sg_name=sg_name)
            question_ids = sg_agg\
                .distinct('question_id').values_list('question_id', flat=True)
            question_list = []
            for q_id in question_ids:
                question = Question.objects.get(id=q_id)
                question_agg = sg_agg.filter(question_id=q_id)
                question_res = {
                    "question": {}, "question_type": None, "answers": {}
                }

                question_res['question'] = {
                    "display_text": question.display_text,
                    "text": question.question_text,
                    "key": question.key
                }

                if question.question_type:
                    question_res["question_type"] = \
                        question.question_type.display.char_id

                ans_options = \
                    question_agg.distinct('answer_option')\
                    .values_list('answer_option', flat=True)
                for ans in ans_options:
                    question_res['answers'][ans] = \
                        question_agg.filter(answer_option=ans)\
                        .aggregate(Sum('num_answers'))['num_answers__sum']

                question_list.append(question_res)
            sg_res[sg_name] = question_list
        response["classes"] = sg_res
        return Response(response)


class SurveyInfoEBoundaryAPIView(ListAPIView, ILPStateMixin):
    queryset = SurveyElectionBoundaryAgg.objects.all()
    filter_backends = [SurveyFilter, ]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        response = {}
        source_res = {}
        boundary_type_ids = queryset\
            .distinct('boundary_id__const_ward_type')\
            .values_list('boundary_id__const_ward_type', flat=True)

        boundary_list = []
        for b_type_id in boundary_type_ids:
            boundary_qs_agg = queryset\
                .filter(boundary_id__const_ward_type=b_type_id)\
                .aggregate(
                    Sum('num_schools'),
                    Sum('num_children'),
                    Sum('num_assessments'),
                )

            boundary_res = {
                "id": b_type_id,
                "name": BoundaryType.objects.get(char_id=b_type_id).name,
                "schools_impacted": boundary_qs_agg['num_schools__sum'],
                "children_impacted": boundary_qs_agg['num_children__sum'],
                "assessment_count": boundary_qs_agg['num_assessments__sum']
            }
            boundary_list.append(boundary_res)
            source_res[b_type_id] = boundary_list
        response['boundaries'] = source_res
        return Response(response)
