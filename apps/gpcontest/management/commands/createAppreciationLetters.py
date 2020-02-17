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
    help = 'Creates GP Contest Appreciation Letters surveyid lettertype startyearmonth endyearmonth filename --lang --colour cols[comma separated cols giving cols for id, designation and name'
    now = date.today()
    surveyid = None
    lettertype = None
    basefiledir = os.getcwd()
    templatedir = "/apps/gpcontest/templates/"
    outputdir = basefiledir+"/generated_files/appreciationletters/"+str(now)+"/"
    letterprefix = "AppreciationLetter"
    numids = 0
    numpdfs = 0
    gpcombinedpdfs = 0
    dirset = False

    templates = {
                 "SB": {"template": "BlockAppreciationLetter.tex", "latex": None},
                 "SD": {"template": "DistrictAppreciationLetter.tex", "latex": None},
                 "GP": {"template": "GPAppreciationLetter.tex", "latex": None}}

    build_d = basefiledir+"/build/"
    colour = "colour"
    cols = []
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
        parser.add_argument('--cols')


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
        gpletters = {}
        with open(filename, "r", encoding='utf-8') as data_file:
            data = csv.reader(data_file)
            header = 1
            rowcounter = 0
            for row in data:
                if header:
                    header = 0
                    continue
                rowcounter += 1
                typeid = int(float(row[self.cols[0]].strip()))
                designation = row[self.cols[1]].strip()
                name = row[self.cols[2]].strip()
                if typeid in letterdata:
                    if designation in letterdata[typeid]:
                        letterdata[typeid][designation] += ";"+name
                    else:
                        letterdata[typeid][designation] = name
                else:
                    self.numids += 1
                    letterdata[typeid] = {designation: name}
        for boundaryid in letterdata:
            print(boundaryid, flush=True)
            template = self.templates[self.lettertype]["latex"]
            returneddata = boundary_details.get_details(self.surveyid, boundaryid, self.lettertype, self.startyearmonth, self.endyearmonth)
            print(returneddata, file=self.utf8stdout, flush=True)
            if returneddata is None:
                continue
            pdfscreated = []
            numpdf = 1
            blockid = 0
            for designation in letterdata[boundaryid]:
                names = letterdata[boundaryid][designation].split(";")
                for name in names:
                    outputfile, blockid = self.createPdfs(boundaryid, designation, name, self.lettertype, template, numpdf, returneddata)
                    if outputfile is None:
                        continue
                    numpdf += 1
                    pdfscreated.append(outputfile)
            if numpdf == 1:
                print("No pdfs to be created", flush=True)
                continue 
            filename = "GPAppreciationLetter_"+str(self.lettertype)+"_"+str(boundaryid)+".pdf"
            self.combinePdfs(pdfscreated, filename, self.outputdir)
            self.deleteTempFiles(pdfscreated)
            if self.lettertype == 'GP':
                if blockid in gpletters:
                    gpletters[blockid].append(self.outputdir+"/"+filename)
                else:
                    gpletters[blockid] = []
                    gpletters[blockid].append(self.outputdir+"/"+filename)
            self.numpdfs += 1
        print(self.outputdir)
        print(gpletters)
        if self.lettertype == 'GP':
            for blockid in gpletters:
                filename = "GPAppreciationLetter_"+str(self.lettertype)+"_ForBlock"+str(blockid)+".pdf"
                self.combinePdfs(gpletters[blockid],filename,self.outputdir)
                self.deleteTempFiles(gpletters[blockid])
                self.gpcombinedpdfs += 1 

    def getYearMonth(self, inputdate ):
        year = int(inputdate[0:4])
        month = self.translatedmonth[self.language][int(inputdate[5:7])]
        return year, month


    def createPdfs(self, typeid, designation, name, lettertype, template, numpdf, returneddata):

        year, month = self.getYearMonth(str(self.now))
        info = returneddata
        info["acadyear"] = self.academicyear
        info["designation"] = designation
        info["designation_name"] = name
        info["imagesdir"] = self.imagesdir
        renderer_template = template.render(info=info)

        output_file = "AppreciationLetter_"+str(typeid)+"_"+str(numpdf)

        districtid = returneddata["district"]["boundary_id"]
        if not self.dirset:
            self.outputdir = self.outputdir+"/"+str(districtid)
            if lettertype != 'SD':
                self.outputdir = self.outputdir+"/"+lettertype
 
            if not os.path.exists(self.outputdir):
                os.makedirs(self.outputdir)
            self.dirset = True

        with open(output_file+".tex", "w", encoding='utf-8') as f:
            f.write(renderer_template)

        os.system("xelatex -output-directory {} {}".format(
                      os.path.realpath(self.build_d),
                      os.path.realpath(output_file)))
        shutil.copy2(self.build_d+"/"+output_file+".pdf", self.outputdir)
        self.deleteTempFiles([output_file+".tex",
                             self.build_d+"/"+output_file+".pdf"])

        if self.lettertype == 'SD':
            return self.outputdir+"/"+output_file+".pdf", None
        return self.outputdir+"/"+output_file+".pdf", returneddata["block"]["boundary_id"]


    def handle(self, *args, **options):
        self.lettertype = options.get("lettertype")

        self.surveyid = options.get("surveyid", None)

        self.startyearmonth = options.get("startyearmonth", None)
        self.endyearmonth = options.get("endyearmonth", None)
        self.academicyear = self.getAcademicYear(self.startyearmonth,
                                                 self.endyearmonth)

        self.cols = [int(n) for n in options.get("cols",None).split(",")]

        csv_file= options.get('filename', None)
        if csv_file == None:
            print("Pass the csv file --filename", flush=True)
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
        print("Number of unique ids: "+str(self.numids), flush=True)
        print("Number of pdfs created: "+str(self.numpdfs), flush=True)
        if self.lettertype == 'GP':
            print("Number of GP combined pdfs created: "+str(self.gpcombinedpdfs), flush=True)

        if created:
            os.system('tar -cvf '+self.outputdir+'_'+str(self.now)+'.tar '+self.outputdir+'/')

        if os.path.exists(self.build_d):
            shutil.rmtree(self.build_d)
