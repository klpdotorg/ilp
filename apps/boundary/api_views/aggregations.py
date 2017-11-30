import logging
from boundary.serializers import (
    BoundarySerializer, BoundaryWithParentSerializer
)
from boundary.models import (Boundary, 
                             BasicBoundaryAgg)
from common.views import ILPAPIView
from common.models import AcademicYear
from rest_framework.exceptions import APIException
from django.conf import settings
from rest_framework.response import Response

logger = logging.getLogger(__name__)

class BaseBoundaryAggView():

    def get_aggregations(self, boundaryAgg):
        # boundaryAgg = BasicBoundaryAgg.objects.filter(boundary=boundaryId).get(year=acYear)
         agg = {
            'num_schools': boundaryAgg.num_schools,
            'num_boys': boundaryAgg.num_boys,
            'num_girls': boundaryAgg.num_girls,
            'year': boundaryAgg.year,
            'boundary': boundaryAgg
         }
         return agg

class BasicBoundaryAggView(ILPAPIView):

    def get(self, request, *args, **kwargs):
        # boundaryAgg = BasicBoundaryAgg.objects.filter(boundary=boundaryId).get(year=acYear)
        boundaryId = kwargs['id']
        ac_year = request.GET.get('year', settings.DEFAULT_ACADEMIC_YEAR)

        try:
            academic_year = AcademicYear.objects.get(char_id=ac_year)
        except AcademicYear.DoesNotExist:
            raise APIError('Academic year is not valid. It should be in the form of 2011-2012.', 404)

        try:
            boundary = Boundary.objects.get(id=boundaryId)
        except Exception:
            raise APIError('Boundary not found', 404)
        
        boundaryAgg = BasicBoundaryAgg.objects.filter(boundary_id=boundaryId).get(year=ac_year)

        agg = {
            'num_schools': boundaryAgg.num_schools,
            'num_boys': boundaryAgg.num_boys,
            'num_girls': boundaryAgg.num_girls,
            'year': boundaryAgg.year,
         }

        agg['boundary'] = BoundaryWithParentSerializer(boundary, context={'request': request}).data
        return Response(agg)