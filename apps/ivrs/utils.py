import datetime

from rest_framework import status

from django.utils import timezone
from django.contrib.auth.models import Group

from .models import State, QuestionGroupType, IncomingNumber
from users.models import User
#from boundary.models import BoundaryType
from schools.models import Institution
from assessments.models import (
    Question, QuestionGroup,QuestionGroup_Questions
)


def get_message(parameters, **kwargs):
    if kwargs.get('is_data_valid', False):
        date = str(parameters['date'])
        data = str(parameters['raw_data'])
        message = "Response accepted. Your message was: " + data + \
                  " received at: " + date

    elif not kwargs.get('is_telephone_present', True):
        message = "The telephone is blank."

    elif not kwargs.get('is_institution_primary', True):
        message = "Please enter Primary Institution ID."

    elif not kwargs.get('is_data_valid', True):
        data = str(parameters['raw_data'])
        expected_response = "3885,1,1,1,2,2"

        message = "Error. Your response: " + data + \
                  ". Expected response: " + expected_response

    elif not kwargs.get('is_logically_correct', True):
        message = "Logical error."

    elif not kwargs.get('is_user_registered', True):
        telephone = str(parameters['telephone'])
        message = "Your number " + telephone + \
                  " is not registered. Please visit https://klp.org.in/" + \
                  " and register yourself."

    elif not kwargs.get('is_institution_id_valid', True):
        institution_id = str(parameters['institution_id'])
        message = "Institution ID " + institution_id + " not found."

    elif not kwargs.get('is_institution_primary', True):
        message = "Please enter Primary Institution ID."

    elif kwargs.get('error_question_number', False):
        data = str(parameters['raw_data'])
        question_number = str(kwargs['error_question_number'])
        message = "Error at que.no: " + question_number + "." + \
                  " Your response was " + data

    return message

def is_data_valid(data):
    is_valid = True

    # Making sure that each input is a valid digit and no alphabets get in.
    if not all(response.strip().isdigit() for response in data):
        is_valid = False
    elif len(data) == 5:
        if any(response == '' for response in data):
            # Responses like 1,2,1,,2 are not accepted.
            is_valid = False
    else:
        is_valid = False

    return is_valid

def validate_telephone_number(telephone):
    if not telephone.isdigit():
        return None

    telephone = telephone[1:] # Strip 0
    if not User.objects.filter(mobile_no__contains=telephone).exists():
        print("User is not registered")#do we need to create new user?
    return telephone
    

def is_logically_correct(data):
    is_logically_correct = True
    
    # Logical error for gkav4. 5 entries in total. List index starts from 0.
    if data[1] in ('2', '3'):
        if not all(answer in ('2', '3') for answer in data[2:]):
            is_logically_correct = False

    return is_logically_correct

def is_institution_exists(institution_id):
    institution_valid = False
    if institution_id.isdigit():
    	institution_valid =  Institution.objects.filter(id=institution_id).exists()
    return institution_valid

def is_institution_primary(institution_id):
    institution_type = Institution.objects.filter(
        id=institution_id
    ).values(
        'admin3_id__type_id'
    )[0]['admin3_id__type_id']
    return (institution_type == u'primary')

def is_answer_accepted(question, answer):
    is_answer_accepted = True
    if question.question_type.display_id in ['CheckBox', 'Radio']:
        checkbox_accepted_answers = {'1': 'Yes', '2': 'No', '3': 'Unknown'}
        if answer not in checkbox_accepted_answers:
            is_answer_accepted = False
        elif checkbox_accepted_answers[answer] not in eval(question.options):
            is_answer_accepted = False
    else:
        if answer not in eval(question.options):
            is_answer_accepted = False

    return is_answer_accepted

def cast_answer(question, answer):
    if question.question_type.display_id in ['CheckBox', 'Radio']:
        checkbox_accepted_answers = {'1': 'Yes', '2': 'No', '3': 'Unknown'}
        return checkbox_accepted_answers[answer]
    else:
        return answer

def process_data(data):
    return [item.strip() for item in data.split(',')]

def populate_answers_list(incoming_number):
    answers = []
    # Ignoring index 0 since question_numbers start from 1
    # Initializing answer slots 1 to number_of_questions with NA.
    # answer slot 0 has value IGNORED_INDEX pre populated.
    answers.append('IGNORED_INDEX')
    number_of_questions = incoming_number.qg_type.questiongroup.questions.all().count()
    for i in range(0, number_of_questions):
        answers.append('NA')
    return answers

def get_date(date):
    date = datetime.datetime.strptime(
        date, '%Y-%m-%d %H:%M:%S'
    )
    date = timezone.make_aware(
        date, timezone.get_current_timezone()
    )
    return date

def populate_state(parameters, message, answers, is_invalid=False):
    date = parameters.get('date', None)
    raw_data = parameters.get('raw_data', None)
    ivrs_type = parameters.get('ivrs_type', None)
    telephone = parameters.get('telephone', None)
    institution_id = parameters.get('institution_id', None)
    session_id = parameters.get('session_id', None)

    try:
        user = User.objects.get(mobile_no=telephone)
    except:
        user = None

    incoming_number = IncomingNumber.objects.get(number=ivrs_type)
    state, created = State.objects.get_or_create(
        session_id=session_id,
        qg_type=incoming_number.qg_type
    )
    state.user = user
    state.telephone = telephone
    state.date_of_visit = get_date(date.strip("'"))
    state.answers = answers

    if raw_data:
        state.raw_data = str(raw_data)

    if institution_id and institution_id.isdigit():
        state.school_id = institution_id 
    else:
        is_invalid=True

    state.comments = message
    state.is_invalid = is_invalid
    print ("the state is:", state)
    state.save()
    return state

def get_question(question_number, question_group):
    # We are directly querying for Primary School because we don't work
    # with PreSchools anymore. If we do so in the future, please make
    # sure you implement the logic here while fetching questions.
    return Question.objects.get(
        questiongroup=question_group,
        questiongroup_questions__sequence=question_number,
    )



