from rest_framework import serializers
from common.serializers import ILPSerializer
from assessments.models import (Survey, QuestionGroup)


class SurveySerializer(ILPSerializer):
    class Meta:
        model = Survey
        fields = (
            'name', 'created_at', 'updated_at', 'partner', 'description',
            'status'
        )


class QuestionGroupSerializer(ILPSerializer):
    class Meta:
        model = QuestionGroup
        fields = (
            'name', 'survey', 'type', 'inst_type', 'survey_on',
            'group_text', 'start_date', 'end_date', 'academic_year',
            'version', 'source', 'double_entry', 'created_by', 'created_at',
            'updated_at', 'status'
        )

