from os import system,sys
import os, inspect

if len(sys.argv) != 4:
    print("Please give database and file names(full path) as arguments. USAGE: python updateinstitutiondata.py dubdubdub `pwd`/ssa_details.csv ilp", file=sys.stderr)
    sys.exit()


fromdatabase = sys.argv[1]

fromfilename = sys.argv[2]

todatabase = sys.argv[3]

basename = "instupdate"
scriptdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

inputsqlfile = scriptdir+"/"+basename+"_getdata.sql"
loadsqlfile = scriptdir+"/"+basename+"_loaddata.sql"

tables=[
        {
            'name': 'update_ssadata',
            'tablename': 'schools_institution',
            'tempquery': "CREATE TEMP TABLE temp_replacename(dise_code bigint,village text,phone_number text,rural_urban text, year_established text); \COPY temp_replacename(dise_code,village,phone_number,rural_urban,year_established) FROM '"+fromfilename+"' with csv NULL 'null';",
            'updatequery': "UPDATE replacetablename set year_established=trim(temp.year_established), rural_urban=temp.rural_urban, village=temp.village, phone_number=temp.phone_number from temp_replacename temp, dise_basicdata dise where temp.dise_code=dise.school_code and dise.id=schools_institution.dise_id;"
        },
        {
            'name': 'update_electedrep',
            'tablename': 'schools_institution',
            'getquery': "\COPY (select sid, ward_id, mla_const_id, mp_const_id from mvw_school_electedrep) TO 'replacefilename.csv' NULL 'null' DELIMITER ',' quote '\\\"' csv;",
            'tempquery': "CREATE TEMP TABLE temp_replacename(sid integer, ward_id integer, mla_id integer, mp_id integer); \COPY temp_replacename(sid, ward_id, mla_id, mp_id) FROM 'replacefilename.csv' with csv NULL 'null';",
            'updatequery': "UPDATE replacetablename set mp_id=temp.mp_id, mla_id=temp.mla_id, ward_id=temp.ward_id from temp_replacename temp where schools_institution.id = temp.sid;"
        }
]

#Create directory and files
def init():
    if not os.path.exists(scriptdir+"/load"):
    	os.makedirs(scriptdir+"/load")
    open(inputsqlfile, 'wb', 0)
    open(loadsqlfile, 'wb', 0)


#Create the getdata.sql and loaddata.sql files
# getdata.sql file has the "Copy to" commands for populating the various csv files
# loaddata.sql file has the "copy from" commands for loading the data into the db
def create_sqlfiles():
    #Loop through the tables
    for table in tables:
        filename = scriptdir+'/load/'+table['name']+'.csv'
        open(filename, 'wb', 0)
        os.chmod(filename, 0o666)
        if 'getquery' in table:
            command = 'echo "'+table['getquery'].replace('replacetablename', table['tablename']).replace('replacefilename', filename).replace('replacename',table['name'])+'">>'+inputsqlfile
            system(command)
        if 'tempquery' in table:
            command = 'echo "'+table['tempquery'].replace('replacetablename', table['tablename']).replace('replacefilename', filename).replace('replacename',table['name'])+'">>'+loadsqlfile
            system(command)
        if 'updatequery' in table:
            command = 'echo "'+table['updatequery'].replace('replacetablename', table['tablename']).replace('replacefilename', filename).replace('replacename',table['name'])+'">>'+loadsqlfile
            system(command)



#Running the "copy to" commands to populate the csvs.
def getdata():
    print("GET DATA")
    system("psql -U klp -d "+fromdatabase+" -f "+inputsqlfile)


#Running the "copy from" commands for loading the db.
def loaddata():
    print("LOAD DATA")
    system("psql -U klp -d "+todatabase+" -f "+loadsqlfile)


#order in which function should be called.
init()
create_sqlfiles()
getdata()
loaddata()
