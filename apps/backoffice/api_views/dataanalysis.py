from django.http import HttpResponse
import json
from rest_framework.response import Response
from django.shortcuts import redirect
from backoffice.dataanalysis.forms import ExportForm
from django.views import View
from django.shortcuts import render
from django.urls import reverse
from boundary.models import BoundaryStateCode, Boundary
from common.models import AcademicYear
import pandas as pd
import matplotlib.pyplot as plt, mpld3
import matplotlib.image as mpimg
from mpld3 import plugins
import seaborn as sns
import numpy as np
import io
import os
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg
from os.path import expanduser

class DataAnalysisSearch(View):
    template_name = 'dataanalysis/analysis_search.html'
    post_template_name = 'dataanalysis/analysis.html'
 
    def get(self, request):
        print("IN GET")
        states = BoundaryStateCode.objects.all()
        academic_year = ['2016-2017','2017-2018','2018-2019','2019-2020']
        return render(request, self.template_name,
                      {'states': states, 'academic_year': academic_year})



class CorelationAnalysis(View):
    template_name = 'dataanalysis/analysis.html'
    basepath = "~/csvs/dataanalysis/"
    alldata = "allanswers"
    dfs = {}
    questiongroups = ["Class4Assessment","Class5Assessment", "Class6Assessment"]
 
    def get(self, request):
        plt.close("all")
        print("IN GET OF ANALYSIS")
        print("Request is:")
        boundary = None
        institution = None
        try:
            year =request.GET.get('year')
            print(year)
            year_id = AcademicYear.objects.get(year=year).char_id
            boundaryid = request.GET.get('boundary_id')
            if boundaryid is not None:
                print(boundaryid)
                boundary = Boundary.objects.get(id=boundaryid)
                print(boundary)
            institutionid = request.GET.get('institution_id')
            if institutionid is not None:
                institutuion = Institution.objects.get(id=institution)
        except Exception as e:
            print(e)
            return render(request, self.template_name,
                    {'status' : 'ERROR'+str(e)})

        #jsondata = self.doAnalysis(startyear_id, endyear_id, boundary, institution)
        jsondata = ''
        status, buffers = self.doCorelation(year_id, boundary, institution)
        #image = base64.b64encode(fig.getvalue()).strip()#.encode("base64").strip()
        #image_base64 =base64.b64encode(fig.getvalue()).decode('utf-8').replace('\n','')
        #imgStr = "data:image/png;base64,"
        #imgStr += base64.b64encode(fig.getvalue())
        #fig.close()
        if status:
            return render(request, self.template_name, 
                    {'status':'','data':buffers, 'charttype':'Corelation HeatMap'})
        else:
            return render(request, self.template_name, 
                    {'status':'No images found', 'charttype':'Corelation HeatMap'})

    def getImage(self, year, boundary, institution, graphtype):
        home = expanduser("~")
        boundarytype = boundary.boundary_type_id
        if boundary is not None:
            if boundarytype == 'SD':
                filepath = home+"/graphimages/"+str(year)+"/SD/"+str(boundary.id)+"/"+graphtype+"/"
            elif boundarytype == 'SB':
                filepath = home+"/graphimages/"+str(year)+"/SD/"+str(boundary.parent_id)+"/SB/"+str(boundary.id)+"/"+graphtype+"/"
            elif boundarytype == 'SC':
                filepath = home+"/graphimages/"+str(year)+"/SD/"+str(boundary.parent_id.parent_id)+"/SB/"+str(boundary.parent_id)+"/SC/"+str(boundary.id)+"/"+graphtype+"/"
        elif institution is not None:
            filepath = home+"/graphimages/"+str(year)+"/SD/"+str(institution.admin1_id)+"/SB/"+str(institution.admin2_id)+"/SC/"+str(institution.admin3_id)+"/institutions/"+str(institution.id)+"/"+graphtype+"/"
        else:
            filepath = home+"/graphimages/"+str(year)+"/"+graphtype
        images = []
        print(filepath)
        print(os.path.exists(filepath))
        if os.path.exists(filepath):
            print("File path exists")
            for filename in os.listdir(filepath):
                print("reading file: "+filename)
                images.append(os.path.join(filepath, filename))
            return images
        else:
            return None

    def doCorelation(self, year, boundary, institution):
        images = self.getImage(year, boundary, institution, "corelation")
        buffers = []
        if images is None:
            return False, "No images present"
        else:
            for image in images:
                with open(image, "rb") as img:
                    f = img.read()
                    buf = bytearray(f)
                    buffers.append((base64.b64encode(buf).strip()).decode('utf8'))

        return True, buffers 

 


class CompetencyAnalysis(View):
    def doAnalysis(self, startyear, endyear, boundary, institution):
        for year in self.years:
            self.dfs[year] = {} 
            for grade in self.grades:
                filename = self.basepath +"/Class"+str(grade)+"_"+str(year)+".csv"
                #filename = self.basepath +year+"/"+"GPContest_Class"+str(grade)+".csv"
                self.dfs[year][grade] = pd.read_csv(filename)

        perdistricts = {}
        for year in self.dfs:
            perdistricts[year] = {}
            for grade in self.dfs[year]:
                perdistricts[year][grade] = self.dfs[year][grade].groupby(['district']).agg(totalscore=('answer',sum), numstudents=('answergroupid','nunique'))
                perdistricts[year][grade]['percentage_'+grade+"_"+year] =  perdistricts[year][grade]['totalscore']*100/(20*perdistricts[year][grade]['numstudents'])
                perdistricts[year][grade].rename(columns={'totalscore':'totalscore_'+year,'numstudents':'numstudents_'+grade+'_'+year},inplace=True)


        perdistrict = {}
        encodedimages = []
        jsonimages = []
        for grade in self.grades:
            toplotbase = 'percentage_'
            toplot = []
            dataconcat = []
            toplotbase = toplotbase+grade+"_"
            for year in self.years:
                toplot.append(toplotbase+year)
                dataconcat.append(perdistricts[year][grade])
            perdistrict[grade] = pd.concat(dataconcat,axis=1,sort=True)
            print("1")
            print(perdistrict[grade])
            print("2")
            print(toplot)
            ax = perdistrict[grade].plot(y=toplot,kind='bar')
            fig = ax.get_figure()
            print("3")
            print(ax.get_xticks())
            print("4")
            for label in ax.get_xticklabels():
                print(label)
            #interactive_legend = plugins.InteractiveLegendPlugin(zip(handles, ax.collections), labels, alpha_unsel=0.5, alpha_over=1.5, start_visible=True)
            #plugins.connect(fig, interactive_legend)
            fig_html = mpld3.fig_to_html(fig)
            figjson = json.dumps(mpld3.fig_to_dict(fig), cls=NpEncoder)
            #img = io.BytesIO()
            #fig.savefig(img, format='png')
            #img.seek(0)
            #encodedimages.append(base64.b64encode(img.getvalue()).decode('utf-8'))
            jsonimages.append(figjson)
        return jsonimages 

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)
        #return encodedimages
