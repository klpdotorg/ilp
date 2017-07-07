from os import system,sys
import os

#Before running this script
#change this to point to the ems database that is used for getting the data
fromdatabase="ems"

#change this to ilp db to be populated with
todatabase="ilp"

inputdatafile="getdata.sql"
loaddatafile="loaddata.sql"

tables=[
        {
            'name': 'schools_institution',
            'columns': 'id, dise_code, name, admin0_id,admin1_id,admin2_id, admin3_id, category_id, gender_id, institution_type_id, management_id, status_id',
            'query': "COPY(select s.id, s.dise_code, s.name, 2, admin1.id, admin2.id, admin3.id, s.cat_id, s.institution_gender, case admin3.boundary_type_id when 1 then 'primary' when 2 then 'pre' end, s.mgmt_id, 'AC'  from schools_institution s, schools_boundary admin3, schools_boundary admin2, schools_boundary admin1 where s.boundary_id=admin3.id and admin3.parent_id=admin2.id and admin2.parent_id=admin1.id and s.active=2) TO '$PWD/load/schools_institution.csv' NULL 'null' DELIMITER   ',' quote '\\\"' csv;",
         },
]

#Create directory and files
def init():
    if not os.path.exists("load"):
    	os.makedirs("load")
    inputfile=open(inputdatafile,'w',0)
    loadfile=open(loaddatafile,'w',0)
    command="psql -U klp -d "+fromdatabase+" -f cleanems.sql"
    system(command)



#Create the getdata.sql and loaddata.sql files
# getdata.sql file has the "Copy to" commands for populating the various csv files
# loaddata.sql file has the "copy from" commands for loading the data into the db
def create_sqlfiles():
  #Loop through the tables
  for table in tables:
      print >>sys.stderr,table
      #create the "copy to" file to get data from ems
      command='echo "'+table['query']+'\">>'+inputdatafile
      system(command)
      #create the "copy from" file to load data into db
      filename=os.getcwd()+'/load/'+table['name']+'.csv'
      open(filename,'w',0)
      os.chmod(filename,0666)
      system('echo "COPY '+table['name']+"("+table['columns']+") from '"+filename+"' with csv NULL 'null';"+'\">>'+loaddatafile)

#Running the "copy to" commands to populate the csvs.
def getdata():
  command="psql -U klp -d "+fromdatabase+" -f "+inputdatafile
  system(command)


#Running the "copy from" commands for loading the db.
def loaddata():
  command="psql -U klp -d "+todatabase+" -f "+loaddatafile+" 1>output 2>error"
  print>>sys.stderr, command
  system(command)


#order in which function should be called.
init()
create_sqlfiles()
getdata()
loaddata()

