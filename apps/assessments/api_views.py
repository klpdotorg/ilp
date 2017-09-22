from django.contrib.auth.models import Group
from django.db.models import Count, Max

from common.views import ILPListAPIView
from common.utils import Date
from common.models import InstitutionType, Status

from assessments.models import (
    AnswerGroup_Institution, QuestionGroup, Source,
    RespondentType
)

from schools.models import Institution


from rest_framework.response import Response
from rest_framework.exceptions import APIException


class StoryMetaView(ILPListAPIView):
    def get(self, request):
        survey = self.request.query_params.get('survey', None)
        source = self.request.query_params.get('source', None)
        versions = self.request.query_params.getlist('version', None)
        admin1_id = self.request.query_params.get('admin1', None)
        admin2_id = self.request.query_params.get('admin2', None)
        admin3_id = self.request.query_params.get('admin3', None)
        school_id = self.request.query_params.get('school_id', None)
        mp_id = self.request.query_params.get('mp_id', None)
        mla_id = self.request.query_params.get('mla_id', None)
        start_date = self.request.query_params.get('from', None)
        end_date = self.request.query_params.get('to', None)
        institution_type = self.request.query_params.get(
            'school_type', InstitutionType.PRIMARY_SCHOOL
        )
        top_summary = self.request.query_params.get('top_summary', None)
        date = Date()
        
        if start_date:
            sane = date.check_date_sanity(start_date)
            if not sane:
                raise APIException(
                    "Please enter `from` in the format YYYY-MM-DD")
            start_date = date.get_datetime(start_date)

        if end_date:
            sane = date.check_date_sanity(end_date)
            if not sane:
                raise APIException(
                    "Please enter `to` in the format YYYY-MM-DD")
            end_date = date.get_datetime(end_date)

        institution_qs = Institution.objects.filter(
            admin3__type=institution_type, status=Status.ACTIVE
        )
        ans_grp_inst_qs = AnswerGroup_Institution.objects.filter(
            institution__in=institution_qs
        ).values('id')

        if admin1_id:
            institution_qs = institution_qs.filter(admin1_id=admin1_id)
            ans_grp_inst_qs = ans_grp_inst_qs.filter(
                institution__admin1_id=admin1_id
            ).all()

        if admin2_id:
            institution_qs = institution_qs.filter(admin2_id=admin2_id)
            ans_grp_inst_qs = ans_grp_inst_qs.filter(
                institution__admin2_id=admin2_id
            ).all()

        if admin3_id:
            institution_qs = institution_qs.filter(admin3_id=admin3_id)
            ans_grp_inst_qs = ans_grp_inst_qs.filter(
                institution__admin3_id=admin3_id
            ).all()

        if mp_id:
            institution_qs = institution_qs.filter(admin2_id=admin2_id)
            ans_grp_inst_qs = ans_grp_inst_qs.filter(
                institution__admin2_id=admin2_id
            ).all()

        if school_id:
            institution_qs = institution_qs.filter(id=school_id)
            ans_grp_inst_qs = ans_grp_inst_qs.filter(
                institution_id=school_id
            )

        if mla_id:
            institution_qs = institution_qs.filter(mla_id=mla_id)
            ans_grp_inst_qs = ans_grp_inst_qs.filter(
                institution__mla_id=mla_id
            ).all()

        if mp_id:
            institution_qs = institution_qs.filter(mp_id=mp_id)
            ans_grp_inst_qs = ans_grp_inst_qs.filter(
                institution__mp_id=mp_id
            ).all()

        # TODO: Returns empty qs, need to look through.
        if start_date:
            ans_grp_inst_qs = ans_grp_inst_qs.filter(
                date_of_visit__gte=start_date
            )

        if end_date:
            ans_grp_inst_qs = ans_grp_inst_qs.filter(
                date_of_visit__lte=end_date
            )

        response_json = {}
        response_json['total'] = {}
        response_json['total']['schools'] = institution_qs.count()
        response_json['total']['stories'] = ans_grp_inst_qs.count()
        response_json['total']['schools_with_stories'] = \
            ans_grp_inst_qs.distinct('institution').count()

        if survey:
            ans_grp_inst_qs = ans_grp_inst_qs.filter(
                questiongroup__survery__name=survey
            )

        if source:
            groups = QuestionGroup.objects.filter(source__name=source)
            ans_grp_inst_qs = ans_grp_inst_qs.filter(
                questiongroup__in=groups
            )

            unique_inst_counts_per_source = [
                {
                    'qs_group__source__name': source,
                    'institution_count': ans_grp_inst_qs.aggregate(
                        Count('institution', distinct=True)
                    )['institution__count']
                }
            ]

            if versions:
                versions = map(int, versions)
                ans_grp_inst_qs = ans_grp_inst_qs.filter(
                    questiongroup__version__in=versions
                )

            response_json[source] = self.get_json(
                source, ans_grp_inst_qs, unique_inst_counts_per_source
            )
        else:
            sources = Source.objects.all().values_list('name', flat=True)

            unique_inst_counts_per_source = ans_grp_inst_qs.values(
                'questiongroup__source__name'
            ).annotate(
                school_count=Count(
                    'school',
                    distinct=True
                )
            )

            for source in sources:
                groups = QuestionGroup.objects.filter(source__name=source)
                ans_grp_inst_qs = ans_grp_inst_qs.filter(
                    questiongroup__in=groups
                )

                response_json[source] = self.get_json(
                    source, ans_grp_inst_qs, unique_inst_counts_per_source
                )

        response_json['respondents'] = self.get_respondents(ans_grp_inst_qs)
        response_json['users'] = self.get_users(ans_grp_inst_qs)

        return Response(response_json)

    def get_json(self, source, ans_grp_inst_qs, inst_counts):
        json = {}

        for i in inst_counts:
            if i['qs_group__source__name'] == source:
                institution_count = i['institution_count']
                break
            else:
                institution_count = 0
                continue

        json['stories'] = ans_grp_inst_qs.count()
        json['schools'] = institution_count

        if ans_grp_inst_qs:
            json['last_story'] = ans_grp_inst_qs.aggregate(
                Max('date_of_visit')
            )['date_of_visit__max']
        else:
            json['last_story'] = None

        if source == "web":
            json['verified_stories'] = ans_grp_inst_qs.filter(
                is_verified=True,
            ).count()
        elif source == "sms":
            gka_districts_queryset = AnswerGroup_Institution.objects.filter(
                questiongroup__source__name="sms"
            ).distinct(
                'institution__admin3__parent__parent'
            ).values(
                'institution__admin3__parent__parent__id',
                'institution__admin3__parent__parent__name'
            )
            old_id_key = 'institution__admin3__parent__parent__id'
            old_name_key = 'institution__admin3__parent__parent__name'

            json['gka_districts'] = [
                {
                    'id': item[old_id_key],
                    'name': item[old_name_key]
                }
                for item in gka_districts_queryset
            ]

        return json

    def get_users(self, ans_grp_inst_qs):
        users = {}
        groups = Group.objects.all()
        for group in groups:
            group_users = group.user_set.all()
            users[group.name] = ans_grp_inst_qs.filter(
                created_by__in=group_users
            ).count()

        return users

    def get_respondents(self, ans_grp_inst_qs):
        respondents = {}

        respondent_type_with_counts = ans_grp_inst_qs.values(
            'respondent_type__name').annotate(Count('respondent_type'))

        for respondent in respondent_type_with_counts:
            if not respondent['respondent_type__name']:
                continue
            else:
                respondents[
                    RespondentType.objects.get(
                        name=respondent['respondent_type__name']
                    ).name
                ] = respondent['respondent_type__count']
        return respondents
