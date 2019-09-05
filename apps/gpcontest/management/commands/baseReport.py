import jinja2
import os
import shutil
from django.core.management.base import BaseCommand
from datetime import datetime, date
from PyPDF2 import PdfFileReader, PdfFileWriter
from assessments.models import Survey
from boundary.models import ElectionBoundary, Boundary


class BaseReport():
 
    def initiatelatex(self):
        # create the build directory if not existing
        if not os.path.exists(self.build_d):
            os.makedirs(self.build_d)
        latex_jinja_env = jinja2.Environment(
            variable_start_string='{{',
            variable_end_string='}}',
            comment_start_string='\#{',
            comment_end_string='}',
            line_comment_prefix='%%',
            trim_blocks=True,
            autoescape=False,
            loader=jinja2.FileSystemLoader(os.path.abspath('/'))
        )
        for filetype in self.templates:
            self.templates[filetype]["latex"] = latex_jinja_env.get_template(
                self.basefiledir+self.templatedir+self.templates[filetype]["template"])

       
    def validateGPIds(self, gpids):
        gp = []
        for gpid in gpids:
            try:
                gp[gpid] = ElectionBoundary.objects.get(
                            id=gpid, const_ward_type='GP')
            except ElectionBoundary.DoesNotExist:
                print("Invalid gpid: "+str(gpid)+" passed")
                return False
        return gp

    def validateBoundaryIds(self, boundaryids, boundaryType):
        for bid in boundaryids:
           try:
               Boundary.objects.get(
                            id=bid, boundary_type_id=boundaryType)
           except Boundary.DoesNotExist:
               print("Invalid districtid: "+str(bid)+" passed")
               return False
        return True

    def validateSurveyId(self, surveyid):
        try:
             Survey.objects.get(id=surveyid)
        except Survey.DoesNotExist:
            print("Invalid surveyid: "+str(surveyid)+" passed")
            return False
        return True

    def checkYearMonth(self, yearmonth):
        try:
            datetime.strptime(yearmonth, '%Y%m')
        except ValueError:
            print("Year month format is invalid it should be YYYYMM, " +yearmonth)
            return False
        return True

    def deleteTempFiles(self, tempFiles):
        for f in tempFiles:
            os.remove(f)

    def mergeReports(self, outputdir, gpfile, schoolfiles, outputfile):
        inputfiles = [outputdir+gpfile]
        for schoolfile in schoolfiles:
            inputfiles.append(outputdir+schoolfile)
        self.combinePdfs(inputfiles, outputfile, outputdir) 
        self.deleteTempFiles(inputfiles)

    def combinePdfs(self, inputfiles, outputfile, outputdir):
        input_streams = []
        try:
            # First open all the files, then produce the output file, and
            # finally close the input files. This is necessary because
            # the data isn't read from the input files until the write
            # operation.
            output_stream = open(outputdir+"/"+outputfile, 'wb')
            for input_file in inputfiles:
                input_streams.append(open(input_file, 'rb'))
                writer = PdfFileWriter()
                for reader in map(PdfFileReader, input_streams):
                    for n in range(reader.getNumPages()):
                        writer.addPage(reader.getPage(n))
                writer.write(output_stream)
        finally:
            for f in input_streams:
                f.close()

    def getAcademicYear(self, startyearmonth, endyearmonth):
        startyear = int(startyearmonth[0:4])
        startmonth = int(startyearmonth[4:6])
        if startmonth <= 5:
            acadyear = str(startyear-1)+"-"+str(startyear)
        else:
            acadyear = str(startyear)+"-"+str(startyear+1)
        return acadyear


