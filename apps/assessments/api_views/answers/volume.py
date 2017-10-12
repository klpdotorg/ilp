import calendar

from collections import Counter, OrderedDict

from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404

from common.views import ILPListAPIView
from common.utils import Date
from common.models import InstitutionType, Status

from schools.models import Institution

from rest_framework.response import Response
from rest_framework.exceptions import APIException

from assessments.models import (
    QuestionGroup, AnswerGroup_Institution, AnswerGroup_Student
)


class QGroupAnswersVolumeAPIView(ILPListAPIView):
    """
    Returns the number of stories per month per year.
    """

    def get(self, request, *args, **kwargs):
        survey_id = kwargs['survey_id']
        qgroup_id = kwargs['qgroup_id']
        source = self.request.query_params.get('source', None)
        versions = self.request.query_params.getlist('version', None)
        admin1_id = self.request.query_params.get('admin1', None)
        admin2_id = self.request.query_params.get('admin2', None)
        admin3_id = self.request.query_params.get('admin3', None)
        institution_id = self.request.query_params.get('school_id', None)
        mp_id = self.request.query_params.get('mp_id', None)
        mla_id = self.request.query_params.get('mla_id', None)
        start_date = self.request.query_params.get('from', None)
        end_date = self.request.query_params.get('to', None)
        institution_type = self.request.query_params.get(
            'school_type', InstitutionType.PRIMARY_SCHOOL
        )
        response_type = self.request.query_params.get(
            'response_type', 'call_volume')

        date = Date()
        if start_date:
            sane = date.check_date_sanity(start_date)
            if not sane:
                raise APIException(
                    "Please enter `from` in the format YYYY-MM-DD")
            else:
                start_date = date.get_datetime(start_date)

        if end_date:
            sane = date.check_date_sanity(end_date)
            if not sane:
                raise APIException(
                    "Please enter `to` in the format YYYY-MM-DD")
            else:
                end_date = date.get_datetime(end_date)

        response_json = {}
        response_json['user_groups'] = {}

        institution_qs = Institution.objects.filter(
            admin3__type=institution_type, status=Status.ACTIVE)
        qgroup = get_object_or_404(
            QuestionGroup, id=qgroup_id, survey_id=survey_id)
        agroup_inst_qs = AnswerGroup_Institution.objects.filter(
            questiongroup=qgroup, institution__in=institution_qs)

        agroup_stud_qs = AnswerGroup_Student.objects.filter()

        if source:
            agroup_inst_qs = agroup_inst_qs.filter(
                questiongroup__source__name=source)

        if versions:
            versions = map(int, versions)
            agroup_inst_qs = agroup_inst_qs.filter(
                questiongroup__version__in=versions)

        if admin1_id:
            agroup_inst_qs = agroup_inst_qs.filter(
                institution__admin1_id=admin1_id)
            agroup_stud_qs = agroup_stud_qs.filter(
                student__institution__admin1_id=admin1_id)

        if admin2_id:
            agroup_inst_qs = agroup_inst_qs.filter(
                institution__admin2_id=admin2_id)
            agroup_stud_qs = agroup_stud_qs.filter(
                student__institution__admin2_id=admin2_id)

        if admin3_id:
            agroup_inst_qs = agroup_inst_qs.filter(
                institution__admin3_id=admin3_id)
            agroup_stud_qs = agroup_stud_qs.filter(
                student__institution__admin3_id=admin3_id)

        if institution_id:
            agroup_inst_qs = agroup_inst_qs.filter(
                institution_id=institution_id)
            agroup_stud_qs = agroup_stud_qs.filter(
                student__institution_id=institution_id)

        if mp_id:
            agroup_inst_qs = agroup_inst_qs.filter(
                institution__mp_id=mp_id)

        if mla_id:
            agroup_inst_qs = agroup_inst_qs.filter(
                institution__mla_id=mla_id)

        if start_date:
            agroup_inst_qs = agroup_inst_qs.filter(
                date_of_visit__gte=start_date)
            agroup_stud_qs = agroup_stud_qs.filter(
                date_of_visit__gte=start_date)

        if end_date:
            agroup_inst_qs = agroup_inst_qs.filter(
                date_of_visit__lte=end_date)
            agroup_stud_qs = agroup_stud_qs.filter(
                date_of_visit__lte=end_date)

        if response_type == 'call_volume':
            dates = agroup_inst_qs.\
                values_list('date_of_visit', flat=True).order_by()
            groups = Group.objects.all()
            for group in groups:
                response_json['user_groups'][group.name] = \
                    agroup_inst_qs.filter(
                        user__in=group.user_set.all()
                    ).count()
        else:
            dates = agroup_stud_qs.values_list('date_of_visit', flat=True)
            response_json['user_groups'] = {}

        response_json['volumes'] = self.get_call_volume(dates)

        return Response(response_json)

    def get_call_volume(self, dates):
        months = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
        json = {}
        for date in dates:
            if date.year in json:
                json[date.year].append(date.month)
            else:
                json[date.year] = []
                json[date.year].append(date.month)

        per_month_json = {}
        for year in json:
            per_month_json[year] = dict(Counter(
                [calendar.month_abbr[date] for date in json[year]])
            )

        ordered_per_month_json = {}
        for year in per_month_json:
            ordered_per_month_json[year] = OrderedDict()
            for month in months:
                ordered_per_month_json[year][month] = \
                    per_month_json[year].get(month, 0)

        return ordered_per_month_json
