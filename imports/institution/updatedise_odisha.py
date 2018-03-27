from os import system, sys
import os
import inspect

if len(sys.argv) != 3:
    print("Please give file names(full path) and database names as arguments. USAGE: python updatedise_odisha.py `pwd`/ilp_odishadise.csv ilp")
    sys.exit()


fromfilename = sys.argv[1]

todatabase = sys.argv[2]

basename = "dise_odisha"
scriptdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

inputsqlfile = scriptdir+"/"+basename+"_getdata.sql"
loadsqlfile = scriptdir+"/"+basename+"_loaddata.sql"

tables = [
        {
            'name': 'update_dise',
            'tablename': 'schools_institution',
            'tempquery': "CREATE TEMP TABLE temp_replacename(school_id int,dise_code bigint); \COPY temp_replacename(school_id,dise_code) FROM '"+fromfilename+"' with csv NULL 'null';",
            'updatequery': "UPDATE replacetablename set dise_id=dise.id from temp_replacename temp, dise_basicdata dise where temp.dise_code=dise.school_code and temp.school_id=schools_institution.id;"
        }
]


# Create directory and files
def init():
    if not os.path.exists(scriptdir+"/load"):
        os.makedirs(scriptdir+"/load")
    open(inputsqlfile, 'wb', 0)
    open(loadsqlfile, 'wb', 0)


# Create the getdata.sql and loaddata.sql files
# getdata.sql file has the "Copy to" commands for populating the various csv files
# loaddata.sql file has the "copy from" commands for loading the data into the db
def create_sqlfiles():
    # Loop through the tables
    for table in tables:
        filename = scriptdir+'/load/'+table['name']+'.csv'
        open(filename, 'wb', 0)
        os.chmod(filename, 0o666)
        if 'getquery' in table:
            command = 'echo "'+table['getquery'].replace('replacetablename', table['tablename']).replace('replacefilename', filename).replace('replacename', table['name'])+'">>'+inputsqlfile
            system(command)
        if 'tempquery' in table:
            command = 'echo "'+table['tempquery'].replace('replacetablename', table['tablename']).replace('replacefilename', filename).replace('replacename', table['name'])+'">>'+loadsqlfile
            system(command)
        if 'updatequery' in table:
            command = 'echo "'+table['updatequery'].replace('replacetablename', table['tablename']).replace('replacefilename', filename).replace('replacename', table['name'])+'">>'+loadsqlfile
            system(command)



# Running the "copy from" commands for loading the db.
def loaddata():
    system("psql -U klp -d "+todatabase+" -f "+loadsqlfile)


# order in which function should be called.
init()
create_sqlfiles()
loaddata()
