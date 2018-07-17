import logging
from boundary.serializers import (
    BoundarySerializer, BoundaryWithParentSerializer
)
from boundary.models import (Boundary,
                             BasicBoundaryAgg,
                             BoundarySchoolCategoryAgg,
                             BoundarySchoolManagementAgg,
                             BoundaryStudentMotherTongueAgg,
                             BoundarySchoolMoiAgg,
                             BoundaryInstitutionGenderAgg)
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
        print("Academic year is: ", ac_year)
        ac_year = ac_year.replace('-', '')
        print("After replacement is: ", ac_year)
        try:
            academic_year = AcademicYear.objects.get(char_id=ac_year)
        except AcademicYear.DoesNotExist:
            raise APIException('Academic year is not valid. It should be in the form of 2011-2012.', 404)

        try:
            boundary = Boundary.objects.get(id=boundaryId)
        except Exception:
            raise APIException('Boundary not found', 404)

        boundaryAgg = BasicBoundaryAgg.objects.filter(boundary_id=boundaryId).get(year=ac_year)

        agg = {
            'num_schools': boundaryAgg.num_schools,
            'num_boys': boundaryAgg.num_boys,
            'num_girls': boundaryAgg.num_girls,
            'year': boundaryAgg.year.char_id,
         }
        # Calculate category aggregations
        boundaryCatAgg = BoundarySchoolCategoryAgg.objects.filter(boundary_id=boundaryId).filter(cat_ac_year=ac_year)
        if boundaryCatAgg is not None:
            cat = []
            print(boundaryCatAgg.values())
            for aggregate in boundaryCatAgg:
                aggregate = {
                    'cat': aggregate.cat_id,
                    'num_boys': aggregate.num_boys,
                    'num_girls': aggregate.num_girls,
                    'num_schools': aggregate.num_schools
                }
                cat.append(aggregate) # End of for-loop
            agg['cat'] = cat
        # End of If

        # Calculate management aggregations

        boundaryMgmtAgg = BoundarySchoolManagementAgg.objects.filter(boundary_id=boundaryId).filter(mgmt_ac_year=ac_year)
        if boundaryMgmtAgg is not None:
            mgmt = []
            for mgmtAgg in boundaryMgmtAgg:
                aggregate = {
                    'management': mgmtAgg.management,
                    'num_boys': mgmtAgg.num_boys,
                    'num_girls': mgmtAgg.num_girls,
                    'num_schools': mgmtAgg.num_schools
                }
                mgmt.append(aggregate) #End of for loop
            agg['management'] = mgmt
        # End of IF and adding management aggregations

        # Calculate mother tongue agg
        studentMtAgg = BoundaryStudentMotherTongueAgg.objects.filter(boundary_id=boundaryId).filter(mt_ac_year=ac_year)
        if studentMtAgg is not None:
            mtAgg = []
            for mt in studentMtAgg:
                result = {
                    'name': mt.mt_id,
                    'num_boys': mt.num_boys,
                    'num_girls': mt.num_girls,
                    'num_students': mt.num_students,
                    'num_schools': mt.num_schools
                }
                mtAgg.append(result)
            agg['mt'] = mtAgg
        # End of mother tongue calculations

        # Calculate medium of instruction agg
        moiAgg = BoundarySchoolMoiAgg.objects.filter(boundary_id=boundaryId).filter(moi_ac_year=ac_year)
        if moiAgg is not None:
            aggregation = []
            for moi in moiAgg:
                result = {
                    'name': moi.moi_id,
                    'num_boys': moi.num_boys,
                    'num_girls': moi.num_girls,
                    'num': moi.num_students,
                    'num_schools': moi.num_schools
                }
                aggregation.append(result)
            # End of for-loop
            agg['moi'] = aggregation
        # End of mother tongue calculations

        # Calculate gender agg
        genderAgg = BoundaryInstitutionGenderAgg.objects.filter(boundary_id=boundaryId).filter(gender_ac_year=ac_year)
        if genderAgg is not None:
            aggregation = []
            for gender in genderAgg:
                result = {
                    'sex': gender.gender_id,
                    'num': gender.num_students
                }
                aggregation.append(result)
            agg['gender'] = aggregation
        agg['boundary'] = BoundaryWithParentSerializer(boundary, context={'request': request}).data
        return Response(agg)
