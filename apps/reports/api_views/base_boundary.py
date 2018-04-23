from boundary.models import Boundary, BasicBoundaryAgg, BoundaryNeighbours, BoundarySchoolCategoryAgg, BoundarySchoolMoiAgg, BoundaryStudentMotherTongueAgg
from . import BaseReport
from django.db.models import Sum


class BaseBoundaryReport(BaseReport):

    def get_boundary_basiccounts(self, boundary, academic_year):
        boundarycounts = {"num_schools": 0, "num_students": 0, "gender": {"girls": 0, "boys": 0}}
        print(academic_year.year)
        qs = BasicBoundaryAgg.objects.filter(boundary_id=boundary, year=academic_year).first()
        if qs:
            boundarycounts["num_schools"] = qs.num_schools
            boundarycounts["num_students"] = qs.num_students
            boundarycounts["gender"] = {"girls": qs.num_girls, "boys": qs.num_boys}
        return boundarycounts

    def get_boundary_details(self, boundary, academic_year):
        retdata = {"cat": {}, "mt": {}, "moi": {}}

        qs = BoundarySchoolCategoryAgg.objects.filter(boundary=boundary, cat_ac_year=academic_year, institution_type='primary').values("cat").annotate(num_schools=Sum('num_schools'), num_students=Sum('num_students'), num_boys=Sum('num_boys'), num_girls=Sum('num_girls'))
        if qs is None:
            return retdata
        for data in qs:
            retdata["cat"][data["cat"]] = {"cat": data["cat"], "num_schools": data["num_schools"], "num_students": data["num_students"]}

        qs = BoundarySchoolMoiAgg.objects.filter(boundary=boundary, moi_ac_year=academic_year).values("moi").annotate(num_schools=Sum('num_schools'), num_students=Sum('num_students'))
        if qs is None:
            return retdata
        for data in qs:
            retdata["moi"][data["moi"]] = {"moi": data["moi"], "num_schools": data["num_schools"], "num_students": data["num_students"]}

        qs = BoundaryStudentMotherTongueAgg.objects.filter(boundary=boundary, mt_ac_year=academic_year).values("mt").annotate(num_schools=Sum('num_schools'), num_students=Sum('num_students'))
        if qs is None:
            return retdata
        for data in qs:
            retdata["mt"][data["mt"]] = {"mt": data["mt"], "num_schools": data["num_schools"], "num_students": data["num_students"]}

        return retdata

    # Get dise information for the boundary
    def get_dise_school_info(self, active_schools, academic_year):
        dise_schools = active_schools  # TODO.filter(acyear=academic_year)
        agg = {
            'num_schools': dise_schools.count(),
            'gender': {'boys': dise_schools.aggregate(
                                num_boys=Sum('boys_count'))['num_boys'],
                       'girls': dise_schools.aggregate(
                                num_girls=Sum('girls_count'))['num_girls']
                       },
            'teacher_count': dise_schools.aggregate(
                                num_teachers=Sum('teacher_count'))['num_teachers']
        }
        agg['num_students'] = agg['gender']['boys'] + agg['gender']['girls']
        return agg

    # Returns the count of schools in the parent boundary, if the passed boundary
    # is district then returns the count of schools in all the districts
    def get_parent_info(self, boundary):
        parent = {"schoolcount": 0}
        if boundary.boundary_type_id != 'SD':
            parentObject = Boundary.objects.filter(id=boundary.parent.id).first()
            if parentObject:
                schools = parentObject.schools()
                parent["schoolcount"] = schools.count()
        else:
            neighbourlist = BoundaryNeighbours.objects.filter(boundary=boundary).values_list("neighbour_id", flat=True)
            if neighbourlist:
                neighbours = Boundary.objects.filter(id__in=list(neighbourlist))
                if neighbours:
                    for neighbour in neighbours:
                        count = neighbour.schools().count()
                        parent["schoolcount"] += count
        return parent

    def getDistrictNeighbours(self, boundary):
        neighbourlist = BoundaryNeighbours.objects.filter(boundary=boundary).values_list("neighbour_id", flat=True)
        neighbours = Boundary.objects.filter(id__in=list(neighbourlist))
        return neighbours

    # Returns the basic information of the pased boundary
    def get_boundary_summary_data(self, boundary, reportData):
        reportData["report_info"] = {}
        reportData["report_info"]["name"] = boundary.name
        reportData["report_info"]["type"] = boundary.boundary_type.name
        reportData["report_info"]["id"] = boundary.id
        reportData["report_info"]["parent"] = []
        reportData["report_info"]["btype"] = boundary.type_id
        reportData["report_info"]["dise"] = boundary.dise_slug
        if boundary.boundary_type_id == 'SB':
            reportData["report_info"]["parent"] = [{
                "type": boundary.parent.boundary_type.name,
                "name": boundary.parent.name,
                "dise": boundary.parent.dise_slug}]
        elif boundary.boundary_type_id == 'SC':
            reportData["report_info"]["parent"] = [{
                "type": boundary.parent.parent.boundary_type.name,
                "name": boundary.parent.parent.name,
                "dise": boundary.parent.parent.dise_slug}, {
                "type": boundary.parent.boundary_type.name,
                "name": boundary.parent.name,
                "dise": boundary.parent.dise_slug}
                ]
