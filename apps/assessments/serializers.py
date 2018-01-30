from rest_framework import serializers

from common.serializers import ILPSerializer
from common.mixins import CompensationLogMixin

from assessments.models import (
    Survey, QuestionGroup, Question, QuestionType,
    QuestionGroup_Questions, AnswerGroup_Institution,
    AnswerInstitution, SurveyOnType,
    AnswerGroup_StudentGroup, AnswerGroup_Student,
    QuestionGroup_Institution_Association,
    AnswerStudent
)

from common.models import RespondentType


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
            'id', 'name', 'survey', 'type', 'inst_type',
            'group_text', 'start_date', 'end_date', 'academic_year',
            'version', 'source', 'double_entry', 'created_by', 'created_at',
            'updated_at', 'status'
        )


class OptionField(serializers.Field):
    "Custom optionfield: {Yes,No} -> [Yes, No]"

    def to_representation(self, obj):
        return obj.lstrip('{').rstrip('}').split(',')


class QuestionSerializer(ILPSerializer):
    options = OptionField(required=False)
    question_type_id = serializers.IntegerField(write_only=True)
    question_type = serializers.CharField(
        read_only=True, source="question_type.display.char_id")

    class Meta:
        model = Question
        fields = (
            'question_text', 'display_text', 'key', 'question_type',
            'options', 'is_featured', 'status', 'id', 'question_type_id'
        )


class QuestionGroupQuestionSerializer(ILPSerializer):
    question_details = QuestionSerializer(source='question')

    class Meta:
        model = QuestionGroup_Questions
        fields = (
            'question_details',
        )

    def create(self, validated_data):
        question_dict = validated_data['question']
        questiongroup_id = self.context['questiongroup']
        question = Question.objects.create(**question_dict)
        return QuestionGroup_Questions.objects.create(
            questiongroup_id=questiongroup_id, question=question
        )


class QuestionGroupInstitutionSerializer(ILPSerializer):
    class Meta:
        model = QuestionGroup_Institution_Association
        fields = (
            'questiongroup', 'institution', 'id', 'status'
        )


class AnswerSerializer(ILPSerializer, CompensationLogMixin):
    answergroup = serializers.PrimaryKeyRelatedField(
        queryset=AnswerGroup_Institution.objects.all(),
        source="answergroup_id")

    class Meta:
        model = AnswerInstitution
        fields = ('id', 'question', 'answer', 'answergroup', 'double_entry')

    def create(self, validated_data):
        # This whole code block is a bit suspect. Not sure why this is needed!
        answergroup = validated_data.pop('answergroup_id')
        validated_data['answergroup_id'] = answergroup.id
        return AnswerInstitution.objects.create(**validated_data)


class AnswerGroupInstSerializer(serializers.ModelSerializer):
    double_entry = serializers.SerializerMethodField()
    comments = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = AnswerGroup_Institution
        fields = (
            'id', 'double_entry','questiongroup', 'institution', 'group_value',
            'created_by', 'date_of_visit',
            'respondent_type', 'comments', 'is_verified',
            'status', 'sysid', 'entered_at'
        )

    def get_double_entry(self, obj):
        return obj.questiongroup.double_entry


class AnswerGroupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerGroup_Institution


class AnswerGroupStudentGroupSerializer(ILPSerializer):
    class Meta:
        model = AnswerGroup_StudentGroup
        fields = '__all__'


class AnswerGroupStudentSerializer(serializers.ModelSerializer):
    double_entry = serializers.SerializerMethodField(required=False)
    comments = serializers.CharField(required=False)

    class Meta:
        model = AnswerGroup_Student
        fields = (
            'id', 'questiongroup', 'student', 'group_value',
            'created_by', 'date_of_visit',
            'respondent_type', 'comments', 'is_verified',
            'status', 'double_entry'
        )

    def get_double_entry(self, obj):
        return obj.questiongroup.double_entry


class AnswerGroupStudentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerGroup_Student
        fields = (
            'student', 'questiongroup', 'group_value',
            'created_by', 'date_of_visit', 'respondent_type',
            'is_verified', 'status', 'comments'
        )


class StudentAnswerSerializer(ILPSerializer, CompensationLogMixin):
    answergroup = serializers.PrimaryKeyRelatedField(
        queryset=AnswerGroup_Student.objects.all(), source="answergroup_id")

    class Meta:
        model = AnswerStudent
        fields = ('id', 'question', 'answer', 'answergroup', 'double_entry')

    def create(self, validated_data):
        # This whole code block is a bit suspect. Not sure why this is needed!
        answergroup = validated_data.pop('answergroup_id')
        validated_data['answergroup_id'] = answergroup.id
        return AnswerStudent.objects.create(**validated_data)
#       return instance


class RespondentTypeSerializer(ILPSerializer):
    class Meta:
        model = RespondentType
        fields = '__all__'
