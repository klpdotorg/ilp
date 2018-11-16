from django.db.models import Sum, Q
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from common.mixins import ILPStateMixin
from boundary.models import BoundaryType, BoundaryStateCode

from assessments.models import *
from assessments.mixins import AggMixin
from assessments.filters import SurveyFilter
from assessments.serializers import SurveySerializer


class SurveySummaryAPIView(AggMixin, ListAPIView, ILPStateMixin):
    filter_backends = [SurveyFilter, ]
    institution_queryset = SurveyInstitutionAgg.objects.all()
    boundary_queryset = SurveyBoundaryAgg.objects.all()
    eboundary_queryset = SurveyElectionBoundaryAgg.objects.all()

    def institution_qs(self):
        """
        Returns institution queryset filtered by boundary_id/state_id
        and filter_backend parameters. `self.institution_queryset` only
        return institution queryset filtered by institution_id.See AggMixin.
        """
        state_id = BoundaryStateCode.objects.get(
            char_id=settings.ILP_STATE_ID).boundary_id
        boundary_id = self.request.query_params.get('boundary_id', state_id)
        eboundary_id = self.request.query_params.get('electionboundary_id', None)
        if eboundary_id:
           institution_qs = SurveyInstitutionAgg.objects.filter(
                Q(institution_id__gp_id=eboundary_id) |
                Q(institution_id__mp_id=eboundary_id) |
                Q(institution_id__mla_id=eboundary_id) |
                Q(institution_id__ward_id=eboundary_id)
            )
        else:
            institution_qs = SurveyInstitutionAgg.objects.filter(
                Q(institution_id__admin0_id=boundary_id) |
                Q(institution_id__admin1_id=boundary_id) |
                Q(institution_id__admin2_id=boundary_id) |
                Q(institution_id__admin3_id=boundary_id)
            )
        return self.filter_queryset(institution_qs)

    def get_summary_response(self, queryset):
        """Generates summary response."""

        if not queryset:
            summary_response = {
                "summary": {
                    "schools_impacted": 0,
                    "num_users": 0,
                    "children_impacted": 0,
                    "total_assessments": 0,
                    "last_assessment": 0, 
                }
            }
            return summary_response
 
        institution_id = self.request.query_params.get('institution_id', None)
        if institution_id:
            qs_agg = queryset.aggregate(
                Sum('num_children'), Sum('num_assessments'), Sum('num_users'))
            institution_summary_response = {
                "summary": {
                    "schools_impacted": 1,
                    "num_users": qs_agg['num_users__sum'],
                    "children_impacted": qs_agg['num_children__sum'],
                    "total_assessments": qs_agg['num_assessments__sum'],
                    "last_assessment": 0 if not queryset else queryset.latest(
                        'last_assessment').last_assessment,
                }
            }
            return institution_summary_response

        qs_agg = queryset.aggregate(
            Sum('num_children'), Sum('num_assessments'), Sum('num_users')
        )
        boundary_summary_response = {
            "summary": {
                "num_users": qs_agg['num_users__sum'],
                "schools_impacted": self.institution_qs().distinct(
                    'institution_id').count(),
                "children_impacted": qs_agg['num_children__sum'],
                "total_assessments": qs_agg['num_assessments__sum'],
                "last_assessment": 0 if not queryset else queryset.latest(
                    'last_assessment').last_assessment,
            }
        }
        return boundary_summary_response

    def list(self, request, *args, **kwargs):
        """
        Returns total summary, and summary for each survey.
        """

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
                "id": sid, "name": survey.name, "source": sources
            }
            res_survey.update(
                **self.get_summary_response(queryset.filter(survey_id=sid))
            )
            res_surveys.append(res_survey)
        response['surveys'] = res_surveys
        return Response(response)


class SurveyVolumeAPIView(AggMixin, ListAPIView, ILPStateMixin):
    filter_backends = [SurveyFilter, ]
    institution_queryset = SurveyInstitutionAgg.objects.all()
    boundary_queryset = SurveyBoundaryAgg.objects.all()
    eboundary_queryset = SurveyElectionBoundaryAgg.objects.all()
    

    def list(self, request, *args, **kwargs):
        """
        Returns total number of assessments done in month/year wise.
        """
        queryset = self.filter_queryset(self.get_queryset())
        years = queryset.values_list('yearmonth', flat=True)
        years = set([year//100 for year in years])
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


class SurveyInfoSourceAPIView(AggMixin, ListAPIView, ILPStateMixin):
    filter_backends = [SurveyFilter, ]
    institution_queryset = SurveyInstitutionAgg.objects.all()
    boundary_queryset = SurveyBoundaryAgg.objects.all()
    eboundary_queryset = SurveyElectionBoundaryAgg.objects.all()

    def institution_qs(self):
        """
        Returns institution queryset filtered by boundary_id/state_id
        and filter_backend parameters. `self.institution_queryset` only
        returns institution queryset filtered by institution_id.See AggMixin.
        """
        state_id = BoundaryStateCode.objects.get(
            char_id=settings.ILP_STATE_ID).boundary_id
        boundary_id = self.request.query_params.get('boundary_id', state_id)
        institution_qs = SurveyInstitutionAgg.objects.filter(
                Q(institution_id__admin0_id=boundary_id) |
                Q(institution_id__admin1_id=boundary_id) |
                Q(institution_id__admin2_id=boundary_id) |
                Q(institution_id__admin3_id=boundary_id)
            )
        return self.filter_queryset(institution_qs)

    def get_qs_agg(self, queryset, source_id):
        """
        Returns querysets sum of num_assessments.
        """
        if self.request.query_params.get('institution_id', None):
            qs_agg = queryset.filter(source=source_id).aggregate(
                Sum('num_assessments')
            )
            qs_agg['num_schools__sum'] = 1
            return qs_agg
        qs_agg = queryset.filter(source=source_id).aggregate(
            Sum('num_assessments'),
        )
        return qs_agg

    def list(self, request, *args, **kwargs):
        """
        Returns schools_impacted, assessement_count and last_assessemnt
        in source wise.
        """
        queryset = self.filter_queryset(self.get_queryset())
        response = {}
        source_res = {}

        source_ids = queryset.distinct(
            'source').values_list('source', flat=True)

        for source_id in source_ids:
            source_name = "None"
            if source_id:
                source_name = Source.objects.get(id=source_id).name
            qs_agg = self.get_qs_agg(queryset, source_id)

            source_res[source_name] = {
                "schools_impacted": self.institution_qs().filter(
                    source=source_id).distinct('institution_id').count(),
                "assessment_count": qs_agg['num_assessments__sum'],
                "last_assessment": queryset.latest(
                    'last_assessment'
                ).last_assessment,
            }
        response['source'] = source_res
        return Response(response)


class SurveyInfoUserAPIView(AggMixin, ListAPIView, ILPStateMixin):
    filter_backends = [SurveyFilter, ]
    institution_queryset = SurveyInstitutionUserTypeAgg.objects.all()
    boundary_queryset = SurveyBoundaryUserTypeAgg.objects.all()

    def list(self, request, *args, **kwargs):
        """
        Returns sum of num_assessments in `user_type` wise.
        """
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
        AggMixin, ListAPIView, ILPStateMixin
):
    filter_backends = [SurveyFilter, ]
    institution_queryset = SurveyInstitutionRespondentTypeAgg.objects.all()
    boundary_queryset = SurveyBoundaryRespondentTypeAgg.objects.all()

    def list(self, request, *args, **kwargs):
        """
        Returns sum of num_assessments in `respondent_type` wise.
        """
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
        # Now find all survey ids who actually have
        # type_id assessment in questiongroup table
        surveys_assessment_types = QuestionGroup.objects.\
            filter(type__char_id='assessment').\
            filter(survey_id__in=survey_ids).\
            values_list('survey_id', flat=True)
        return Survey.objects.filter(id__in=surveys_assessment_types)


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


class SurveyDetailSourceAPIView(AggMixin, ListAPIView, ILPStateMixin):
    filter_backends = [SurveyFilter, ]
    institution_queryset = SurveyInstitutionQuestionGroupAnsAgg.objects.all()
    boundary_queryset = SurveyBoundaryQuestionGroupAnsAgg.objects.all()

    def list(self, request, *args, **kwargs):
        """
        Returns sources, and in each sources contains
        list of questions and answer details.
        [
            questions(key, display_text, text),
            answers(answer_option with total num of answers),
            question_type
        ].
        """
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
                ans_agg = question_agg.\
                    values('answer_option').annotate(Sum('num_answers'))
                for ans in ans_agg:
                    question_res['answers'][ans['answer_option']] = \
                        ans['num_answers__sum']
                question_list.append(question_res)
            sources_res[source.name] = question_list
        response["source"] = sources_res
        return Response(response)


class SurveyDetailKeyAPIView(AggMixin, ListAPIView, ILPStateMixin):
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
        response = {}
        scores_res = {}
        ans_qs = self.filter_queryset(self.get_answer_queryset())
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
        AggMixin, ListAPIView, ILPStateMixin
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
        """
        Returns studentgroups.
        Each studentgroup contains questionkey dicts.
        Each questionkey dict contains answer_total, answer_score.
        
        Question Keys is fetched from `self.get_queryset()` and,
        Question Keys Answer is fetched from `self.get_answer_queryset()`.
        """
        classes_res = {}
        qs = self.filter_queryset(self.get_queryset())
        ans_qs = self.filter_queryset(self.get_answer_queryset())

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
        AggMixin, ListAPIView, ILPStateMixin
):
    filter_backends = [SurveyFilter, ]
    institution_queryset = SurveyInstitutionQuestionGroupQuestionKeyAgg.\
        objects.all()
    boundary_queryset = SurveyBoundaryQuestionGroupQuestionKeyAgg.\
        objects.all()
    eboundary_queryset = SurveyEBoundaryQuestionGroupQuestionKeyAgg.\
        objects.all()

    def get_answer_queryset(self):
        institution_id = self.request.query_params.get('institution_id', None)
        boundary_id = self.request.query_params.get('boundary_id', None)
        eboundary_id = self.request.query_params.get('electionboundary_id', None)
        if institution_id:
            return SurveyInstitutionQuestionGroupQuestionKeyCorrectAnsAgg.\
                objects.filter(institution_id=institution_id)
        if boundary_id:
            return SurveyBoundaryQuestionGroupQuestionKeyCorrectAnsAgg.\
                objects.filter(boundary_id=boundary_id)
        if eboundary_id:
            return SurveyEBoundaryQuestionGroupQuestionKeyCorrectAnsAgg.\
                objects.filter(eboundary_id=eboundary_id)

        state_id = BoundaryStateCode.objects.get(
            char_id=settings.ILP_STATE_ID).boundary_id
        return SurveyBoundaryQuestionGroupQuestionKeyCorrectAnsAgg.objects.\
            filter(boundary_id=state_id)

    def list(self, request, *args, **kwargs):
        """
        Returns questiongroups.
        Each questiongroups contains questionkey dicts.
        Each questionkey dict contains answer_total, answer_score.

        Question Keys is fetched from `self.get_queryset()` and,
        Question Keys Answer is fetched from `self.get_answer_queryset()`.
        """
        qgroup_res = {}
        qs = self.filter_queryset(self.get_queryset())

        ans_qs = self.filter_queryset(self.get_answer_queryset())

        qgroups = qs.distinct('questiongroup_id')\
            .values_list('questiongroup_id', 'questiongroup_name')

        for qgroup_id, qgroup_name in qgroups:
            qgroup_qs = qs.filter(questiongroup_id=qgroup_id)
            qgroup_ans_qs = ans_qs.filter(questiongroup_id=qgroup_id)
            key_agg = qgroup_qs.values(
                'question_key').annotate(num_assess=Sum('num_assessments'))
            ans_key_agg = qgroup_ans_qs.values(
                'question_key').annotate(num_assess=Sum('num_assessments'))

            question_keys = key_agg.values_list('question_key', flat=True)           
            qgroup_res[qgroup_name] = qgroup_res.get(qgroup_name, {})

            for q_key in question_keys:
                total = key_agg.get(question_key=q_key)['num_assess']
                try:
                    score_qs = ans_key_agg.get(question_key=q_key)
                    score = score_qs['num_assess']
                except ObjectDoesNotExist:
                    score = 0
                order = CompetencyOrder.objects.get(
                    key=q_key, questiongroup_id=qgroup_id
                )
                if qgroup_res[qgroup_name].get(q_key, None):
                    qgroup_res[qgroup_name][q_key]["total"] += total
                    qgroup_res[qgroup_name][q_key]["score"] += score
                else:
                    qgroup_res[qgroup_name][q_key] = {
                        "total": total,
                        "score": score,
                        "order": order.sequence
                    }
        return Response(qgroup_res)


class SurveyInfoClassGenderAPIView(ListAPIView, ILPStateMixin):
    filter_backends = [SurveyFilter, ]

    def get_survey_type(self):
        survey_id = self.request.query_params.get('survey_id', None)
        return Survey.objects.get(id=survey_id).survey_on.char_id

    def get_queryset(self):
        """
        If survey_type is 'institution' returns
            - SurveyInstitutionQuestionGroupGenderAgg
            - SurveyBoundaryQuestionGroupGenderAgg
        If survey_type is 'studentgroup' returns
            - SurveyInstitutionClassGenderAgg
            - SurveyBoundaryClassGenderAgg
        """
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
            return SurveyBoundaryQuestionGroupGenderAgg.objects.filter(
                boundary_id=state_id)
        else:
            if institution_id:
                return SurveyInstitutionClassGenderAgg.objects.filter(
                    institution_id=institution_id)
            elif boundary_id:
                return SurveyBoundaryClassGenderAgg.objects.filter(
                    boundary_id=boundary_id)
            return SurveyBoundaryClassGenderAgg.objects.filter(
                boundary_id=state_id)

    def get_answer_queryset(self):
        """
        If survey_type is 'institution' returns
            - SurveyInstitutionQuestionGroupGenderCorrectAnsAgg
            - SurveyBoundaryQuestionGroupGenderCorrectAnsAgg
        If survey_type is 'studentgroup' returns
            - SurveyInstitutionClassGenderCorrectAnsAgg
            - SurveyBoundaryClassGenderCorrectAnsAgg
        """
        survey_type = self.get_survey_type()
        state_id = BoundaryStateCode.objects.get(
            char_id=settings.ILP_STATE_ID).boundary_id
        institution_id = self.request.query_params.get('institution_id', None)
        boundary_id = self.request.query_params.get('boundary_id', None)

        if survey_type == 'institution':
            if institution_id:
                return SurveyInstitutionQuestionGroupGenderCorrectAnsAgg.\
                    objects.filter(institution_id=institution_id)
            elif boundary_id:
                return SurveyBoundaryQuestionGroupGenderCorrectAnsAgg.\
                    objects.filter(boundary_id=boundary_id)
            return SurveyBoundaryQuestionGroupGenderCorrectAnsAgg.\
                objects.filter(boundary_id=state_id)
        elif survey_type == 'studentgroup':
            if institution_id:
                return SurveyInstitutionClassGenderCorrectAnsAgg.\
                    objects.filter(institution_id=institution_id)
            elif boundary_id:
                return SurveyBoundaryClassGenderCorrectAnsAgg.\
                    objects.filter(boundary_id=boundary_id)
            return SurveyBoundaryClassGenderCorrectAnsAgg.\
                objects.filter(boundary_id=state_id)

    def list(self, request, *args, **kwargs):
        """
        Returns Questiongroup name;
        Each QG contains Male and Female - total_count and perfect_score_count;

        `self.get_queryset()` returns GenderAgg.
        `self.get_answer_queryset()` returns GenderCorrectAnsAgg.
        """
        group_res = {}
        qs = self.filter_queryset(self.get_queryset())
        ans_qs = self.filter_queryset(self.get_answer_queryset())

        group_field = 'sg_name'
        if self.get_survey_type() == 'institution':
            group_field = 'questiongroup_name'

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
                    "total_count": gender_agg['num_assessments__sum'] or 0,
                    "perfect_score_count": gender_ans_agg[
                        'num_assessments__sum'] or 0
                }
            group_res[group_name] = {
                "gender": gender_res
            }
        return Response(group_res)


class SurveyDetailClassAPIView(AggMixin, ListAPIView, ILPStateMixin):
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

    def institution_qs(self):
        state_id = BoundaryStateCode.objects.get(
            char_id=settings.ILP_STATE_ID).boundary_id
        boundary_id = self.request.query_params.get('boundary_id', state_id)
        institution_qs = SurveyInstitutionAgg.objects.filter(
            Q(institution_id__admin0_id=boundary_id) |
            Q(institution_id__admin1_id=boundary_id) |
            Q(institution_id__admin2_id=boundary_id) |
            Q(institution_id__admin3_id=boundary_id)
        )
        return self.filter_queryset(institution_qs)

    def list(self, request, *args, **kwargs):
        boundary_id = self.request.query_params.get('boundary_id', None)
        queryset = self.filter_queryset(self.get_queryset())

        if boundary_id:
            queryset = queryset.filter(boundary_id=boundary_id)

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
                    Sum('num_children'),
                    Sum('num_assessments'),
                )

            boundary_res = {
                "id": b_type_id,
                "name": BoundaryType.objects.get(char_id=b_type_id).name,
                "schools_impacted": self.institution_qs().distinct(
                    'institution_id').count(),
                "children_impacted": boundary_qs_agg['num_children__sum'],
                "assessment_count": boundary_qs_agg['num_assessments__sum']
            }
            boundary_list.append(boundary_res)
            source_res[b_type_id] = boundary_list
        response['boundaries'] = source_res
        return Response(response)


class SurveyDetailEBoundaryAPIView(AggMixin, ListAPIView, ILPStateMixin):
    filter_backends = [SurveyFilter, ]
    boundary_queryset = SurveyBoundaryElectionTypeCount.objects.all()
    eboundary_queryset = SurveyEBoundaryElectionTypeCount.objects.all()
    institution_queryset = SurveyInstitutionElectionTypeCount.objects.all()

    def list(self, request, *args, **kwargs):
        boundary_id = self.request.GET.get('boundary_id', None)
        eboundary_id = self.request.query_params.get('electionboundary_id', None)

        queryset = self.filter_queryset(self.get_queryset())
        res = {}

        electioncount_agg = queryset.values('const_ward_type').annotate(
            Sum('electionboundary_count'))
        for electioncount in electioncount_agg:
            res[electioncount['const_ward_type']] = \
                electioncount['electionboundary_count__sum']
        return Response(res)


class SurveyQuestionGroupQDetailsAPIView(
        AggMixin, ListAPIView, ILPStateMixin
):
    filter_backends = [SurveyFilter, ]
    institution_queryset = SurveyInstitutionQuestionGroupQDetailsAgg.\
        objects.all()
    boundary_queryset = SurveyBoundaryQuestionGroupQDetailsAgg.\
        objects.all()
    eboundary_queryset = SurveyEBoundaryQuestionGroupQDetailsAgg.\
        objects.all()

    def get_answer_queryset(self):
        institution_id = self.request.query_params.get('institution_id', None)
        boundary_id = self.request.query_params.get('boundary_id', None)
        eboundary_id = self.request.query_params.get('electionboundary_id', None)
        if institution_id:
            return SurveyInstitutionQuestionGroupQDetailsCorrectAnsAgg.\
                objects.filter(institution_id=institution_id)
        if boundary_id:
            return SurveyBoundaryQuestionGroupQDetailsCorrectAnsAgg.\
                objects.filter(boundary_id=boundary_id)
        if eboundary_id:
            return SurveyEBoundaryQuestionGroupQDetailsCorrectAnsAgg.\
                objects.filter(eboundary_id=eboundary_id)

        state_id = BoundaryStateCode.objects.get(
            char_id=settings.ILP_STATE_ID).boundary_id
        return SurveyBoundaryQuestionGroupQDetailsCorrectAnsAgg.objects.\
            filter(boundary_id=state_id)

    def list(self, request, *args, **kwargs):
        """
        Returns questiongroups.
        Each questiongroups contains dicts.
        Each concept dict contains microconceptgroup dict that contains 
        microconcept dict that contains answer_total, answer_score.

        Question Details is fetched from `self.get_queryset()` and,
        Question Details  Answer is fetched from `self.get_answer_queryset()`.
        """
        qgroup_res = {}
        qs = self.filter_queryset(self.get_queryset())

        ans_qs = self.filter_queryset(self.get_answer_queryset())

        qgroups = qs.distinct('questiongroup_id')\
            .values_list('questiongroup_id', 'questiongroup_name')

        for qgroup_id, qgroup_name in qgroups:
            q_res = {}
            qgroup_qs = qs.filter(questiongroup_id=qgroup_id)
            qgroup_ans_qs = ans_qs.filter(questiongroup_id=qgroup_id)
            qdetails = qgroup_qs.values(
                'concept__description','microconcept_group__description','microconcept__description').annotate(
                    Sum('num_assessments'))
            ans_qdetails = qgroup_ans_qs.values(
                'concept__description','microconcept_group__description','microconcept__description').annotate(
                    Sum('num_assessments'))

            for row in qdetails:
                concept = row['concept__description']
                microconcept_group = row['microconcept_group__description']
                microconcept = row['microconcept__description']
                if concept in q_res:
                    if microconcept_group in q_res[concept]:
                        if microconcept in q_res[concept][microconcept_group]:
                            q_res[concept][microconcept_group][microconcept]["total"] += row['num_assessments__sum']
                            q_res[concept]["total"] += row['num_assessments__sum']
                            q_res[concept][microconcept_group]["total"] += row['num_assessments__sum']
                        else:
                            q_res[concept][microconcept_group][microconcept] = {"total": row['num_assessments__sum'], "score":0}
                            q_res[concept]["total"] += row['num_assessments__sum']
                            q_res[concept][microconcept_group]["total"] += row['num_assessments__sum']
                    else:
                        q_res[concept][microconcept_group] = {microconcept:{"total": row['num_assessments__sum'], "score":0}, "total":0, "score":0}
                        q_res[concept]["total"] += row['num_assessments__sum']
                        q_res[concept][microconcept_group]["total"] += row['num_assessments__sum']
                else:
                    q_res[concept] = {microconcept_group: {microconcept:{"total":row['num_assessments__sum'],"score":0},"total":0, "score":0}, "total":0, "score":0}
                    q_res[concept]["total"] += row['num_assessments__sum']
                    q_res[concept][microconcept_group]["total"] += row['num_assessments__sum']
 
            for row in ans_qdetails:
                concept = row['concept__description']
                microconcept_group = row['microconcept_group__description']
                microconcept = row['microconcept__description']
                if concept in q_res:
                    if microconcept_group in q_res[concept]:
                        if microconcept in q_res[concept][microconcept_group]:
                            q_res[concept][microconcept_group][microconcept]["score"] += row['num_assessments__sum']
                            q_res[concept]["score"] += row['num_assessments__sum']
                            q_res[concept][microconcept_group]["score"] += row['num_assessments__sum']
                        else:
                            q_res[concept][microconcept_group][microconcept] = {"score": row['num_assessments__sum'], "total":0}
                            q_res[concept]["score"] += row['num_assessments__sum']
                            q_res[concept][microconcept_group]["score"] += row['num_assessments__sum']
                    else:
                        q_res[concept][microconcept_group] = {microconcept:{"score": row['num_assessments__sum'], "total":0}, "total":0, "score":0}
                        q_res[concept]["score"] += row['num_assessments__sum']
                        q_res[concept][microconcept_group]["score"] += row['num_assessments__sum']
                else:
                    q_res[concept] = {microconcept_group: {microconcept:{"score":row['num_assessments__sum'],"total":0},"total":0, "score":0}, "total":0, "score":0}
                    q_res[concept]["score"] += row['num_assessments__sum']
                    q_res[concept][microconcept_group]["score"] += row['num_assessments__sum']
            qgroup_res[qgroup_name] = q_res
        return Response(qgroup_res)


class SurveyQuestionGroupQuestionKeyYearComparisonAPIView(
        AggMixin, ListAPIView, ILPStateMixin
):
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

    def getYearData(self, year, survey_id, survey_tag):
        qgroup_res = {} 
            
        qs = self.filter_queryset(self.get_queryset())
        if survey_id:
            qs = qs.filter(survey_id=survey_id)

        if survey_tag:
            qs = qs.filter(survey_tag=survey_tag)

        to_yearmonth = year.split('-')[1]+'04'
        from_yearmonth = year.split('-')[0]+'06'
        print('to_yearmonth: '+to_yearmonth+", from_yearmonth: "+from_yearmonth)
        qs = qs.filter(yearmonth__lte=to_yearmonth, yearmonth__gte=from_yearmonth)


        ans_qs = self.filter_queryset(self.get_answer_queryset())
        if survey_id:
            ans_qs = ans_qs.filter(survey_id=survey_id)

        if survey_tag:
            ans_qs = ans_qs.filter(survey_tag=survey_tag)

        ans_qs = ans_qs.filter(yearmonth__lte=to_yearmonth, yearmonth__gte=from_yearmonth)

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
                    score_qs = ans_key_agg.get(question_key=q_key)
                    score = score_qs['num_assess']
                except ObjectDoesNotExist:
                    score = 0
                q_res[q_key] = {
                    "total": total,
                    "score": score
                }
            qgroup_res[qgroup_name] = q_res
        return qgroup_res

    def list(self, request, *args, **kwargs):
        """
        Returns questiongroups.
        Each questiongroups contains questionkey dicts.
        Each questionkey dict contains answer_total, answer_score.

        Question Keys is fetched from `self.get_queryset()` and,
        Question Keys Answer is fetched from `self.get_answer_queryset()`.
        """
        qgroup_res = {}

        survey_tag = request.query_params.get('survey_tag', None)
        survey_id = request.query_params.get('survey_id', None)
        year = request.query_params.get('year', None)

        if year==None:
            raise ParseError("Mandatory param year is not passed.")
        
        startyear = int('20'+year[0]+year[1])
        endyear = int('20'+year[2]+year[3])
        current_year = str(startyear)+"-"+str(endyear)
        pre_startyear = int('20'+year[0]+year[1])-1
        pre_endyear = int('20'+year[2]+year[3])-1
        pre_year = str(pre_startyear)+"-"+str(pre_endyear)

        qgroup_res[current_year] = self.getYearData(current_year, survey_id, survey_tag)
        qgroup_res[pre_year] = self.getYearData(pre_year, survey_id, survey_tag)
        return Response(qgroup_res)


