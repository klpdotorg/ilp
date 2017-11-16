from os import system,sys
import os, inspect


if len(sys.argv) != 3:
    print("Please give database names as arguments. USAGE: python import_studentgrouprelations_data.py ems ilp")
    sys.exit()

#Before running this script
#change this to point to the ems database that is used for getting the data
fromdatabase = sys.argv[1]

#change this to ilp db to be populated with
todatabase = sys.argv[2]

basename = "sgrel"
scriptdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

inputdatafile =  scriptdir+"/"+basename+"_getdata.sql"
tempdatafile =  scriptdir+"/"+basename+"_tempdata.sql"

tables=[
    {
        'name': 'schools_staffstudentgrouprelation',
        'temptablename': 'temp_staffstudentgrouprelation',
        'table_name': 'schools_staffstudentgrouprelation',
        'tempcolumns': 'id integer, academic_year_id text, staff_id integer, status_id text, student_group_id integer',
        'columns': 'id, academic_year_id, staff_id, status_id, student_group_id',
        'tempquery': "\COPY (select st.id, concat(substr(split_part(ay.name, '-',1),3,4), substr(split_part(ay.name,'-',2),3,4)), st.staff_id, case st.active when 2 then 'AC' when 1 then 'IA' when 0 then 'DL' end, st.student_group_id from schools_staff_studentgrouprelation st, schools_academic_year ay where st.academic_id=ay.id) TO '"+scriptdir+"/load/schools_staffstudentgrouprelation.csv' NULL 'null' DELIMITER ',' quote '\\\"' csv;",
        'insertquery': "INSERT into schools_staffstudentgrouprelation(id, academic_year_id, staff_id, status_id, student_group_id) select temp.id,temp.academic_year_id,temp.staff_id,temp.status_id,temp.student_group_id from temp_staffstudentgrouprelation temp,schools_staff st, schools_studentgroup sg where temp.staff_id=st.id and temp.student_group_id=sg.id;"
    },
    {
        'name': 'schools_studentstudentgrouprelation',
        'temptablename': 'temp_stustudentgrouprelation',
        'table_name': 'schools_studentstudentgrouprelation',
        'tempcolumns': 'academic_year_id text, status_id text, student_id integer, student_group_id integer',
        'columns': 'academic_year_id, status_id, student_id, student_group_id',
        'tempquery': "\COPY (select concat(substr(split_part(ay.name, '-',1),3,4), substr(split_part(ay.name,'-',2),3,4)), case stusg.active when 2 then 'AC' when 1 then 'IA' when 0 then 'DL' end,stusg.student_id, stusg.student_group_id from schools_student_studentgrouprelation stusg, schools_academic_year ay,schools_studentgroup sg where stusg.academic_id=ay.id and stusg.student_group_id=sg.id and stusg.active in (0,1,2)) TO '"+scriptdir+"/load/schools_studentstudentgrouprelation.csv' NULL 'null' DELIMITER ',' quote '\\\"' csv;",
        'insertquery': "INSERT into schools_studentstudentgrouprelation(academic_year_id, status_id, student_id, student_group_id) select distinct temp.academic_year_id,temp.status_id,temp.student_id,temp.student_group_id from temp_stustudentgrouprelation temp,schools_student stu, schools_studentgroup sg where temp.student_id=stu.id and temp.student_group_id=sg.id;"
    }

]

#Create directory and files
def init():
    if not os.path.exists(scriptdir+"/load"):
    	os.makedirs(scriptdir+"/load")
    inputfile = open(inputdatafile,'wb',0)
    tempfile = open(tempdatafile,'wb',0)


#Create the getdata.sql and loaddata.sql files
# getdata.sql file has the "Copy to" commands for populating the various csv files
# loaddata.sql file has the "copy from" commands for loading the data into the db
def create_sqlfiles():
    #Loop through the tables
    for table in tables:
        system('echo "'+table['tempquery']+'\">>'+inputdatafile)

        #create temp table
        system('echo "CREATE TEMP TABLE '+table['temptablename']+'('+table['tempcolumns']+');"'+'>>'+tempdatafile)

        #create the file where the data will be written into
        filename = scriptdir+'/load/'+table['name']+'.csv'
        open(filename,'wb',0)
        os.chmod(filename,0o666)

        #write commands for creating temp table and copying data into it
        system('echo "\COPY '+table['temptablename']+"("+table['columns']+") from '"+filename+"' with csv NULL 'null';"+'\">>'+tempdatafile)

        #get data from temp table and fill only for students present in the db
        system('echo "'+table['insertquery']+'">>'+tempdatafile)


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
