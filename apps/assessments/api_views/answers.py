from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from common.mixins import ILPStateMixin
from common.views import ILPViewSet

from assessments.models import (
    AnswerGroup_Institution, AnswerGroup_StudentGroup,
    AnswerGroup_Student
)
from assessments.serializers import (
    AnswerGroupInstSerializer, AnswerGroupStudentGroupSerializer,
    AnswerGroupStudentSerializer
)


# TODO: The following three view sets have not been
# linked to any URLs

class AnswerGroupInstViewSet(ILPViewSet, ILPStateMixin):
    queryset = AnswerGroup_Institution.objects.all()
    serializer_class = AnswerGroupInstSerializer


class AnswerGroupStudentGroupViewSet(ILPViewSet, ILPStateMixin):
    queryset = AnswerGroup_StudentGroup.objects.all()
    serializer_class = AnswerGroupStudentGroupSerializer


class AnswerGroupStudentViewSet(ILPViewSet, ILPStateMixin):
    queryset = AnswerGroup_Student.objects.all()
    serializer_class = AnswerGroupStudentSerializer


class SharedAssessmentsView(ListAPIView):
    """
        This view returns recent 6 assessments from our three assesment groups.
        The data is consumed in the ILP home page "Shared Stories" section.
    """

    def list(self, request, *args, **kwargs):
        inst = AnswerGroup_Institution.objects.all().order_by('-pk')[:6]
        st_group = AnswerGroup_StudentGroup.objects.all().order_by('-pk')[:6]
        st = AnswerGroup_Student.objects.all().order_by('-pk')[:6]

        return Response({
            'institutions': AnswerGroupInstSerializer(inst, many=True).data,
            'student_groups': AnswerGroupStudentGroupSerializer(
                st_group, many=True).data,
            'students': AnswerGroupStudentSerializer(st, many=True).data
        })
