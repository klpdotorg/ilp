import os
import json
import sys
import re

content_id = sys.argv[1]
print(content_id)

dir = os.path.dirname(__file__)
input_file = os.path.join(dir, '../datapull/'+content_id)#this txt file has list of gdata id 
json_file = open('../datapull/ContentParameters.json', 'w')

json_file.write("{\"request\": {\"filters\": {\"objectType\": [\"Content\"],\"identifier\": [")
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
