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
                                "tabs": {"names": [{"substr": "ClassWise","title": "Class Wise",
                                    "subtabs": {"names": [{"substr":"Class4", "title": "Class 4"}, {"substr":"Class5", "title": "Class 5"}, {"substr":"Class6", "title": "Class 6"}]}}]
                               }},
                  "summarycounts": {"type": "Summary Counts",
                                    "path": "SummaryYearCounts",
                                    "tabs": {
                                        "names": [{"substr": "ClassWise", "title": "Class Wise", 
                                            "subtabs": {"names": [{"substr":"Class4","title": "Class 4"}, {"substr":"Class5","title": "Class 5"}, {"substr":"Class6","title": "Class 6"}]}},{"substr": "All", "title": "All Assessments"}],
                                        "commonsubtabs": {"names": [{"substr": "All", "title": "All Areas"},
                                                              {"substr": "Phase1", "title": "Phase 1"},
                                                              {"substr": "Phase2", "title": "Phase 2"}],
                                                    "subtabs": {"names": [{"substr":"NumAssessments","title": "Number of Assessments"},
                                                                          {"substr": "AverageScore", "title": "Average Score"}]
                                                               }
                                                    }
                                        }
                                   },
                  "actualgpvsassessed":{"type": "Num GP Vs Assessed GP",
                      "path": "NumGPsVsAssessedGPs",
                      "tabs": {"names": [{"title":"Num GPs Vs Assessed GPs","substr":"NumGPsVsAssessedGPs"}]}
                      },
                  "mappedschoolvsassessed":{"type": "Mapped Schools Vs Assessed Schools",
                      "path": "MappedSchoolsVsAssessedSchools",
                      "tabs": {"names": [{"title":"Mapped Schools Vs Assessed Schools", "substr":"MappedSchoolsVsAssessedSchools"}]}
                      },
                  "questionperformance": {"type": "Question Performance",
                      "path": "questionperformance",
                      "tabs": {"names": [{"title":"Class 4", "substr": "Class4QuestionPerf"}, {"substr": "Class5QuestionPerf", "title": "Class 5"}, {"substr": "Class6QuestionPerf", "title": "Class 6"}] }
                      },
                  "outliers": {"type": "Outliers",
                      "path": "OutlierBoxPlots",
                      "tabs": {"names": [{"title":"Class 4", "substr": "Class4Outliers"}, {"substr": "Class5Outliers", "title": "Class 5"}, {"substr": "Class6Outliers", "title": "Class 6"}] }
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
            else:
                boundaryid = ""
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
                'names': names,
                'tabs': self.graphtypes[graphtype]['tabs'],
                'charttype':self.graphtypes[graphtype]["type"],
                'year': year_id,
                'boundaryid': boundaryid,
                'boundary': {}
                }
            if boundaryid is not "":
                response['boundary'] = {"boundarytype": boundary.boundary_type_id,
                    "name": boundary.name,
                    "id": boundaryid}
        else:
            response = {'status':'No images found'}
        print("Returning response")
        return Response(response)
    
    def getImage(self, year, boundary, institution, graphtype):
        home = expanduser("~")
        graphpath = self.graphtypes[graphtype]["path"]
        if boundary is not None:
            boundarytype = boundary.boundary_type_id
            if boundarytype == 'SD':
                filepath = home+"/graphimages/"+graphpath+"/"+str(year)+"/SD/"+str(boundary.id)+"/"
            elif boundarytype == 'SB':
                filepath = home+"/graphimages/"+graphpath+"/"+str(year)+"/SD/"+str(boundary.parent_id)+"/SB/"+str(boundary.id)+"/"
            elif boundarytype == 'SC':
                filepath = home+"/graphimages/"+graphpath+"/"+str(year)+"/SD/"+str(boundary.parent_id.parent_id)+"/SB/"+str(boundary.parent_id)+"/SC/"+str(boundary.id)+"/"
        elif institution is not None:
            filepath = home+"/graphimages/"+graphpath+"/"+str(year)+"/SD/"+str(institution.admin1_id)+"/SB/"+str(institution.admin2_id)+"/SC/"+str(institution.admin3_id)+"/institutions/"+str(institution.id)+"/"
        else:
            filepath = home+"/graphimages/"+graphpath+"/"+str(year)+"/"
        images = {}
        print(filepath)
        print(os.path.exists(filepath))
        if os.path.exists(filepath):
            for filename in os.listdir(filepath):
                path = os.path.join(filepath, filename)
                if os.path.isdir(path):
                    continue
                images[filename] = path
            print(images)
            return images
        else:
            return None

    def getData(self, year, boundary, institution, graphtype):
        images = self.getImage(year, boundary, institution, graphtype)
        buffers = []
        names = {}
        count =0
        if images is None:
            return False, None, None
        else:
            for imgname in images:
                image = images[imgname]
                names[re.sub('\..*$', '', imgname)]= count
                with open(image, "rb") as img:
                    print("Reading the image")
                    f = img.read()
                    buf = bytearray(f)
                    buffers.append((base64.b64encode(buf).strip()).decode('utf8'))
                count += 1
        print(names)            

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
