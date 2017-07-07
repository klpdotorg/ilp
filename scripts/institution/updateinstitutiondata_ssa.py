from os import system,sys
import os

#Before running this script
#change this to point to the ems database that is used for getting the data
fromdatabase="dubdubdub"

#change this to ilp db to be populated with
todatabase="ilp"

inputdatafile="getdata.sql"
tempdatafile="tempdata.sql"
loaddatafile="loaddata.sql"

tables=[
        {
            'name': 'update_ssadata',
            'tablename': 'schools_institution',
            'temptablename': 'temp_info',
            'createcolumns': 'year_established text,rural_urban text,village text,phone_number text, dise_code text',
            'columns': 'year_established,rural_urban,village,phone_number,dise_code',
            'query': "COPY(select estdyear,rururb,vilname,mobile1,dise_code from ssa_school, tb_school where ssa_school.schcd=tb_school.dise_code ) TO '$PWD/load/update_ssadata.csv' NULL 'null' DELIMITER   ',' quote '\\\"' csv;",
        }
]

#Create directory and files
def init():
    if not os.path.exists("load"):
    	os.makedirs("load")
    inputfile=open(inputdatafile,'wb',0)
    loadfile=open(loaddatafile,'wb',0)
    tempfile=open(tempdatafile,'wb',0)


#Create the getdata.sql and loaddata.sql files
# getdata.sql file has the "Copy to" commands for populating the various csv files
# loaddata.sql file has the "copy from" commands for loading the data into the db
def create_sqlfiles():
    #Loop through the tables
    for table in tables:
        #create the "copy to" file to get data from ems
        command='echo "'+table['query']+'\">>'+inputdatafile
        system(command)

        #create temp table
        filename=os.getcwd()+'/load/'+table['name']+'.csv'
        command = 'echo "CREATE TEMP TABLE '+table['temptablename']+'('+table['createcolumns']+');"'+'>>'+tempdatafile
        print(command, file=sys.stderr)
        system(command)

        #create sql file to copy into the temp table and then update
        system('echo "COPY '+table['temptablename']+"("+table['columns']+") from '"+filename+"' with csv NULL 'null';"+'\">>'+tempdatafile)
        command='echo "UPDATE '+table['tablename']+' set '
        columns = table['columns'].split(',')
        for num in range(0, len(columns)-2):
            command = command+columns[num]+'='+table['temptablename']+'.'+columns[num]+', '
        command = command+columns[num+1]+'='+table['temptablename']+'.'+columns[num+1]
        command = command + ' from '+table['temptablename']+' where '+table['tablename']+'.dise_code = '+table['temptablename']+'.dise_code;">>'+tempdatafile
        print(command, file=sys.stderr)
        system(command)


#Running the "copy to" commands to populate the csvs.
def getdata():
    command="psql -U klp -d "+fromdatabase+" -f "+inputdatafile
    system(command)


#Running the "copy from" commands for loading the db.
def loaddata():
    command="psql -U klp -d "+todatabase+" -f "+tempdatafile+" 1>output 2>error"
    print(command, file=sys.stderr)
    system(command)


#order in which function should be called.
init()
create_sqlfiles()
getdata()
loaddata()
