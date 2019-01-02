import pdfkit

from django.template.loader import render_to_string

from assessments.models import(
    AnswerGroup_Institution, AnswerInstitution,
    QuestionGroup
)


def get_assessment_field_names(survey_id):
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
    question_groups = QuestionGroup.objects.filter(survey_id=survey_id)
    for question_group in question_groups:
        questions = question_group.questions.all()
        for q in questions:
            if q.question_text not in field_names:
                field_names.append(q.question_text)
    return field_names


def get_assessment_field_data(survey_id):
    assessments = AnswerGroup_Institution.objects.filter(
        questiongroup__survey__id=survey_id
    )

    for assessment in assessments:
        answers = assessment.answers.all()
        field_data_dict = {
            'survey': assessment.questiongroup.survey.name,
            'state': assessment.institution.admin0.name,
            'district': assessment.institution.admin1.name,
            'block': assessment.institution.admin2.name,
            'cluster': assessment.institution.admin3.name,
            'school': assessment.institution.name,
            'institution_id': assessment.institution.id,
            'dise_id':
                assessment.institution.dise.school_code
                if assessment.institution.dise is not None else '',
            'assessment_id': assessment.id,
            'entered_at': assessment.entered_at,
            'date_of_visit': assessment.date_of_visit,
            'respondent_type': assessment.respondent_type,
            'question_group': assessment.questiongroup.name,
        }

        for answer in answers:
            field_data_dict[answer.question.question_text] = answer.answer

        return field_data_dict


def generate_pdf():
    template = 'backoffice/export_pdf.html'
    html = render_to_string(template, {'data': None})
    config = pdfkit.configuration()
    options = {'encoding': 'utf-8'}
    pdf = pdfkit.PDFKit(
        html, 'string', configuration=config, options=options).to_pdf()
    return pdf
