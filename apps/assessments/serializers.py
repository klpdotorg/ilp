from common.serializers import ILPSerializer
from rest_framework import serializers
from assessments.models import (
    Survey, QuestionGroup, Question,
    QuestionGroup_Questions, AnswerGroup_Institution,
    AnswerInstitution, SurveyOnType,
    AnswerGroup_StudentGroup, AnswerGroup_Student
)
from common.mixins import (
                           CompensationLogMixin,
                           AnswerUpdateModelMixin)
from rest_framework import serializers
from easyaudit.models import CRUDEvent



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
            'options', 'is_featured', 'status', 'id'
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


class AnswerSerializer(ILPSerializer, CompensationLogMixin):
    answergroup = serializers.PrimaryKeyRelatedField(queryset=AnswerGroup_Institution.objects.all(), source="answergroup_id")

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
    institution_name = serializers.CharField(source='institution.name')
    name = serializers.CharField(source='created_by.username')

    class Meta:
        model = AnswerGroup_Institution
        fields = (
            'id', 'double_entry','questiongroup', 'institution', 'group_value',
            'created_by', 'date_of_visit',
            'respondent_type', 'comments', 'is_verified',
            'status', 'sysid', 'entered_at', 'name', 'institution_name'
        )

    def get_double_entry(self, obj):
        return obj.questiongroup.double_entry


class AnswerGroupStudentGroupSerializer(ILPSerializer):
    class Meta:
        model = AnswerGroup_StudentGroup
        fields = '__all__'


class AnswerGroupStudentSerializer(ILPSerializer):
    class Meta:
        model = AnswerGroup_Student
        fields = '__all__'


# class AnswerSerializer(ILPSerializer, CompensationLogMixin):
#    #  answergrpdetails = AnswerGroupInstSerializer(source='answergroup')

#     class Meta:
#         model = AnswerInstitution
#         fields = ('id', 'question', 'answer', 'double_entry')

#     def create(self, validated_data):
#        print("Inside AnswerSerializer create:", validated_data)
#        return AnswerInstitution.objects.create(**validated_data)

# class AnswerGroupInstSerializer(serializers.ModelSerializer):
#     answers = AnswerSerializer(many="True")
#     double_entry = serializers.SerializerMethodField()

#     class Meta:
#         model = AnswerGroup_Institution
#         fields = (
#             'id', 'double_entry','questiongroup', 'institution', 'group_value',
#             'created_by', 'date_of_visit',
#             'respondent_type', 'comments', 'is_verified',
#             'status', 'sysid', 'entered_at', 'answers'
#         )
    
#     def get_double_entry(self, obj):
#         return obj.questiongroup.double_entry
        
#     def create(self, validated_data):
#         # Remove the answers field first so we can create AnswerGroup_Institution object
#         print("Inside answergroup inst serializer CREATE")
#         answers = validated_data.pop('answers')
#         answergroup_obj = AnswerGroup_Institution.objects.create(**validated_data)
#         print("Answer group object is: ", answergroup_obj)
#         # Loop through the answers and create/link them properly
#         for answer in answers:
#             print("Quesiton id is: ", answer['question'].id)
#             answerdata={
#                 'answergroup': answergroup_obj,
#                 'question': answer['question'].id,
#                 'answer': answer['answer']
#             }
#             if(answergroup_obj.questiongroup.double_entry == True):
#                 answerdata['double_entry'] = 1
#                 print("Double entry is 1")
#             print("Answer data to be created is: ", answerdata)
#             answer = AnswerSerializer(data=answerdata)
#             answer.is_valid(raise_exception=True)
#             answer.save(answergroup=answergroup_obj)
#             print("Answer object is:", answer.data)
#         return answergroup_obj

#     def update(self, instance, validated_data):
#         instance.double_entry = validated_data.get('double_entry',instance.double_entry)
#         instance.questiongroup = validated_data.get('questiongroup', instance.questiongroup)
#         instance.institution = validated_data.get('institution', instance.institution)
#         instance.group_value = validated_data.get('group_value', instance.group_value)
#         #  'created_by', 'date_of_visit',
#         # 'respondent_type', 'comments', 'is_verified',
#         # 'status', 'sysid', 'entered_at', 'answers'
#         instance.date_of_visit = validated_data.get('date_of_visit', instance.date_of_visit)
#         instance.respondent_type = validated_data.get('respondent_type', instance.respondent_type)
#         instance.comments = validated_data.get('comments', instance.comments)
#         instance.is_verified = validated_data.get('is_verified', instance.is_verified)
#         instance.status = validated_data.get('status', instance.status)
#         instance.sysid = validated_data.get('sysid', instance.sysid)
#         instance.entered_at = validated_data.get('entered_at', instance.entered_at)
#         instance.save()

#         answers = validated_data.pop('answers')

#         # A new answer may be added for an existing answergroup
#         for answer in answers:
#             print("Quesiton id is: ", answer['question'].id)
#             answerdata={
#                 'answergroup': instance,
#                 'question': answer['question'].id,
#                 'answer': answer['answer']
#             }
#             answerObj, created = AnswerInstitution.objects.get_or_create(**answerdata)
#             if not created:
#                 print("Answer exists. Updating")
#                 answerObj.answer = answer['answer']
#                 answerObj.question = answer['question'].id
#                 answerObj.save()
#             else:
#                 print("Answer created and linked")
#                 pass
        
#         return instance
