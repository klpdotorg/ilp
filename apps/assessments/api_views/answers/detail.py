from django.db.models import Count

from common.views import ILPListAPIView
from common.models import InstitutionType
from common.utils import Date

from schools.models import Institution
from boundary.models import Boundary

from rest_framework.response import Response
from rest_framework.exceptions import APIException

from assessments.models import (
    QuestionGroup, AnswerGroup_Institution,
    Source, Question, AnswerInstitution,
    QuestionGroup_Questions
)

from .gp_contest import GPContest


class QGroupAnswersDetailAPIView(ILPListAPIView):
    """
    Returns questions and their corresponding answers.
    """

    def get(self, request, *args, **kwargs):
        survey_id = kwargs['survey_id']
        qgroup_id = kwargs['qgroup_id']
        gka_comparison = self.request.query_params.get('gka_comparison', None)
        survey = self.request.query_params.get('survey', None)
        source = self.request.query_params.get('source', None)
        versions = self.request.query_params.getlist('version', None)
        admin1_id = self.request.query_params.get('admin1', None)
        admin2_id = self.request.query_params.get('admin2', None)
        admin3_id = self.request.query_params.get('admin3', None)
        institution_id = self.request.query_params.get('school_id', None)
        mp_id = self.request.query_params.get('mp_id', None)
        mla_id = self.request.query_params.get('mla_id', None)
        start_date = self.request.query_params.get('from', None)
        end_date = self.request.query_params.get('to', None)
        institution_type = self.request.query_params.get(
            'school_type', InstitutionType.PRIMARY_SCHOOL
        )

        date = Date()
        if start_date:
            sane = date.check_date_sanity(start_date)
            if not sane:
                raise APIException(
                    "Please enter `from` in the format YYYY-MM-DD")
            else:
                start_date = date.get_datetime(start_date)

        if end_date:
            sane = date.check_date_sanity(end_date)
            if not sane:
                raise APIException(
                    "Please enter `to` in the format YYYY-MM-DD")
            else:
                end_date = date.get_datetime(end_date)

        qgroup = QuestionGroup.objects.get(
            id=qgroup_id, survey_id=survey_id
        )
        agroup_inst_ids = AnswerGroup_Institution.objects.filter(
            questiongroup=qgroup
        ).values('id')

        if source:
            agroup_inst_ids = agroup_inst_ids.filter(
                questiongroup__source__name=source)

        if versions:
            versions = map(int, versions)
            agroup_inst_ids = agroup_inst_ids.filter(
                questiongroup__version__in=versions)

        if institution_type:
            agroup_inst_ids = agroup_inst_ids.filter(
                institution__admin3__type=institution_type)

        if admin1_id:
            agroup_inst_ids = agroup_inst_ids.filter(
                institution__admin1_id=admin1_id
            )
            boundary = Boundary.objects.get(id=admin1_id)

        if admin2_id:
            agroup_inst_ids = agroup_inst_ids.filter(
                institution__admin2_id=admin2_id
            )
            boundary = Boundary.objects.get(id=admin2_id)

        if admin3_id:
            agroup_inst_ids = agroup_inst_ids.filter(
                institution__admin3_id=admin3_id
            )
            boundary = Boundary.objects.get(id=admin3_id)

        if institution_id:
            institution = Institution.objects.get(id=institution_id)
            agroup_inst_ids = agroup_inst_ids.filter(
                institution=institution)

        if mp_id:
            agroup_inst_ids = agroup_inst_ids.filter(
                institution__mp_id=mp_id)

        if mla_id:
            agroup_inst_ids = agroup_inst_ids.filter(
                institution__mla_id=mla_id)

        if start_date:
            agroup_inst_ids = agroup_inst_ids.filter(
                date_of_visit__gte=start_date)

        if end_date:
            agroup_inst_ids = agroup_inst_ids.filter(
                date_of_visit__lte=end_date)

        response_json = {}

        if gka_comparison:
            gka = GKA(start_date, end_date)
            response_json = gka.generate_report(
                boundary, institution)
        elif survey == "GPContest":
            gp_contest = GPContest()
            response_json = gp_contest.generate_report(agroup_inst_ids)
        else:
            sources = Source.objects.all()
            if source:
                sources = sources.filter(name=source)
            sources = sources.values_list('name', flat=True)

        for source in sources:
            response_json[source] = get_que_and_ans(
                agroup_inst_ids, source, institution_type, versions)

        return Response(response_json)


def get_que_and_ans(agroup_inst_ids, source, institution_type, versions):
    response_list = []

    qgroup_questions = QuestionGroup_Questions.objects.filter(
        question__is_featured=True)

    if source:
        qgroup_questions = qgroup_questions.filter(
            questiongroup__source__name=source)

    if versions:
        qgroup_questions = qgroup_questions.filter(
            questiongroup__version__in=versions)

    # if institution_type:
    #     qgroup_questions = qgroup_questions.filter(
    #         questiongroup__inst_type__name=institution_type
    #     )

    answers = AnswerInstitution.objects.filter(
        answergroup__in=agroup_inst_ids)
    answer_counts = answers\
        .values('question', 'answer')\
        .annotate(Count('answer'))

    question_dict = {}
    question_ids = qgroup_questions.values_list('question_id', flat=True)

    for entry in answer_counts:
        if entry['question'] in question_ids:
            if entry['question'] in question_dict:
                question_dict[
                    entry['question']]['answers']['options'][entry['answer']]\
                     = entry['answer__count']
            else:
                question = Question.objects.get(id=entry['question'])
                question_dict[question.id] = {}
                question_dict[question.id]['question'] = {
                    'key': question.key,
                    'text': question.question_text,
                    'display_text': question.display_text,
                }
                question_dict[question.id]['answers'] = {
                    'question_type': question.question_type.display.char_id,
                    'options': {
                        entry['answer']: entry['answer__count']
                    }
                }

    for qgroup_question in qgroup_questions:
        j = {}
        if qgroup_question.question.id not in question_dict:
            j['question'] = {
                'key': qgroup_question.question.key,
                'text': qgroup_question.question.question_text,
                'display_text': qgroup_question.question.display_text
            }
            j['answers'] = {
                'question_type': (
                    qgroup_question.question.question_type.display.char_id),
                'options': {}
            }
        else:
            j = question_dict[question.id]
        response_list.append(j)

    return response_list
