from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response

from boundary.serializers import (
    BoundarySerializer, BoundaryWithParentSerializer
)
from boundary.models import Boundary, BoundaryType
from boundary.filters import BoundarySurveyFilter

from common.views import ILPListAPIView, ILPDetailAPIView
from common.models import (
    InstitutionType,
    Status,
    RespondentType
)
from common.serializers import RespondentTypeSerializer
from common.mixins import ILPStateMixin
from common.filters import ILPInBBOXFilter
from common.state_codes import STATES


class Admin1sBoundary(ILPListAPIView, ILPStateMixin):
    serializer_class = BoundarySerializer
    filter_backends = [BoundarySurveyFilter, ]

    def get_queryset(self):
        state = self.get_state()
        queryset = Boundary.objects.filter(parent=state.id)
        school_type = self.request.query_params.get('school_type', None)
        boundarytype = BoundaryType.SCHOOL_DISTRICT
        if school_type is not None:
            # Hack to accomodate KLP dubdubdub URLs
            if school_type == "primaryschools":
                school_type = InstitutionType.PRIMARY_SCHOOL
            elif school_type == "preschools":
                school_type = InstitutionType.PRE_SCHOOL
            # End of hack
            queryset = queryset.filter(type=school_type)
            if school_type == InstitutionType.PRE_SCHOOL:
                boundarytype = BoundaryType.PRESCHOOL_DISTRICT
            queryset = queryset.filter(boundary_type__exact=boundarytype)
        else:
            queryset = queryset.filter(
                Q(boundary_type=BoundaryType.SCHOOL_DISTRICT) |
                Q(boundary_type=BoundaryType.PRESCHOOL_DISTRICT)
            )
        return queryset


class TestAdmin1sBoundary(ILPListAPIView, ILPStateMixin):
    serializer_class = BoundarySerializer

    def get_queryset(self):
        state = self.get_state()
        queryset = Boundary.objects.filter(parent=state.id)
        school_type = self.request.query_params.get('school_type', None)
        boundarytype = BoundaryType.SCHOOL_DISTRICT
        if school_type is not None:
            # Hack to accomodate KLP dubdubdub URLs
            if school_type == "primaryschools":
                school_type = InstitutionType.PRIMARY_SCHOOL
            elif school_type == "preschools":
                school_type = InstitutionType.PRE_SCHOOL
            # End of hack
            queryset = queryset.filter(type=school_type)
            if school_type == InstitutionType.PRE_SCHOOL:
                boundarytype = BoundaryType.PRESCHOOL_DISTRICT
            queryset = queryset.filter(boundary_type__exact=boundarytype)
        else:
            queryset = queryset.filter(
                Q(boundary_type=BoundaryType.SCHOOL_DISTRICT) |
                Q(boundary_type=BoundaryType.PRESCHOOL_DISTRICT)
            )
        return queryset


class Admin2sBoundary(ILPListAPIView, ILPStateMixin):
    serializer_class = BoundaryWithParentSerializer
    filter_backends = [BoundarySurveyFilter, ILPInBBOXFilter]
    
    def get_queryset(self):
        # Get all the admin2 boundary ids for a particular state as a list
        admin2boundaries = self.get_state_boundaries().\
            values_list('admin2_id', flat=True).distinct()
        # Now, filter boundary table ids which are there in the above list and
        # then look for Blocks or clusters
        result = Boundary.objects.filter(id__in=admin2boundaries).filter(
            Q(boundary_type=BoundaryType.SCHOOL_BLOCK) |
            Q(boundary_type=BoundaryType.PRESCHOOL_PROJECT))
        school_type = self.request.query_params.get('school_type', None)
        if school_type is not None:
            # Hack to accomodate KLP dubdubdub URLs
            if school_type == "primaryschools":
                school_type = InstitutionType.PRIMARY_SCHOOL
            elif school_type == "preschools":
                school_type = InstitutionType.PRE_SCHOOL
            # END OF HACK
            boundary_type = BoundaryType.SCHOOL_BLOCK
            result = result.filter(type=school_type)
            if school_type == InstitutionType.PRE_SCHOOL:
                boundary_type = BoundaryType.PRESCHOOL_PROJECT
            result = result.filter(boundary_type__exact=boundary_type)
        return result


class Admin3sBoundary(ILPListAPIView, ILPStateMixin):
    serializer_class = BoundaryWithParentSerializer
    filter_backends = [BoundarySurveyFilter, ]

    def get_queryset(self):
        # Get all the admin2 boundary ids for a particular state as a list
        admin3boundaries = self.get_state_boundaries()\
            .values_list('admin3_id', flat=True)

        # Now, filter boundary table ids which are there in the above list
        # and then look for Blocks or clusters
        queryset = Boundary.objects.filter(id__in=admin3boundaries)
        school_type = self.request.query_params.get('school_type', None)
        boundary_type = BoundaryType.SCHOOL_CLUSTER
        if school_type is not None:
            # Hack to accomodate KLP dubdubdub URLs
            if school_type == "primaryschools":
                school_type = InstitutionType.PRIMARY_SCHOOL
            elif school_type == "preschools":
                school_type = InstitutionType.PRE_SCHOOL
            # END OF HACK
            queryset = queryset.filter(type=school_type)
            if school_type == InstitutionType.PRE_SCHOOL:
                boundary_type = BoundaryType.PRESCHOOL_CIRCLE
            queryset = queryset.filter(boundary_type__exact=boundary_type)
        else:
            queryset = queryset.filter(
                Q(boundary_type=BoundaryType.SCHOOL_CLUSTER) |
                Q(boundary_type=BoundaryType.PRESCHOOL_CIRCLE))
        return queryset


class Admin2sInsideAdmin1(ILPListAPIView):
    ''' Returns a list of all blocks/projects inside a given district id '''
    serializer_class = BoundaryWithParentSerializer
    filter_backends = [BoundarySurveyFilter, ]

    def get_queryset(self):
        parent_district_id = self.kwargs.get('id', 0)
        return Boundary.objects.filter(
            parent=parent_district_id, status=Status.ACTIVE
        )


class Admin3sInsideAdmin1(ILPListAPIView):
    '''
    Returns a list of all clusters/circles inside a given pre or
    primary district.
    '''
    serializer_class = BoundaryWithParentSerializer
    filter_backends = [BoundarySurveyFilter, ]

    def get_queryset(self):
        parent_district_id = self.kwargs.get('id', 0)
        return Boundary.objects.filter(
            parent__parent=parent_district_id,
            status=Status.ACTIVE
        )


class Admin3sInsideAdmin2(ILPListAPIView):
    '''
    Returns a list of all clusters/circles inside a given block/project id
    '''
    serializer_class = BoundaryWithParentSerializer
    filter_backends = [BoundarySurveyFilter, ]

    def get_queryset(self):
        admin2_id = self.kwargs.get('id', 0)
        return Boundary.objects.filter(
            parent=admin2_id, status=Status.ACTIVE
        )


# Note: need to add cachemixin later in the params.
# Commenting because of error in console about cache setting not enabled
class AdminDetails(ILPDetailAPIView):
    """
    Returns details for a particular admin level
    bbox - Bounding box to search within
        e.g. 77.349415,12.822471,77.904224,14.130930
    """
    serializer_class = BoundaryWithParentSerializer
    bbox_filter_field = 'geom'
    lookup_url_kwarg = 'id'

    def get_queryset(self):
        return Boundary.objects.all_active()


class StateList(APIView):
    """
        Returns a list of states and their names, logos etc
        A web/mobile client can use this info to dynamically brand
        itself for different states.
    """

    def get_respondent_types(self, state=None):
        """ Returns respondent types of a state.
            If no state is passed, this function will return common types
        """
        respondent_types = RespondentType.objects.filter(state_code=state)
        return RespondentTypeSerializer(respondent_types, many=True).data

    def get(self, request):

        # Konnect expects the below data in a certain format
        # So we have to build a response in the format -
        # {
        #     'results': [
        #         {
        #             'name':
        #             ...
        #         }
        #     ]
        # }
        states = []

        for s in STATES:
            # First get the common respondent types
            STATES[s]['respondent_types'] = self.get_respondent_types()
            # Now get the state only respondent types
            STATES[s]['respondent_types'] += self.get_respondent_types(s)

            states.append(STATES[s])

        return Response({'results': states})
