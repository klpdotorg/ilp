import logging
from django.contrib.auth.models import Group
from django.db.models import Count, Max

from common.views import ILPListAPIView
from common.utils import Date
from common.models import InstitutionType, Status

from schools.models import Institution

from rest_framework.response import Response
from rest_framework.exceptions import APIException


from assessments.models import (Survey, QuestionGroup,
                                Question, QuestionGroup_Questions,
                                QuestionGroup_Institution_Association,
                                AnswerGroup_Institution,
                                AnswerInstitution, Source,
                                RespondentType)
from assessments.serializers import (SurveySerializer,
                                     QuestionGroupSerializer,
                                     QuestionSerializer,
                                     QuestionGroupQuestionSerializer,
                                     AnswerSerializer)
from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin
from common.mixins import ILPStateMixin
from common.views import ILPViewSet

logger = logging.getLogger(__name__)


class SurveysViewSet(ILPViewSet, ILPStateMixin):
    '''Returns all surveys'''
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    #filter_class = StudentGroupFilter


class QuestionGroupViewSet(NestedViewSetMixin, ILPStateMixin, 
                           viewsets.ModelViewSet):
    '''Returns all questiongroups belonging to a survey'''
    queryset = QuestionGroup.objects.all()
    serializer_class = QuestionGroupSerializer

    # M2M query returns duplicates. Overrode this function
    # from NestedViewSetMixin to implement the .distinct()
    def filter_queryset_by_parents_lookups(self, queryset):
        parents_query_dict = self.get_parents_query_dict()
        logger.debug("Arguments passed into view is: %s", parents_query_dict)
        if parents_query_dict:
            try:
                queryset = queryset.filter(
                    **parents_query_dict
                ).order_by().distinct('id')
            except ValueError:
                logger.exception(
                    ("Exception while filtering queryset based on dictionary."
                     "Params: %s, Queryset is: %s"),
                    parents_query_dict, queryset)
                raise Http404
        return queryset.order_by('id')


class QuestionViewSet(ILPStateMixin, viewsets.ModelViewSet):
    '''Return all questions'''
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class QuestionGroupQuestions(NestedViewSetMixin, ILPStateMixin,                                             viewsets.ModelViewSet):
    '''Returns all questions belonging to a questiongroup'''
    queryset = QuestionGroup_Questions.objects.all()
    serializer_class = QuestionGroupQuestionSerializer
    
    # M2M query returns duplicates. Overrode this function
    # from NestedViewSetMixin to implement the .distinct()
    def filter_queryset_by_parents_lookups(self, queryset):
        parents_query_dict = self.get_parents_query_dict()
        print("Arguments passed into QuestionGroupQuestions view is: %s",               parents_query_dict)
        questiongroup = parents_query_dict.get('questiongroup_id')
        print("Question group id is: ", questiongroup)
        if parents_query_dict:
            try:
                queryset = queryset.filter(
                    questiongroup_id=questiongroup
                ).order_by().distinct('id')
            except ValueError:
                logger.exception(
                    ("Exception while filtering queryset based on dictionary."
                     "Params: %s, Queryset is: %s"),
                    parents_query_dict, queryset)
                raise Http404
        return queryset.order_by('id')


# class QuestionGroupAnswers(NestedViewSetMixin, ILPStateMixin,
#                            viewsets.ModelViewSet):
#     queryset = QuestionGroup.objects.all()
#     serializer_class = AnswerSerializer
    
#     # M2M query returns duplicates. Overrode this function
#     # from NestedViewSetMixin to implement the .distinct()
#     def filter_queryset_by_parents_lookups(self, queryset):
#         parents_query_dict = self.get_parents_query_dict()
#         try:
#             questiongroup = parents_query_dict.get('questiongroup_id')
#             print("Question group id is: ", questiongroup)
#             qnGroup = QuestionGroup.objects.get(id=questiongroup)
#             surveyon = qnGroup.survey_on;
#             print('SurveyOnType object is: ', surveyon)
#             for x in surveyon.__dict__.keys():
#                 print(x)
#             if surveyon.char_id == 'institution':
#                 # Query the institution answergroup table
#                 print("Querying the institution answergroup table")
#                 answergroupinstitution = AnswerGroup_Institution.objects.filter(questiongroup=qnGroup)
#                 queryset = AnswerInstitution.objects.filter             (answergroup__in=answergroupinstitution)
#                 # queryset = answergroupinstitution.answerinstitution.all()
#                 print("Answer Groups is: ", answergroupinstitution.count())
#             elif surveyon.char_id == 'studentgroup':
#                 pass
            
#             elif surveyon.char_id == 'student':
#                 # Query the student answergroup table
#                 pass   
#         except ValueError:
#                 logger.exception(
#                     ("Exception while filtering queryset based on dictionary."
#                      "Params: %s, Queryset is: %s"),
#                     parents_query_dict, queryset)
#                 raise Http404  
#         return queryset.order_by("id")
    
class QGroupAnswerAPIView(ILPListAPIView):
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
        institution_qs, agroup_inst_qs = \
            self.get_querysets(survey_id, qgroup_id)

        sources = Source.objects.all()
        if source:
            sources = sources.filter(name=source)
        sources = sources.values_list('name', flat=True)

        unique_inst_counts_per_source = agroup_inst_qs.values(
            'questiongroup__source__name'
        ).annotate(
            institution_count=Count('institution', distinct=True)
        )

        response_source = {}
        for source in sources:
            groups = QuestionGroup.objects.filter(source__name=source)
            source_agroup_inst_qs = agroup_inst_qs.filter(
                questiongroup__in=groups)

            if versions:
                versions = map(int, versions)
                agroup_inst_qs = agroup_inst_qs.filter(
                    questiongroup__version__in=versions)

            response_source[source] = self.get_json(
                source, source_agroup_inst_qs, unique_inst_counts_per_source
            )

        response_json = {}
        response_json['total'] = {
            'schools': institution_qs.count(),
            'stories': agroup_inst_qs.count(),
            'schools_with_stories':
                agroup_inst_qs.distinct('institution').count()
        }
        response_json['respondents'] = self.get_respondents(agroup_inst_qs)
        response_json['users'] = self.get_users(agroup_inst_qs)
        response_json['top_summary'] = \
            self.get_total_summary(
                institution_qs.count(), institution_qs, admin1_id
            )
        response_json.update(response_source)

        return Response(response_json)

    def get_querysets(self, survey_id, qgroup_id):
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
        agroup_inst_qs = AnswerGroup_Institution.objects.filter(
            questiongroup=qgroup, institution__in=institution_qs
        ).values('id')

        if admin1_id:
            institution_qs = institution_qs.filter(admin1_id=admin1_id)
            agroup_inst_qs = agroup_inst_qs.filter(
                institution__admin1_id=admin1_id
            ).all()

        if admin2_id:
            institution_qs = institution_qs.filter(admin2_id=admin2_id)
            agroup_inst_qs = agroup_inst_qs.filter(
                institution__admin2_id=admin2_id
            ).all()

        if admin3_id:
            institution_qs = institution_qs.filter(admin3_id=admin3_id)
            agroup_inst_qs = agroup_inst_qs.filter(
                institution__admin3_id=admin3_id
            ).all()

        if mp_id:
            institution_qs = institution_qs.filter(admin2_id=admin2_id)
            agroup_inst_qs = agroup_inst_qs.filter(
                institution__admin2_id=admin2_id
            ).all()

        if school_id:
            institution_qs = institution_qs.filter(id=school_id)
            agroup_inst_qs = agroup_inst_qs.filter(
                institution_id=school_id
            )

        if mla_id:
            institution_qs = institution_qs.filter(mla_id=mla_id)
            agroup_inst_qs = agroup_inst_qs.filter(
                institution__mla_id=mla_id
            ).all()

        if mp_id:
            institution_qs = institution_qs.filter(mp_id=mp_id)
            agroup_inst_qs = agroup_inst_qs.filter(
                institution__mp_id=mp_id
            ).all()

        # todo: Returns empty qs, need to look through,
        # maybe issue with the migrated data.
        if start_date:
            agroup_inst_qs = agroup_inst_qs.filter(
                date_of_visit__gte=start_date
            )

        if end_date:
            agroup_inst_qs = agroup_inst_qs.filter(
                date_of_visit__lte=end_date
            )

        return (institution_qs, agroup_inst_qs)

    def get_total_summary(self, inst_count, inst_qs, admin1_id):
        pass
        # todo: Need to do once gka assessment is migrated.

        # programme = Survey.objects.get(name='Ganitha Kanika Andolana')
        # gka_school_q = inst_qs.filter(programmes=programme)

        # admin1 = None
        # if admin1_id:
        #     admin1 = Boundary.objects.get(hierarchy__name='district', id=admin1_id)
        # elif admin2_id:
        #     admin1 = Boundary.objects.get(hierarchy__name='block', id=admin2_id).parent
        # elif admin3_id:
        #     admin1 = Boundary.objects.get(hierarchy__name='cluster', id=admin3_id).parent.parent

        # edu_vol_group = Group.objects.get(name="EV")
        # edu_volunteers = BoundaryUsers.objects.filter(user__groups=edu_vol_group)
        # if admin1:
        #     edu_volunteers = edu_volunteers.filter(boundary=admin1)

        # academic_year = AcademicYear.objects.latest('id')
        # num_boys = SchoolExtra.objects.filter(
        #     academic_year=academic_year,
        #     school__in=gka_school_q
        # ).aggregate(Sum('num_boys'))['num_boys__sum']
        # num_girls = SchoolExtra.objects.filter(
        #     academic_year=academic_year,
        #     school__in=gka_school_q
        # ).aggregate(Sum('num_girls'))['num_girls__sum']

        # if not num_boys:
        #     num_boys = 0

        # if not num_girls:
        #     num_girls = 0

        # return {
        #     'total_schools': inst_count,
        #     'gka_schools': gka_school_q.count(),
        #     'children_impacted': num_boys + num_girls,
        #     'education_volunteers': edu_volunteers.count()
        # }

    def get_json(self, source, agroup_inst_qs, inst_counts):
        json = {}

        institution_count = 0
        for i in inst_counts:
            if i['questiongroup__source__name'] == source:
                institution_count = i['institution_count']
                break
            else:
                institution_count = 0
                continue

        json['stories'] = agroup_inst_qs.count()
        json['schools'] = institution_count

        if agroup_inst_qs:
            json['last_story'] = agroup_inst_qs.aggregate(
                Max('date_of_visit')
            )['date_of_visit__max']
        else:
            json['last_story'] = None

        if source == "web":
            json['verified_stories'] = agroup_inst_qs.filter(
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

    def get_users(self, agroup_inst_qs):
        users = {}
        groups = Group.objects.all()
        for group in groups:
            group_users = group.user_set.all()
            users[group.name] = agroup_inst_qs.filter(
                created_by__in=group_users
            ).count()

        return users

    def get_respondents(self, agroup_inst_qs):
        respondents = {}

        respondent_type_with_counts = agroup_inst_qs.values(
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
