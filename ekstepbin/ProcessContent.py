import os
import json
import sys
import re

dir = os.path.dirname(__file__)
input_file = os.path.join(dir, '../datapull/content_details.json')
content_file = open('../datapull/content_details.txt', 'w') 
content_concept_file = open('../datapull/content_concept.txt', 'w')#this file has contents linked with concepts

with open(input_file, 'r', encoding='utf8')as json_file:
    jdata = json.load(json_file)
    data = jdata["result"]["content"]
    datalen = len(data)
    for i in range (0,datalen):
        if 'subject' in data[i]:
            content_file.write(data[i]["subject"])
        else:
           content_file .write("none")
        content_file.write("|")
        content_file.write(str( data[i]["language"]))
        content_file.write("|")
        content_file.write( str(data[i]["gradeLevel"]))
        content_file.write("|")
        content_file.write( data[i]["contentType"])
        content_file.write("|")
        content_file.write( data[i]["identifier"])
        content_file.write("|")
        content_file.write(str( data[i]["ageGroup"]))
        content_file.write("|")
        content_file.write((data[i]["name"]).rstrip("\r\n"))
        content_file.write("|")
        content_file.write( data[i]["description"].replace('\n','').replace('\r',''))
        content_file.write("|")
        if 'medium' in data[i]:
            content_file.write(str(data[i]["medium"]))
        else:
            content_file .write("none")
        content_file.write("|")
        if 'concepts' in data[i]:
            content_file.write(str(data[i]["concepts"]))
            conceptlen = len(data[i]["concepts"])
            for k in range(0,conceptlen):
                content_concept_file.write(data[i]["identifier"])
                content_concept_file.write("|")
                content_concept_file.write(data[i]["concepts"][k])
                content_concept_file.write("\n")
        else:
            content_file .write("none")
        content_file.write("\n")
        
content_file.close()
content_concept_file.close()
