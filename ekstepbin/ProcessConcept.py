import os
import json
import sys
import re

dir = os.path.dirname(__file__)
input_file = os.path.join(dir, '../datapull/concept_details.json')
concept_file = open('../datapull/concept_details.txt', 'w')

with open(input_file, 'r', encoding='utf8')as json_file:
    jdata = json.load(json_file)
    data = jdata["result"]["concepts"]
    datalen = len(data)
    print(datalen)
    for i in range (0,datalen):
        concept_file.write(data[i]["subject"])
        concept_file.write("|")
        concept_file.write( data[i]["identifier"])
        concept_file.write("|")
        concept_file.write(str(data[i]["name"]))
        concept_file.write("|")
        concept_file.write(str(data[i]["description"]))
        concept_file.write("\n")

concept_file.close()
