from common.serializers import ILPSerializer
from assessments.models import (
    Survey, QuestionGroup, Question,
    QuestionGroup_Questions, AnswerGroup_Institution,
    AnswerInstitution, SurveyOnType
)


class SurveyOnTypeSerializer(ILPSerializer):

    class Meta:
        model = SurveyOnType
        fields = (
            'char_id', 'description'
        )


class SurveySerializer(ILPSerializer):
    class Meta:
        model = Survey
        fields = (
            'id', 'name', 'created_at', 'updated_at', 'partner', 'description',
            'status'
        )


class QuestionGroupSerializer(ILPSerializer):
    class Meta:
        model = QuestionGroup
        fields = (
            'id', 'name', 'survey', 'type', 'inst_type', 'survey_on',
            'group_text', 'start_date', 'end_date', 'academic_year',
            'version', 'source', 'double_entry', 'created_by', 'created_at',
            'updated_at', 'status'
        )


class QuestionSerializer(ILPSerializer):
    class Meta:
        model = Question
        fields = (
            'question_text', 'display_text', 'key', 'question_type',
            'options', 'is_featured', 'status'
        )


class QuestionGroupQuestionSerializer(ILPSerializer):
    question_details = QuestionSerializer(source='question')
    
    class Meta:
        model = QuestionGroup_Questions
        fields = (
            'question_details', 
        )


class AnswerGroupInstSerializer(ILPSerializer):
    class Meta:
        model = AnswerGroup_Institution
        fields = (
            'id', 'questiongroup', 'institution', 'group_value',
            'double_entry', 'created_by', 'date_of_visit',
            'respondent_type', 'comments', 'is_verified',
            'status', 'sysid', 'entered_at'
        )


class AnswerSerializer(ILPSerializer):
    answergrpdetails = AnswerGroupInstSerializer(source='answergroup')

    class Meta:
        model = AnswerInstitution
        fields = ('question', 'answer', 'answergrpdetails')
