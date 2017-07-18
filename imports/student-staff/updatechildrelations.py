from os import system,sys
import os


if len(sys.argv) != 3:
    print("Please give database names as arguments. USAGE: python updatechildrelations.py ems ilp", file=sys.stderr)
    sys.exit()

#Before running this script
#change this to point to the ems database that is used for getting the data
fromdatabase = sys.argv[1]

#change this to ilp db to be populated with
todatabase = sys.argv[2]

basename = "rel"

inputdatafile = basename+"_getdata.sql"
tempdatafile = basename+"_tempdata.sql"

# name stores the name of file where copy is done. temptablename is the name of temporary table that is created.
# table_name is name of the table that is to be updated.
# tempcolumns are the colums that are to be created in temp table.
# columsn are the columns to be filled in temp table. The count of this and tempcolumns should match
# tempquery is the query that is used to fill the temp table
# updatequery is the query that is to be used for updating the table.
tables=[
    {
        'name': 'updaterel',
        'temptablename': 'temp_rel',
        'table_name': 'schools_student',
        'tempcolumns': 'stuid integer, mothername text, fathername text',
        'columns': 'stuid, mothername, fathername',
        'tempquery': "COPY(select stu.id,concat_ws('',trim(r.first_name),' ',trim(r.middle_name),' ',trim(r.last_name)) as mothername, concat_ws('',trim(r1.first_name),' ',trim(r1.middle_name),' ',trim(r1.last_name)) as fathername from schools_student stu left outer join schools_relations r on (stu.child_id=r.child_id and r.relation_type='Mother') left outer join schools_relations r1 on (stu.child_id=r1.child_id and r1.relation_type='Father') where trim(concat_ws('',r.first_name,' ',r.middle_name,' ',r.last_name))!='' or trim(concat_ws('',r1.first_name,' ',r1.middle_name,' ',r1.last_name)) !='') TO '$PWD/load/updaterel.csv' NULL 'null' DELIMITER ',' quote '\\\"' csv;",
        'updatequery': "UPDATE schools_student set mother_name=temp_rel.mothername, father_name=temp_rel.fathername from temp_rel where id=temp_rel.stuid;"
    }
]

#Create directory and files
def init():
    if not os.path.exists("load"):
    	os.makedirs("load")
    inputfile = open(inputdatafile,'wb',0)
    tempfile = open(tempdatafile,'wb',0)
    system('psql -U klp -d '+fromdatabase+' -f cleanems.sql')


#Create the getdata.sql and loaddata.sql files
# getdata.sql file has the "Copy to" commands for populating the various csv files
# loaddata.sql file has the "copy from" commands for loading the data into the db
def create_sqlfiles():
    #Loop through the tables
    for table in tables:
        #create the "copy to" query file to get data from ems
        system('echo "'+table['tempquery']+'\">>'+inputdatafile)

        #create the file where the data will be written into
        filename = os.getcwd()+'/load/'+table['name']+'.csv'
        open(filename,'wb',0)
        os.chmod(filename,0o666)

        #write commands for creating temp table and copying data into it
        system('echo "CREATE TEMP TABLE '+table['temptablename']+'('+table['tempcolumns']+');"'+'>>'+tempdatafile)
        system('echo "COPY '+table['temptablename']+"("+table['columns']+") from '"+filename+"' with csv NULL 'null';"+'\">>'+tempdatafile)

        #get data from temp table and fill only for students present in the db
        system('echo "'+table['updatequery']+'">>'+tempdatafile)


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
