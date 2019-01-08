from assessments.models import(
    AnswerGroup_Institution, QuestionGroup
)


def get_assessment_field_names(survey):
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
    question_groups = QuestionGroup.objects.filter(survey=survey)
    for question_group in question_groups:
        questions = question_group.questions.all()
        for q in questions:
            if q.question_text not in field_names:
                field_names.append(q.question_text)
    return field_names


def get_assessment_field_data(
        survey, admin1=None, admin2=None, admin3=None,
        institution=None, year=None, month=None
):
    assessments = AnswerGroup_Institution.objects.filter(
        questiongroup__survey=survey
    )
    if admin1:
        assessments = assessments.filter(institution__admin1=admin1)
    if admin2:
        assessments = assessments.filter(institution__admin2=admin2)
    if admin3:
        assessments = assessments.filter(institution__admin3=admin3)
    if institution:
        assessments = assessments.filter(institution=institution)
    if year:
        assessments = assessments.filter(date_of_visit__year=year)
    if month:
        assessments = assessments.filter(date_of_visit__month=month)

    field_data = []
    for assessment in assessments:
        answers = assessment.answers.all()
        field_datum = {
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
            field_datum[answer.question.question_text] = answer.answer
        field_data.append(field_datum)
    return field_data
