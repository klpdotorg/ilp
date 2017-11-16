from os import system,sys
import os, inspect

if len(sys.argv) != 3:
    print("Please give database names as arguments. USAGE: python updatespatialdata.py spatial ilp")
    sys.exit()


#Before running this script
#change this to point to the ems database that is used for getting the data
fromdatabase = sys.argv[1]

#change this to ilp db to be populated with
todatabase = sys.argv[2]

basename = "spatialupdate"
scriptdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

inputdatafile = scriptdir+"/"+basename+"_getdata.sql"
tempdatafile = scriptdir+"/"+basename+"_tempdata.sql"

tables = [
    {
        'name': 'update_mlaspatial',
        'tablename': 'boundary_electionboundary',
        'temptablename': 'temp_mlainfo',
        'createcolumns': 'ac_no integer, state_ut text, the_geom geometry',
        'columns': 'ac_no, state_ut, the_geom',
        'query': "\COPY (select replacecolumns from assembly) TO '"+scriptdir+"/load/replacefile.csv' NULL 'null' DELIMITER   ',' quote '\\\"' csv;",
        'update_query': "UPDATE replacetablename set geom=temp.the_geom from replacetemptable temp where elec_comm_code = temp.ac_no and const_ward_type_id='MLA' and status_id='AC' ;"
    },
    {
        'name': 'update_mpspatial',
        'tablename': 'boundary_electionboundary',
        'temptablename': 'temp_mpinfo',
        'createcolumns': 'pc_no integer, state_ut text, the_geom geometry',
        'columns': 'pc_no, state_ut, the_geom',
        'query': "\COPY (select replacecolumns from parliament) TO '"+scriptdir+"/load/replacefile.csv' NULL 'null' DELIMITER   ',' quote '\\\"' csv;",
        'update_query': "UPDATE replacetablename set geom=temp.the_geom from replacetemptable temp where elec_comm_code = temp.pc_no and const_ward_type_id='MP' and status_id='AC' ;"
    }

]

#Create directory and files
def init():
    if not os.path.exists(scriptdir+"/load"):
    	os.makedirs(scriptdir+"/load")
    inputfile=open(inputdatafile,'wb',0)
    tempfile=open(tempdatafile,'wb',0)


#Create the getdata.sql and loaddata.sql files
# getdata.sql file has the "Copy to" commands for populating the various csv files
# loaddata.sql file has the "copy from" commands for loading the data into the db
def create_sqlfiles():
    #Loop through the tables
    for table in tables:
        #create the "copy to" file to get data from ems
        system('echo "'+table['query'].replace('replacecolumns',table['columns']).replace('replacefile',table['name'])+'\">>'+inputdatafile)

        #create temp table
        filename = scriptdir+'/load/'+table['name']+'.csv'
        system('echo "CREATE TEMP TABLE '+table['temptablename']+'('+table['createcolumns']+');"'+'>>'+tempdatafile)

        #create sql file to copy into the temp table and then update
        system('echo "\COPY '+table['temptablename']+"("+table['columns']+") from '"+filename+"' with csv NULL 'null';"+'\">>'+tempdatafile)
        system('echo "'+table['update_query'].replace('replacetablename',table['tablename']).replace('replacetemptable',table['temptablename'])+'">>'+tempdatafile)


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
