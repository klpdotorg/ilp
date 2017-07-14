from os import system,sys
import os

#Before running this script
#change this to point to the ems database that is used for getting the data
fromdatabase = "dubdubdub"

#change this to ilp db to be populated with
todatabase = "ilp"

basename = "update"

inputdatafile = basename+"_getdata.sql"
tempdatafile = basename+"_tempdata.sql"

tables=[
        {
            'name': 'update_ssadata',
            'tablename': 'schools_institution',
            'temptablename': 'temp_info',
            'createcolumns': 'year_established text,rural_urban text,village text,phone_number text, dise_code text',
            'columns': 'year_established,rural_urban,village,phone_number,dise_code',
            'query': "COPY(select estdyear,rururb,vilname,mobile1,dise_code from ssa_school, tb_school where ssa_school.schcd=tb_school.dise_code ) TO '$PWD/load/update_ssadata.csv' NULL 'null' DELIMITER   ',' quote '\\\"' csv;",
            'update_query': "UPDATE schools_institution set year_established=temp_info.year_established, rural_urban=temp_info.rural_urban, village=temp_info.village, phone_number=temp_info.phone_number from temp_info where schools_institution.dise_code = temp_info.dise_code;"
        }
        #{
            #'name': 'update_electedrep',
            #'tablename': 'schools_institution',
            #'temptablename': 'temp_elect',
        #}
]

#Create directory and files
def init():
    if not os.path.exists("load"):
    	os.makedirs("load")
    inputfile=open(inputdatafile,'wb',0)
    tempfile=open(tempdatafile,'wb',0)


#Create the getdata.sql and loaddata.sql files
# getdata.sql file has the "Copy to" commands for populating the various csv files
# loaddata.sql file has the "copy from" commands for loading the data into the db
def create_sqlfiles():
    #Loop through the tables
    for table in tables:
        #create the "copy to" file to get data from ems
        system('echo "'+table['query']+'\">>'+inputdatafile)

        #create temp table
        filename=os.getcwd()+'/load/'+table['name']+'.csv'
        system('echo "CREATE TEMP TABLE '+table['temptablename']+'('+table['createcolumns']+');"'+'>>'+tempdatafile)

        #create sql file to copy into the temp table and then update
        system('echo "COPY '+table['temptablename']+"("+table['columns']+") from '"+filename+"' with csv NULL 'null';"+'\">>'+tempdatafile)
        system('echo "'+table['update_query']+'">>'+tempdatafile)


#Running the "copy to" commands to populate the csvs.
def getdata():
    system("psql -U klp -d "+fromdatabase+" -f "+inputdatafile)


#Running the "copy from" commands for loading the db.
def loaddata():
    system("psql -U klp -d "+todatabase+" -f "+tempdatafile)


#order in which function should be called.
init()
create_sqlfiles()
getdata()
loaddata()
