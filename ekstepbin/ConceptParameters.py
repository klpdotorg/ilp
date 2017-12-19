import os
import json
import sys
import re

concepts = sys.argv[1]
dir = os.path.dirname(__file__)
input_file = os.path.join(dir, '../datapull/'+concepts)#this txt file has list of concepts from ME_SESSION_SUMMARY.json
json_file = open('../datapull/ConceptParameters.json', 'w')

json_file.write("{\"request\": {\"filters\": {\"objectType\": [\"Concept\"],\"identifier\": [")
first_line = 1
for line in open(input_file, 'r'):
    if first_line:
        json_file.write('"' + line.strip().rstrip("\r\n") + '"')
        first_line = 0
    else:
       json_file.write(',"' + line.strip().rstrip("\r\n") + '"')
json_file.write("]")
json_file.write("\n")
json_file.write("},\"limit\": 500}}")

json_file.close()
