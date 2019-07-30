from schools.utils import schoolGPmapping

def run():
    print("Getting school GP mapping info for select districts")
    schoolinfo = schoolGPmapping.getSchoolInfo([420,421], 2)
    print(schoolinfo)