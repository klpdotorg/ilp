from django.http import HttpResponse
import re
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
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

class DataAnalysisSearch(View):
    template_name = 'dataanalysis/analysis.html'
 
    def get(self, request):
        print("IN GET")
        states = BoundaryStateCode.objects.all()
        academic_year = ['2016-2017','2017-2018','2018-2019','2019-2020']
        return render(request, self.template_name,
                      {'states': states, 'academic_year': academic_year})



class DataAnalysis(ListAPIView):
    basepath = "~/csvs/dataanalysis/"
    alldata = "allanswers"
    dfs = {}
    graphtypes = {"corelation":{"type": "Corelation Heat Map",
                                "path": "corelation",
                                "tabs": {"ClassWise":["Class4","Class5", "Class6"]},
                                "order": {"Class4":0,"Class5":1,"Class6":2}
                               },
                  "summarycounts": {"type": "Summary Counts",
                                    "path": "summarycounts",
                                    "tabs": {"AllDistricts":["NumAssessments","AverageScore"], "Phase1": ["NumAssessments","AverageScore"], "Phase2":["NumAssessments","AverageScore"]},
                                    "order": {"AllDistrictsNumAssessments": 0,"AllDistrictsAverageScore": 1,"Phase1NumAssessments": 2,"Phase1AverageScore": 3,"Phase2NumAssessments": 4,"Phase2AverageScore": 5}
                                   }
                  }
          
 
    def list(self, request, *args, **kwargs):
        plt.close("all")
        print("IN LIST OF ANALYSIS")
        boundary = None
        institution = None
        try:
            year =request.GET.get('year')
            if year is not None:
                print(year)
                year_id = AcademicYear.objects.get(year=year).char_id
            else:
                year_id = ""
            boundaryid = request.GET.get('boundary_id')
            if boundaryid is not None:
                print(boundaryid)
                boundary = Boundary.objects.get(id=boundaryid)
                print(boundary)
            institutionid = request.GET.get('institution_id')
            if institutionid is not None:
                institutuion = Institution.objects.get(id=institution)
            graphtype = request.GET.get('graph_type')
            print(graphtype)
            if graphtype not in self.graphtypes:
                raise Exception("Invalid graph type")
        except Exception as e:
            print(e)
            response = {'status': 'ERROR: '+str(e)}
            return Response(response)

        jsondata = ''
        status, buffers, names = self.getData(year_id, boundary, institution, graphtype)
        if status:
            response = {
                'status':'',
                'data': buffers,
                'order': self.graphtypes[graphtype]['order'],
                'names': names,
                'tabs': self.graphtypes[graphtype]['tabs'],
                'charttype':self.graphtypes[graphtype]["type"]}
        else:
            response = {'status':'No images found'}
        print("Returning response")
        return Response(response)
    
    def getImage(self, year, boundary, institution, graphtype):
        home = expanduser("~")
        if boundary is not None:
            boundarytype = boundary.boundary_type_id
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
        images = {}
        print(filepath)
        print(os.path.exists(filepath))
        order = self.graphtypes[graphtype]["order"]
        names = []
        for name in order:
            names.append(name)
        if os.path.exists(filepath):
            for filename in os.listdir(filepath):
                for name in order:
                    if name in filename:
                        index = order[name]
                        images[index] = os.path.join(filepath,filename)
                        continue
            imgarray = []
            print(images)
            for index in range(0,len(images)):
                imgarray.append(images[index])
            print(imgarray)
            print(names)
            return imgarray, names
        else:
            return None, None

    def getData(self, year, boundary, institution, graphtype):
        images, names = self.getImage(year, boundary, institution, graphtype)
        buffers = []
        if images is None:
            return False, None, None
        else:
            for image in images:
                with open(image, "rb") as img:
                    print("Reading the image")
                    f = img.read()
                    buf = bytearray(f)
                    buffers.append((base64.b64encode(buf).strip()).decode('utf8'))

        return True, buffers, names 



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
