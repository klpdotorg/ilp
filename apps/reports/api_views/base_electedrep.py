from boundary.models import ElectionBoundary, BasicElectionBoundaryAgg, ElectionBoundarySchoolCategoryAgg, ElectionBoundarySchoolMoiAgg, ElectionBoundaryStudentMotherTongueAgg
from rest_framework.exceptions import APIException
from django.db.models import Sum
from . import BaseReport


class BaseElectedRepReport(BaseReport):

    def get_electionboundary_basiccounts(self, electedrepid, academic_year):
        electionboundarycounts = {"num_schools":0, "num_students":0, "gender":{"girls":0, "boys":0}}
        print(academic_year.year)
        qs = BasicElectionBoundaryAgg.objects.filter(electionboundary_id=electedrepid, year=academic_year).first()
        if qs:
            electionboundarycounts["num_schools"] = qs.num_schools
            electionboundarycounts["num_students"] = qs.num_students
            electionboundarycounts["gender"] = {"girls": qs.num_girls, "boys": qs.num_boys}
        return electionboundarycounts


    def get_electionboundary_details(self, electedrep, academic_year):
        retdata = {"cat":{}, "mt": {}, "moi":{}}

        qs = ElectionBoundarySchoolCategoryAgg.objects.filter(electionboundary=electedrep, cat_ac_year=academic_year, institution_type='primary').values("cat").annotate(num_schools=Sum('num_schools'), num_students=Sum('num_students'), num_boys=Sum('num_boys'), num_girls=Sum('num_girls'))
        if qs == None:
            return retdata
        for data in qs:
            retdata["cat"][data["cat"]] = {"cat": data["cat"], "num_schools": data["num_schools"], "num_students": data["num_students"]}

        qs = ElectionBoundarySchoolMoiAgg.objects.filter(electionboundary=electedrep, moi_ac_year=academic_year).values("moi").annotate(num_schools=Sum('num_schools'), num_students=Sum('num_students'))
        if qs == None:
            return retdata
        for data in qs:
            retdata["moi"][data["moi"]] = {"moi": data["moi"], "num_schools": data["num_schools"], "num_students": data["num_students"]}

        qs = ElectionBoundaryStudentMotherTongueAgg.objects.filter(electionboundary=electedrep, mt_ac_year=academic_year).values("mt").annotate(num_schools=Sum('num_schools'), num_students=Sum('num_students'))
        if qs == None:
            return retdata
        for data in qs:
            retdata["mt"][data["mt"]] = {"mt": data["mt"], "num_schools": data["num_schools"], "num_students": data["num_students"]}

        return retdata


    def getSummaryData(self, electedrep, reportInfo):
        reportInfo["report_info"] = {}
        reportInfo["report_info"]["commision_code"] = \
            electedrep.elec_comm_code
        reportInfo["report_info"]["name"] = \
            electedrep.const_ward_name
        reportInfo["report_info"]["type"] = \
            electedrep.const_ward_type.name
        reportInfo["report_info"]["dise"] = electedrep.dise_slug
        if electedrep.current_elected_party:
            reportInfo["report_info"]["elected_party"] = \
                electedrep.current_elected_party.name
        reportInfo["report_info"]["elected_rep"] = \
            electedrep.current_elected_rep

    def getNeighbours(self, neighbours, elect_type, reportInfo):
        for neighbour in neighbours:
            neighbour_info = {}
            neighbour_info["commision_code"] = neighbour.elec_comm_code
            neighbour_info["name"] = neighbour.const_ward_name.lower()
            neighbour_info["type"] = neighbour.const_ward_type.name.lower()
            neighbour_info["elected_party"] = neighbour.current_elected_party.name.lower()
            neighbour_info["elected_rep"] = neighbour.current_elected_rep.lower()
            neighbour_info["dise"] = neighbour.dise_slug
            reportInfo["neighbour_info"].append(neighbour_info)

    #def getParentData(self, electedrep, reportInfo):
    #    reportInfo["parent_info"] = []
    #    if electedrep.parent:
    #        reportInfo["parent_info"].append({
    #            "const_ward_type": electedrep.parent.const_ward_type,
    #            "const_ward_name": electedrep.parent.const_ward_name,
    #            "id": electedrep.parent.id})
    #        if electedrep.parent.parent:
    #            reportInfo["parent_info"].append({
    #                "const_ward_type": electedrep.parent.parent.const_ward_type,
    ##                "const_ward_name": electedrep.parent.parent.const_ward_name,
    #                "id": electedrep.parent.parent.id})
    ##            if electedrep.parent.parent.parent:
    #                reportInfo["parent_info"].append({
    #                    "const_ward_type": electedrep.parent.parent.parent.const_ward_type,
    #                    "const_ward_name": electedrep.parent.parent.parent.const_ward_name,
    ##                    "id": electedrep.parent.parent.parent.id})
