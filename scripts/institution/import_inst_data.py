from os import system,sys
import os

#Before running this script
#change this to point to the ems database that is used for getting the data
emsdatabase="ems"

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
        {
            'name': 'schools_institutionlanguage',
            'columns': 'id, institution_id, moi_id',
            'query': "COPY(select lang.id,lang.institution_id,case lang.moi_type_id when 1 then 'kan' when 2 then 'urd' when 3 then 'tam' when 4 then 'tel' when 5 then 'eng' when 6 then 'mar' when 7 then 'hin' when 8 then 'kon' when 9 then 'sin' when 10 then 'oth' when 11 then 'guj' when 12 then 'unknown' when 13 then 'multi' when 14 then 'nep' when 15 then 'ori' when 16 then 'ben' when 17 then 'mal' when 18 then 'san' when 19 then 'lam' end  from schools_institution_languages lang, schools_institution s where lang.institution_id=s.id  and s.active=2) TO '$PWD/load/schools_institutionlanguage.csv' NULL 'null' DELIMITER   ',' quote '\\\"' csv;",
        }
]

#Create directory and files
def init():
    if not os.path.exists("load"):
    	os.makedirs("load")
    inputfile=open(inputdatafile,'w',0)
    loadfile=open(loaddatafile,'w',0)
    command="psql -U klp -d "+emsdatabase+" -f cleanems.sql"
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
  command="psql -U klp -d "+emsdatabase+" -f "+inputdatafile
  system(command)


#Running the "copy from" commands for loading the db.
def loaddata():
  command="psql -U klp -d "+todatabase+" -f "+loaddatafile+" 1>output 2>error"
  print>>sys.stderr, command
  system(command)

#Reset Sequences
#https://wiki.postgresql.org/wiki/Fixing_Sequences
def resetseq():
    command="psql -U klp -d "+todatabase+" -f "+resetseq.sql+" 1>seq_out 2>seq_err"
    system(command)


#order in which function should be called.
init()
create_sqlfiles()
getdata()
#loaddata()
#resetseq()

