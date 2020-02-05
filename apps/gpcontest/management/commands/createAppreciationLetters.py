import jinja2
import os
import shutil
import xlwt
import csv
from django.core.management.base import BaseCommand
from datetime import datetime, date
from PyPDF2 import PdfFileReader, PdfFileWriter
from assessments.models import Survey
from boundary.models import ElectionBoundary, Boundary
from schools.models import Institution
from gpcontest.reports import boundary_details
from . import baseReport 


class Command(BaseCommand, baseReport.CommonUtils):
    # used for printing utf8 chars to stdout
    utf8stdout = open(1, 'w', encoding='utf-8', closefd=False)
    help = 'Creates GP Contest Appreciation Letters surveyid lettertype startyearmonth endyearmonth filename --lang --colour'
    now = date.today()
    surveyid = None
    lettertype = None
    basefiledir = os.getcwd()
    templatedir = "/apps/gpcontest/templates/"
    outputdir = basefiledir+"/generated_files/appreciationletters/"+str(now)+"/"
    letterprefix = "AppreciationLetter"

    templates = {
                 "SB": {"template": "BlockAppreciationLetter.tex", "latex": None},
                 "SD": {"template": "DistrictAppreciationLetter.tex", "latex": None},
                 "GP": {"template": "GPAppreciationLetter.tex", "latex": None}}

    build_d = basefiledir+"/build/"
    colour = "colour"
    imagesdir = basefiledir+"/apps/gpcontest/images/"
    translatedmonth = {'kannada':{1:'ಜನವರಿ',2:'ಫೆಬ್ರವರಿ',3:'ಮಾರ್ಚ್',4:'ಎಪ್ರಿಲ್',5:'ಮೇ',6:'ಜೂನ್',7:'ಜುಲೈ',8:'ಆಗಸ್ಟ್',9:'ಸೆಪ್ಟಂಬರ್',10:'ಅಕ್ಟೋಬರ್',11:'ನವೆಂಬರ್',12:'ಡಿಸೆಂಬರ್'},
            'english':{1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',7:'July',8:'August',9:'September',
                10:'October',11:'November',12:'December'}}


    def add_arguments(self, parser):
        parser.add_argument('surveyid')
        parser.add_argument('lettertype')
        parser.add_argument('startyearmonth')
        parser.add_argument('endyearmonth')
        parser.add_argument('--colour', nargs='?', default='colour')
        parser.add_argument('--lang', nargs='?', default='kannada')
        parser.add_argument('--filename')


    def validateInputs(self):
        if not self.validateSurveyId(self.surveyid):
            return False
        if not self.checkYearMonth(self.startyearmonth):
            return False
        if not self.checkYearMonth(self.endyearmonth):
            return False
        return True

    def createLetters(self, filename):
        letterdata = {}
        with open(filename, "r", encoding='utf-8') as data_file:
            data = csv.reader(data_file)
            header = 1
            rowcounter = 0
            for row in data:
                if header:
                    header = 0
                    continue
                rowcounter += 1
                typeid = int(float(row[0].strip()))
                designation = row[1].strip()
                name = row[2].strip()
                if typeid in letterdata:
                    letterdata[typeid][designation] = name
                else:
                    letterdata[typeid] = {designation: name}
        for boundaryid in letterdata:
            print("BOUNDARY ID IS------"+str(boundaryid))
            outputdir = self.outputdir+"/"+self.lettertype
            template = self.templates[self.lettertype]["latex"]
            pdfscreated = []
            numpdf = 1
            for designation in letterdata[boundaryid]:
                 outputfile = self.createPdfs(boundaryid, designation, letterdata[boundaryid][designation], outputdir, template, numpdf)
                 numpdf += 1
                 pdfscreated.append(outputfile)
            filename = "GPAppreciationLetter_"+str(self.lettertype)+"_"+str(boundaryid)+".pdf"
            self.combinePdfs(pdfscreated, filename, outputdir)
            self.deleteTempFiles(pdfscreated)

    def getYearMonth(self, inputdate ):
        print(inputdate)
        year = int(inputdate[0:4])
        month = self.translatedmonth[self.language][int(inputdate[5:7])]
        return year, month


    def createPdfs(self, typeid, designation, name, outputdir, template, numpdf):

        returneddata = boundary_details.get_details(self.surveyid, typeid, self.lettertype, self.startyearmonth, self.endyearmonth)
        print(returneddata, file=self.utf8stdout)
        year, month = self.getYearMonth(str(self.now))
        info = returneddata
        info["acadyear"] = self.academicyear
        info["designation"] = designation
        info["designation_name"] = name
        info["imagesdir"] = self.imagesdir
        renderer_template = template.render(info=info)

        output_file = "AppreciationLetter_"+str(typeid)+"_"+str(numpdf)
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)

        print(output_file)
        with open(output_file+".tex", "w", encoding='utf-8') as f:
            f.write(renderer_template)

        os.system("xelatex -output-directory {} {}".format(
                      os.path.realpath(self.build_d),
                      os.path.realpath(output_file)))
        shutil.copy2(self.build_d+"/"+output_file+".pdf", outputdir)
        self.deleteTempFiles([output_file+".tex",
                             self.build_d+"/"+output_file+".pdf"])

        return outputdir+"/"+output_file+".pdf"


    def handle(self, *args, **options):
        self.lettertype = options.get("lettertype")

        self.surveyid = options.get("surveyid", None)

        self.startyearmonth = options.get("startyearmonth", None)
        self.endyearmonth = options.get("endyearmonth", None)
        self.academicyear = self.getAcademicYear(self.startyearmonth,
                                                 self.endyearmonth)

        csv_file= options.get('filename', None)
        if csv_file == None:
            print("Pass the csv file --filename")
            return

        self.language = options.get("lang")

        self.templatedir = self.templatedir+"/"+self.language+"/"
        self.imagesdir = self.imagesdir+"/"+self.language+"/"

        colour = options.get("colour")
        self.imagesdir = self.imagesdir+"/"+colour+"/"

        self.initiatelatex()

        if not os.path.exists(self.outputdir):
            os.makedirs(self.outputdir)

        created = self.createLetters(csv_file)

        if created:
            os.system('tar -cvf '+self.outputdir+'_'+str(self.now)+'.tar '+self.outputdir+'/')

        if os.path.exists(self.build_d):
            shutil.rmtree(self.build_d)
