from rest_framework import serializers

from common.serializers import ILPSerializer
from common.mixins import CompensationLogMixin

from assessments.models import (
    Survey, QuestionGroup, Question, QuestionType,
    QuestionGroup_Questions, AnswerGroup_Institution,
    AnswerInstitution, SurveyOnType,
    AnswerGroup_StudentGroup, AnswerGroup_Student,
    QuestionGroup_Institution_Association,
    AnswerStudent, QuestionGroup_StudentGroup_Association,
    QuestionGroup_Institution_Association,
    SurveyUserTypeMapping
)
from boundary.models import BoundaryNeighbours
from common.models import RespondentType


class SurveyOnTypeSerializer(ILPSerializer):

    class Meta:
        model = SurveyOnType
        fields = (
            'char_id', 'description'
        )


class QuestionGroupSerializer(ILPSerializer):
    source_name = serializers.ReadOnlyField(source='source.name')

    class Meta:
        model = QuestionGroup
        fields = (
            'id', 'name', 'survey', 'type', 'inst_type',
            'group_text', 'start_date', 'end_date', 'academic_year',
            'version', 'source', 'source_name', 'double_entry',
            'created_by', 'created_at', 'updated_at', 'status',
            'image_required', 'comments_required', 'lang_name',
        )


class SurveyCreateSerializer(ILPSerializer):
    class Meta:
        model = Survey
        fields = '__all__'

    def create(self, validated_data):
        new_id = Survey.objects.latest('id').id + 1
        return Survey.objects.create(id=new_id, **validated_data)


class SurveyUserTypeMappingSerializer(ILPSerializer):
    class Meta:
        model = SurveyUserTypeMapping
        fields = '__all__'


class SurveySerializer(ILPSerializer):
    state = serializers.ReadOnlyField(source='admin0.name')
    questiongroups = serializers.SerializerMethodField()
    user_types = SurveyUserTypeMappingSerializer(
        source='surveyusertypemapping_set',
        many=True,
        read_only=True
    )

    class Meta:
        model = Survey
        fields = (
            'id',
            'name',
            'lang_name',
            'created_at',
            'updated_at',
            'partner',
            'description',
            'status',
            'state',
            'questiongroups',
            'user_types',
        )

    def get_questiongroups(self, survey):
        status = self.context['request'].query_params.get('status', None)
        if status is None:
            return QuestionGroupSerializer(
                survey.questiongroup_set, many=True
            ).data
        else:
            return QuestionGroupSerializer(
                survey.questiongroup_set.filter(status__char_id=status),
                many=True
            ).data


class OptionField(serializers.Field):
    "Custom optionfield: {Yes,No} -> [Yes, No]"

    def to_representation(self, obj):
        return obj.lstrip('{').rstrip('}').split(',')


class QuestionSerializer(ILPSerializer):
    options = OptionField(required=False)
    question_type_id = serializers.IntegerField(write_only=True)
    question_type = serializers.CharField(
        read_only=True, source="question_type.display.char_id")
    sequence = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = (
            'question_text', 'display_text', 'key', 'question_type',
            'options', 'is_featured', 'status', 'id', 'question_type_id',
            'lang_name', 'sequence', 'lang_options',
        )

    def get_sequence(self, question):
        try:
            qgroup = self.context['request'].parser_context['kwargs'].get(
                'parent_lookup_questiongroup'
            )
            questiongroup_question = QuestionGroup_Questions.objects.get(
                question=question,
                questiongroup__id=qgroup
            )
        except Exception as e:
            print(e)
            return 0
        else:
            return questiongroup_question.sequence


class QuestionGroupQuestionSerializer(ILPSerializer):
    question_details = QuestionSerializer(source='question')

    class Meta:
        model = QuestionGroup_Questions
        fields = (
            'question_details', 'sequence'
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
    institution_name = serializers.SerializerMethodField()
    created_by_username = serializers.SerializerMethodField()

    class Meta:
        model = AnswerGroup_Institution
        fields = (
            'id', 'double_entry','questiongroup', 'institution', 'institution_name', 'group_value',
            'created_by', 'created_by_username', 'date_of_visit',
            'respondent_type', 'comments', 'is_verified',
            'status', 'sysid', 'entered_at'
        )

    def get_created_by_username(self, obj):
        username=''
        if obj is not None and obj.created_by is not None and obj.created_by.first_name is not None: 
            username = username + obj.created_by.first_name
        if obj is not None and obj.created_by is not None and obj.created_by.last_name is not None:
            username = username + ' ' + obj.created_by.last_name
        # if username is None:
        #     username = obj.created_by.email
        return username

    def get_institution_name(self, obj):
        return obj.institution.name

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


class QuestionGroupInstitutionAssociationSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuestionGroup_Institution_Association
        fields = (
                'questiongroup', 'institution', 'status',
        )


class QuestionGroupStudentGroupAssociationSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuestionGroup_StudentGroup_Association
        fields = (
                'questiongroup', 'studentgroup', 'status',
        )
