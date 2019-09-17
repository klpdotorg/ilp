import csv
from django.utils import timezone
from datetime import datetime
from django.core.management.base import BaseCommand
from schools.models import Institution, InstitutionCategory, Management, InstitutionLanguage
from boundary.models import Boundary, ElectionBoundary
from common.models import Status, AcademicYear, InstitutionType, Language, InstitutionGender
from dise.models import BasicData


class Command(BaseCommand):

    fileoptions = {"institutions"}
    csv_files = {}

    def add_arguments(self, parser):
        parser.add_argument('institutions')

    def get_csv_files(self, options):
        for fileoption in self.fileoptions:
            file_name = options.get(fileoption, None)
            if not file_name:
                print("Please specify a filename with the --"+fileoption+" argument")
                return False
            f = open(file_name, encoding='utf-8')
            self.csv_files[fileoption] = csv.reader(f)
        return True

    def check_value(self, value, default=None):
        if value.strip() == '':
            if default:
                return default
            return None
        return value

    def create_institutions(self):
        count = 0
        institutions = []
        for row in self.csv_files["institutions"]:
            if count == 0:
                count += 1
                continue
            count += 1
            state = self.getBoundary(row[0].strip().lower(), 'ST')
            if state == None:
                continue
            district = self.getBoundary(row[1].strip().lower(), 'SD')
            if district == None:
                continue
            block = self.getBoundary(row[2].strip().lower(), 'SB')
            if block == None:
                continue
            cluster = self.getBoundary(row[3].strip().lower(), 'SC')
            if cluster == None:
                continue
            gp = self.getGP(row[4].strip().lower(),row[5])
            if gp == None:
                continue
            name = row[6]
            dise = self.getDise(row[7])
            try:
                category = InstitutionCategory.objects.get(name__iexact=row[8].lower())
                gender = InstitutionGender.objects.get(char_id__iexact =row[9].lower())
                institutiontype = InstitutionType.objects.get(char_id='primary')
                management = Management.objects.get(id=1)
                language = Language.objects.get(char_id__iexact=row[10].lower())
                status = Status.objects.get(char_id='AC')
            except Exception as e:
                print(e)
                continue
            try:

                institution = Institution.objects.create(
                    name=name,
                    admin0=state,
                    admin1=district,
                    admin2=block,
                    admin3=cluster,
                    gp=gp,
                    dise=dise,
                    category=category,
                    gender=gender,
                    management=management,
                    institution_type=institutiontype,
                    status=status
                    )
                self.createInstitutionLanguage(institution,language)
                institutions.append(institution)
            except Exception as e:
                print(e)
        return institutions 

    def createInstitutionLanguage(self, institution, language):
        try:
            obj, created = InstitutionLanguage.objects.get_or_create(institution=institution,
                    moi=language)
            print("Created institution, language mapping")
        except Exception as e:
            print(e)
        

    def getBoundary(self, name, btype):
        try:
            boundary = Boundary.objects.get(name__iexact=name,boundary_type=btype)
        except Boundary.DoesNotExist:
            print("No boundary with name: "+name+" and type: "+btype+" found")
            return None
        return boundary

    def getGP(self, gpid, gpname):
        try:
            gp = ElectionBoundary.objects.get(id=gpid, const_ward_name__iexact = gpname, const_ward_type='GP')
        except ElectionBoundary.DoesNotExist:
            print("No GP found with id :"+str(gpid)+" and name: "+gpname)
            return None
        return gp

    def getDise(self, disecode):
        try:
            dise = BasicData.objects.get(school_code=disecode,academic_year_id='1617')
        except BasicData.DoesNotExist:
            print("No DISE data found for code :"+str(disecode)+" and academic year 1617")
            try:
                dise = BasicData.objects.get(school_code=disecode,academic_year_id='1516')
                print("Dise data available for 1516")
                newdise = self.createDiseEntry(dise, disecode, '1617')
                return newdise
            except BasicData.DoesNotExist:
                print("No DISE data found for code :"+str(disecode)+" and academic year 1516")
                return None

            return None
        return dise

    def createDiseEntry(self, dise, disecode, academicyear):
        newdise = dise
        newdise.id = None 
        newdise.pk=None
        newdise.academic_year_id=academicyear
        newdise.save()
        try:
            createddise = BasicData.objects.get(school_code=disecode,academic_year_id=academicyear)
        except BasicData.DoesNotExist:
            print("Could not create dise entry for schoolcode :"+str(disecode)+" and academicyear :"+str(academicyear))
            return None
        return createddise

    def handle(self, *args, **options):
        if not self.get_csv_files(options):
            return

        # create schools
        institutions = self.create_institutions()
        print(institutions)
        print(str(len(institutions))+" number of institutions created")
