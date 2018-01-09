import os

from rest_framework import status
from rest_framework.response import Response

from django.conf import settings
from .models import State, IncomingNumber
from .utils import (
    cast_answer,
    get_message,
    get_question,
    is_answer_accepted,
    is_data_valid,
    is_logically_correct,
    is_institution_exists,
    is_institution_primary,
    populate_state,
    populate_answers_list,
    process_data,
    validate_telephone_number
)

from schools.models import Institution
from common.views import ILPAPIView

class SMSView(ILPAPIView):
    def get(self, request):
        # In the SMS functionality of exotel, it expects a 200 response for all
        # its requests if it is to send the 'body' of your response as an sms
        # reply to the sender. Hence you will find places below where
        # status.HTTP_200_OK has been hardcoded in the response.
        content_type = "text/plain"

        telephone = validate_telephone_number(
            request.query_params.get('From', None)
        )

        if not telephone:
            return Response(
                "Invalid phone number.",
                status=status.HTTP_200_OK,
                content_type=content_type
        )
        
        parameters = {}
        parameters['telephone'] = telephone
        parameters['date'] = request.query_params.get('Date', None)
        parameters['ivrs_type'] = request.query_params.get('To', None)
        parameters['raw_data'] = request.query_params.get('Body', None)
        parameters['session_id'] = request.query_params.get('SmsSid', None)

        processed_data = process_data(parameters['raw_data'])
        incoming_number = IncomingNumber.objects.get(number=parameters['ivrs_type'])
        institution_id = processed_data.pop(0)
        answers = populate_answers_list(incoming_number)
        parameters['institution_id'] = institution_id 

        is_invalid = True
	
        if not is_data_valid(processed_data):
            message = get_message(parameters, is_data_valid=False)

        elif not is_logically_correct(processed_data):
            message = get_message(parameters, is_logically_correct=False)
      
        elif not is_institution_exists(institution_id): 
            message = get_message(parameters, is_institution_id_valid=False)

        # Since we are working only with primary schools. Deprecate if
        # preschools come into picture.
        elif not is_institution_primary(institution_id): 
            message = get_message(parameters, is_institution_primary=False)

        else:
            for question_number, answer in enumerate(processed_data):
                # Add 1 to question_number since it starts from 0.
                q_no = question_number + 1
                question = get_question(q_no, incoming_number.qg_type.questiongroup)
                if not is_answer_accepted(question, answer):
                    # If we find any of the answers are corrupt, we return an error response.
                    message = get_message(parameters, error_question_number=q_no)
                    break
                else:
                    answer = cast_answer(question, answer)
                answers[q_no] = answer
            else:
                is_invalid = False
                message = get_message(parameters, is_data_valid=True)

        state = populate_state(parameters, message, answers, is_invalid=is_invalid)

        return Response(
            message,
            status=status.HTTP_200_OK,
            content_type=content_type
        )


