from django.contrib.auth.models import Group
from django.db.models import Count, Max, Sum

from common.views import ILPListAPIView
from common.utils import Date
from common.models import (
    InstitutionType, Status, AcademicYear,
)

from schools.models import (
    Institution, InstitutionStuGenderCount
)

from rest_framework.response import Response
from rest_framework.exceptions import APIException

from assessments.models import (
    QuestionGroup, AnswerGroup_Institution,
    Source, RespondentType, Survey
)


class QGroupAnswersMetaAPIView(ILPListAPIView):
    """
    Returns total number of stories(surverys) and schools with stories
    along with respondent types.
    """
    def get(self, request, *args, **kwargs):
        survey_id = kwargs['survey_id']
        qgroup_id = kwargs['qgroup_id']
        admin1_id = self.request.query_params.get('admin1', None)
        source = self.request.query_params.get('source', None)
        versions = self.request.query_params.getlist('version', None)

        institution_qs, agroup_inst_ids = \
            self.get_querysets(survey_id, qgroup_id)

        sources = Source.objects.all()
        if source:
            sources = sources.filter(name=source)
        sources = sources.values_list('name', flat=True)

        unique_inst_counts_per_source = agroup_inst_ids.values(
            'questiongroup__source__name'
        ).annotate(
            institution_count=Count('institution', distinct=True)
        )

        response_source = {}
        for source in sources:
            groups = QuestionGroup.objects.filter(source__name=source)
            agroup_inst_ids = agroup_inst_ids.filter(
                questiongroup__in=groups)

            if versions:
                versions = map(int, versions)
                agroup_inst_ids = agroup_inst_ids.filter(
                    questiongroup__version__in=versions)

            response_source[source] = self.get_json(
                source, agroup_inst_ids, unique_inst_counts_per_source
            )

        response_json = {}
        response_json['total'] = {
            'schools': institution_qs.count(),
            'stories': agroup_inst_ids.count(),
            'schools_with_stories':
                agroup_inst_ids.distinct('institution').count()
        }
        response_json['respondents'] = self.get_respondents(agroup_inst_ids)
        response_json['users'] = self.get_users(agroup_inst_ids)
        response_json['top_summary'] = \
            self.get_total_summary(
                institution_qs.count(), agroup_inst_ids, admin1_id
            )
        response_json.update(response_source)

        return Response(response_json)

    def get_querysets(self, survey_id, qgroup_id):
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
        qgroup = QuestionGroup.objects.get(
            id=qgroup_id, survey_id=survey_id
        )
        agroup_inst_ids = AnswerGroup_Institution.objects.filter(
            questiongroup=qgroup, institution__in=institution_qs
        ).values('id')

        if admin1_id:
            institution_qs = institution_qs.filter(admin1_id=admin1_id)
            agroup_inst_ids = agroup_inst_ids.filter(
                institution__admin1_id=admin1_id
            ).all()

        if admin2_id:
            institution_qs = institution_qs.filter(admin2_id=admin2_id)
            agroup_inst_ids = agroup_inst_ids.filter(
                institution__admin2_id=admin2_id
            ).all()

        if admin3_id:
            institution_qs = institution_qs.filter(admin3_id=admin3_id)
            agroup_inst_ids = agroup_inst_ids.filter(
                institution__admin3_id=admin3_id
            ).all()

        if mp_id:
            institution_qs = institution_qs.filter(admin2_id=admin2_id)
            agroup_inst_ids = agroup_inst_ids.filter(
                institution__admin2_id=admin2_id
            ).all()

        if institution_id:
            institution_qs = institution_qs.filter(id=institution_id)
            agroup_inst_ids = agroup_inst_ids.filter(
                institution_id=institution_id
            )

        if mla_id:
            institution_qs = institution_qs.filter(mla_id=mla_id)
            agroup_inst_ids = agroup_inst_ids.filter(
                institution__mla_id=mla_id
            ).all()

        if mp_id:
            institution_qs = institution_qs.filter(mp_id=mp_id)
            agroup_inst_ids = agroup_inst_ids.filter(
                institution__mp_id=mp_id
            ).all()

        # todo: Returns empty qs, need to look through,
        # maybe issue with the migrated data.
        if start_date:
            agroup_inst_ids = agroup_inst_ids.filter(
                date_of_visit__gte=start_date
            )

        if end_date:
            agroup_inst_ids = agroup_inst_ids.filter(
                date_of_visit__lte=end_date
            )

        return (institution_qs, agroup_inst_ids)

    def get_total_summary(
            self, inst_count, agroup_inst_ids,
            admin1_id=None, admin2_id=None, admin3_id=None
    ):

        survey = Survey.objects.get(name='Ganitha Kalika Andolana')
        gka_inst_ids = agroup_inst_ids.filter(questiongroup__survey=survey)

        # TODO:
        # if admin1_id:
        #     admin1 = Boundary.objects.get(id=admin1_id)
        # elif admin2_id:
        #     admin1 = Boundary.objects.get(id=admin2_id).parent
        # elif admin3_id:
        #     admin1 = Boundary.objects.get(id=admin3_id).parent.parent
        # else:
        #     admin1 = None

        # edu_vol_group = Group.objects.get(name="EV")
        # edu_volunteers = BoundaryUsers.objects.filter(
        #   user__groups=edu_vol_group)
        # if admin1:
        #     edu_volunteers = edu_volunteers.filter(boundary=admin1)

        academic_year = AcademicYear.objects.latest('char_id')
        num_boys = InstitutionStuGenderCount.objects.filter(
            academic_year=academic_year, institution__in=gka_inst_ids
        ).aggregate(Sum('num_boys'))['num_boys__sum']
        num_girls = InstitutionStuGenderCount.objects.filter(
            academic_year=academic_year, institution__in=gka_inst_ids
        ).aggregate(Sum('num_girls'))['num_girls__sum']

        if not num_boys:
            num_boys = 0

        if not num_girls:
            num_girls = 0

        return {
            'total_schools': inst_count,
            'gka_schools': gka_inst_ids.count(),
            'children_impacted': num_boys + num_girls,
            # 'education_volunteers': edu_volunteers.count()
        }

    def get_json(self, source, agroup_inst_ids, inst_counts):
        json = {}

        institution_count = 0
        for i in inst_counts:
            if i['questiongroup__source__name'] == source:
                institution_count = i['institution_count']
                break
            else:
                institution_count = 0
                continue

        json['stories'] = agroup_inst_ids.count()
        json['schools'] = institution_count

        if agroup_inst_ids:
            json['last_story'] = agroup_inst_ids.aggregate(
                Max('date_of_visit')
            )['date_of_visit__max']
        else:
            json['last_story'] = None

        if source == "web":
            json['verified_stories'] = agroup_inst_ids.filter(
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

    def get_users(self, agroup_inst_ids):
        users = {}
        groups = Group.objects.all()
        for group in groups:
            group_users = group.user_set.all()
            users[group.name] = agroup_inst_ids.filter(
                created_by__in=group_users
            ).count()

        return users

    def get_respondents(self, agroup_inst_ids):
        respondents = {}

        respondent_type_with_counts = agroup_inst_ids.values(
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
