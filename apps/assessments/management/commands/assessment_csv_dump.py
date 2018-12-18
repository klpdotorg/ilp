import csv

from django.core.management.base import BaseCommand
from assessments.models import(
    AnswerGroup_Institution,
    AnswerInstitution,
    QuestionGroup
)


class Command(BaseCommand):
    help = 'Generates CSV dump for assessment data'

    def handle(self, *args, **options):
        field_names = [
            'survey',
            'state',
            'district',
            'block',
            'cluster',
            'school',
            'institution_id',
            'dise_id',
            'assessment_id',
            'entered_at',
            'date_of_visit',
            'respondent_type',
            'question_group',
        ]
        question_groups = QuestionGroup.objects.filter(survey_id=11)
        for question_group in question_groups:
            questions = question_group.questions.all()
            for q in questions:
                if q.question_text not in field_names:
                    field_names.append(q.question_text)

        assessments = AnswerGroup_Institution.objects.filter(
            questiongroup__survey__id=11
        )

        with open('assessment_csv_dump.csv', mode='w') as csv_file:

            writer = csv.DictWriter(csv_file, fieldnames=field_names)
            writer.writeheader()

            for assessment in assessments:
                answers = assessment.answers.all()
                data_dict = {
                    'survey': assessment.questiongroup.survey.name,
                    'state': assessment.institution.admin0.name,
                    'district': assessment.institution.admin1.name,
                    'block': assessment.institution.admin2.name,
                    'cluster': assessment.institution.admin3.name,
                    'school': assessment.institution.name,
                    'institution_id': assessment.institution.id,
                    'dise_id': assessment.institution.dise.school_code if assessment.institution.dise is not None else '',
                    'assessment_id': assessment.id,
                    'entered_at': assessment.entered_at,
                    'date_of_visit': assessment.date_of_visit,
                    'respondent_type': assessment.respondent_type,
                    'question_group': assessment.questiongroup.name,
                }

                for answer in answers:
                    data_dict[answer.question.question_text] = answer.answer

                writer.writerow(data_dict)
