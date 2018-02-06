from django.db.models import Sum, Q
from django.conf import settings
from django.db.models.fields import IntegerField
from django.db.models.expressions import Value

from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from common.mixins import ILPStateMixin
from boundary.models import BoundaryType, BoundaryStateCode

from assessments.models import *

from assessments.mixins import AggQuerySetMixin
from assessments.filters import SurveyFilter
from assessments.serializers import SurveySerializer


class SurveySummaryAPIView(AggQuerySetMixin, ListAPIView, ILPStateMixin):
    filter_backends = [SurveyFilter, ]
    institution_queryset = SurveyInstitutionAgg.objects.all()
    boundary_queryset = SurveyBoundaryAgg.objects.all()

    def get_summary_response(self, queryset):
        institution_id = self.request.query_params.get('institution_id', None)
        if institution_id:
            qs_agg = queryset.aggregate(
                Sum('num_children'), Sum('num_assessments'), Sum('num_users'))
            institution_summary_response = {
                "summary": {
                    "total_school": 1,
                    "schools_impacted": 1,
                    "num_users": qs_agg['num_users__sum'],
                    "children_impacted": qs_agg['num_children__sum'],
                    "total_assessments": qs_agg['num_assessments__sum'],
                    "last_assessment": queryset.latest(
                        'last_assessment').last_assessment,
                }
            }
            return institution_summary_response

        qs_agg = queryset.aggregate(
            Sum('num_schools'), Sum('num_children'), Sum('num_assessments'),
            Sum('num_users')
        )
        boundary_summary_response = {
            "summary": {
                "total_school": qs_agg['num_schools__sum'],
                "num_users": qs_agg['num_users__sum'],
                "schools_impacted": qs_agg['num_schools__sum'],
                "children_impacted": qs_agg['num_children__sum'],
                "total_assessments": qs_agg['num_assessments__sum'],
                "last_assessment": queryset.latest(
                    'last_assessment').last_assessment,
            }
        }
        return boundary_summary_response

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        response = {}
        summary_response = self.get_summary_response(queryset)
        response.update(**summary_response)

        res_surveys = []
        survey_ids = queryset.distinct('survey_id').\
            values_list('survey_id', flat=True)
        for sid in survey_ids:
            survey = Survey.objects.get(id=sid)
            sources = survey.questiongroup_set.distinct(
                'source__name').values_list('source', flat=True)
            res_survey = {
                "id": sid,
                "name": survey.name,
                "source": sources
            }
            res_survey.update(
                **self.get_summary_response(queryset.filter(survey_id=sid))
            )
            res_surveys.append(res_survey)
        response['surveys'] = res_surveys
        return Response(response)


class SurveyVolumeAPIView(AggQuerySetMixin, ListAPIView, ILPStateMixin):
    filter_backends = [SurveyFilter, ]
    institution_queryset = SurveyInstitutionAgg.objects.all()
    boundary_queryset = SurveyBoundaryAgg.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        years = queryset.values_list('yearmonth', flat=True)
        years = [year//100 for year in years]
        months = {
            "01": "Jan", "02": "Feb", "03": "Mar",
            "04": "Apr", "05": "May", "06": "Jun",
            "07": "Jul", "08": "Aug", "09": "Sep",
            "10": "Oct", "11": "Nov", "12": "Dec",
            "00": ""
        }
        volume_res = {}
        for year in years:
            year_res = {}
            y_agg = queryset.filter(yearmonth__startswith=year)
            for month in months:
                num_assess = y_agg.filter(yearmonth__endswith=month).\
                    aggregate(Sum('num_assessments'))['num_assessments__sum']
                year_res[months[month]] = num_assess if num_assess else 0
            volume_res[year] = year_res
        return Response(volume_res)


class SurveyInfoSourceAPIView(AggQuerySetMixin, ListAPIView, ILPStateMixin):
    filter_backends = [SurveyFilter, ]
    institution_queryset = SurveyInstitutionAgg.objects.all()
    boundary_queryset = SurveyBoundaryAgg.objects.all()

    def get_qs_agg(self, queryset, source_id):
        if self.request.query_params.get('institution_id', None):
            qs_agg = queryset.filter(source=source_id).aggregate(
                Sum('num_assessments')
            )
            qs_agg['num_schools__sum'] = 1
            return qs_agg
        qs_agg = queryset.filter(source=source_id).aggregate(
            Sum('num_schools'), Sum('num_assessments'),
        )
        return qs_agg

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
            qs_agg = self.get_qs_agg(queryset, source_id)

            source_res[source_name] = {
                "schools_impacted": qs_agg['num_schools__sum'],
                "assessment_count": qs_agg['num_assessments__sum'],
                "last_assessment": queryset.latest(
                    'last_assessment').last_assessment,
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


class SurveyInfoUserAPIView(AggQuerySetMixin, ListAPIView, ILPStateMixin):
    filter_backends = [SurveyFilter, ]
    institution_queryset = SurveyInstitutionUserTypeAgg.objects.all()
    boundary_queryset = SurveyBoundaryUserTypeAgg.objects.all()

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


class SurveyInfoRespondentAPIView(
        AggQuerySetMixin, ListAPIView, ILPStateMixin
):
    filter_backends = [SurveyFilter, ]
    institution_queryset = SurveyInstitutionRespondentTypeAgg.objects.all()
    boundary_queryset = SurveyBoundaryRespondentTypeAgg.objects.all()

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
        if institution_id:
            queryset = queryset.filter(institution_id=institution_id)
        survey_ids = queryset\
            .distinct('survey_id').values_list('survey_id', flat=True)
        return Survey.objects.filter(id__in=survey_ids)


class SurveyInfoBoundaryAPIView(ListAPIView, ILPStateMixin):
    serializer_class = SurveySerializer

    def get_queryset(self):
        queryset = SurveyBoundaryAgg.objects.all()
        boundary_id = self.request.query_params.get('boundary_id', None)
        if boundary_id:
            queryset = queryset.filter(boundary_id=boundary_id)
        survey_ids = queryset\
            .distinct('survey_id').values_list('survey_id', flat=True)
        return Survey.objects.filter(id__in=survey_ids)


class SurveyDetailSourceAPIView(AggQuerySetMixin, ListAPIView, ILPStateMixin):
    filter_backends = [SurveyFilter, ]
    institution_queryset = SurveyInstitutionQuestionGroupAnsAgg.objects.all()
    boundary_queryset = SurveyBoundaryQuestionGroupAnsAgg.objects.all()

    def list(self, request, *args, **kwargs):
        source_names = self.request.query_params.getlist('source', None)
        queryset = self.filter_queryset(self.get_queryset())

        source_ids = Source.objects.all()
        if source_names:
            source_ids = Source.objects.filter(name__in=source_names)
        source_ids = source_ids.values_list('id', flat=True)

        response = {}
        sources_res = {}
        for s_id in source_ids:
            source = Source.objects.get(id=s_id)
            source_agg = queryset.filter(source=s_id)
            question_ids = source_agg\
                .distinct('question_id').values_list('question_id', flat=True)
            question_list = []
            ans_options = \
                source_agg.distinct('answer_option')\
                .values_list('answer_option', flat=True)
            for q_id in question_ids:
                question = Question.objects.get(id=q_id)
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

                question_agg = source_agg.filter(question_id=q_id)
                for ans in ans_options:
                    question_res['answers'][ans] = \
                        question_agg.filter(answer_option=ans)\
                        .aggregate(Sum('num_answers'))['num_answers__sum']
                question_list.append(question_res)
            sources_res[source.name] = question_list
        response["source"] = sources_res
        return Response(response)


class SurveyDetailKeyAPIView(AggQuerySetMixin, ListAPIView, ILPStateMixin):
    filter_backends = [SurveyFilter, ]
    institution_queryset = SurveyInstitutionQuestionKeyAgg.objects.all()
    boundary_queryset = SurveyBoundaryQuestionKeyAgg.objects.all()

    def get_answer_queryset(self):
        institution_id = self.request.query_params.get('institution_id', None)
        boundary_id = self.request.query_params.get('boundary_id', None)
        if institution_id:
            return SurveyInstitutionQuestionKeyCorrectAnsAgg.objects.filter(
                institution_id=institution_id)
        if boundary_id:
            return SurveyBoundaryQuestionKeyCorrectAnsAgg.objects.filter(
                boundary_id=boundary_id)

        state_id = BoundaryStateCode.objects.get(
            char_id=settings.ILP_STATE_ID).boundary_id
        return SurveyBoundaryQuestionKeyCorrectAnsAgg.objects.filter(
            boundary_id=state_id)

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


class SurveyClassQuestionKeyAPIView(
        AggQuerySetMixin, ListAPIView, ILPStateMixin
):
    filter_backends = [SurveyFilter, ]
    institution_queryset = SurveyInstitutionClassQuestionKeyAgg.objects.all()
    boundary_queryset = SurveyBoundaryClassQuestionKeyAgg.objects.all()

    def get_answer_queryset(self):
        institution_id = self.request.query_params.get('institution_id', None)
        boundary_id = self.request.query_params.get('boundary_id', None)
        if institution_id:
            return SurveyInstitutionClassQuestionKeyCorrectAnsAgg.objects.\
                filter(institution_id=institution_id)
        if boundary_id:
            return SurveyBoundaryClassQuestionKeyCorrectAnsAgg.objects.\
                filter(boundary_id=boundary_id)

        state_id = BoundaryStateCode.objects.get(
            char_id=settings.ILP_STATE_ID).boundary_id
        return SurveyBoundaryClassQuestionKeyCorrectAnsAgg.objects.filter(
            boundary_id=state_id)

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


class SurveyQuestionGroupQuestionKeyAPIView(
        AggQuerySetMixin, ListAPIView, ILPStateMixin
):
    filter_backends = [SurveyFilter, ]
    institution_queryset = SurveyInstitutionQuestionGroupQuestionKeyAgg.\
        objects.all()
    boundary_queryset = SurveyBoundaryQuestionGroupQuestionKeyAgg.\
        objects.all()

    def get_answer_queryset(self):
        institution_id = self.request.query_params.get('institution_id', None)
        boundary_id = self.request.query_params.get('boundary_id', None)
        if institution_id:
            return SurveyInstitutionQuestionGroupQuestionKeyCorrectAnsAgg.\
                objects.filter(institution_id=institution_id)
        if boundary_id:
            return SurveyBoundaryQuestionGroupQuestionKeyCorrectAnsAgg.\
                objects.filter(boundary_id=boundary_id)

        state_id = BoundaryStateCode.objects.get(
            char_id=settings.ILP_STATE_ID).boundary_id
        return SurveyBoundaryQuestionGroupQuestionKeyCorrectAnsAgg.objects.\
            filter(boundary_id=state_id)

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        ans_qs = self.filter_queryset(self.get_answer_queryset())
        qgroup_res = {}

        qgroups = qs.distinct('questiongroup_id')\
            .values_list('questiongroup_id', 'questiongroup_name')

        for qgroup_id, qgroup_name in qgroups:
            q_res = {}
            qgroup_qs = qs.filter(questiongroup_id=qgroup_id)
            qgroup_ans_qs = ans_qs.filter(questiongroup_id=qgroup_id)
            key_agg = qgroup_qs.values(
                'question_key').annotate(num_assess=Sum('num_assessments'))
            ans_key_agg = qgroup_ans_qs.values(
                'question_key').annotate(num_assess=Sum('num_assessments'))

            question_keys = key_agg.values_list('question_key', flat=True)           
            for q_key in question_keys:
                total = key_agg.get(question_key=q_key)['num_assess']
                try:
                    score = ans_key_agg.get(question_key=q_key)['num_assess']
                except Exception as e:
                    score = None
                q_res[q_key] = {
                    "total": total,
                    "score": score
                }
            qgroup_res[qgroup_name] = q_res
        return Response(qgroup_res)


class SurveyInfoClassGenderAPIView(ListAPIView, ILPStateMixin):
    filter_backends = [SurveyFilter, ]

    def get_survey_type(self):
        survey_id = self.request.query_params.get('survey_id', None)
        return Survey.objects.get(id=survey_id).survey_on.char_id

    def get_queryset(self):
        survey_type = self.get_survey_type()
        state_id = BoundaryStateCode.objects.get(
            char_id=settings.ILP_STATE_ID).boundary_id
        institution_id = self.request.query_params.get('institution_id', None)
        boundary_id = self.request.query_params.get('boundary_id', None)

        if survey_type == 'institution':
            if institution_id:
                return SurveyInstitutionQuestionGroupGenderAgg.objects.filter(
                    institution_id=institution_id)
            elif boundary_id:
                return SurveyBoundaryQuestionGroupGenderAgg.objects.filter(
                    boundary_id=boundary_id)
            else:
                return SurveyBoundaryQuestionGroupGenderAgg.objects.filter(
                    boundary_id=state_id)
        else:
            if institution_id:
                return SurveyInstitutionClassGenderAgg.objects.filter(
                    institution_id=institution_id)
            elif boundary_id:
                return SurveyBoundaryClassGenderAgg.objects.filter(
                    boundary_id=boundary_id)
            else:
                return SurveyBoundaryClassGenderAgg.objects.filter(
                    boundary_id=state_id)

    def get_answer_queryset(self):
        survey_type = self.get_survey_type()
        if survey_type == 'institution':
            return SurveyQuestionGroupGenderCorrectAnsAgg.objects.all()
        return SurveyClassGenderCorrectAnsAgg.objects.all()

        survey_type = self.get_survey_type()
        state_id = BoundaryStateCode.objects.get(
            char_id=settings.ILP_STATE_ID).boundary_id
        institution_id = self.request.query_params.get('institution_id', None)
        boundary_id = self.request.query_params.get('boundary_id', None)

        if survey_type == 'institution':
            if institution_id:
                return SurveyInstitutionQuestionGroupGenderCorrectAnsAgg.\
                    filter(institution_id=institution_id)
            elif boundary_id:
                return SurveyBoundaryQuestionGroupGenderCorrectAnsAgg.\
                    objects.filter(boundary_id=boundary_id)
            else:
                return SurveyBoundaryQuestionGroupGenderCorrectAnsAgg.\
                    filter(boundary_id=state_id)
        else:
            if institution_id:
                return SurveyInstitutionClassGenderCorrectAnsAgg.\
                    filter(institution_id=institution_id)
            elif boundary_id:
                return SurveyBoundaryClassGenderCorrectAnsAgg.\
                    objects.filter(boundary_id=boundary_id)
            else:
                return SurveyBoundaryClassGenderCorrectAnsAgg.\
                    filter(boundary_id=state_id)

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


class SurveyDetailClassAPIView(AggQuerySetMixin, ListAPIView, ILPStateMixin):
    filter_backends = [SurveyFilter, ]
    institution_queryset = SurveyInstitutionClassAnsAgg.objects.all()
    boundary_queryset = SurveyBoundaryClassAnsAgg.objects.all()

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
