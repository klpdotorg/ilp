from os import system, sys
import os
import inspect

# SSA coords file is expected to have 3 columns in the order:- dise code, latitude and longitude
if len(sys.argv) != 3:
    print("Please give csv filename and database name as arguments. USAGE: python updateinstitutioncoords.py ssa_coords.csv ilp")
    sys.exit()


basename = "instcoord"
scriptdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

fromfile = sys.argv[1]
todatabase = sys.argv[2]

tempdatafile = scriptdir+"/"+basename+"_tempdata.sql"

tables = [
        {
            'name': 'update_instcoord',
            'tablename': 'schools_institution',
            'temptablename': 'temp_coords',
            'createcolumns': 'dise_code text, latitude text, longitude text',
            'columns': 'dise_code, latitude, longitude',
            'update_query': "UPDATE schools_institution set coord=ST_GeomFromText('POINT(' || coords.longitude || ' ' || coords.latitude || ')', 4326) from temp_coords coords,dise_basicdata where coords.dise_code::bigint = dise_basicdata.school_code and dise_basicdata.academic_year_id = '1617' and dise_basicdata.id = schools_institution.dise_id;"
        }
]


# Create directory and files
def init():
    if not os.path.exists(scriptdir+"/load"):
        os.makedirs(scriptdir+"/load")
    open(tempdatafile, 'wb', 0)


# Create the temp sql files with the db commands for creating temp table, filling it
# and updating the institution table accordingly.
def create_sqlfiles():
    # Loop through the tables
    for table in tables:

        # create temp table
        open(fromfile, 'r')
        system('echo "CREATE TEMP TABLE '+table['temptablename']+'('+table['createcolumns']+');"'+'>>'+tempdatafile)

        # create sql file to copy into the temp table and then update
        system('echo "\COPY '+table['temptablename']+"("+table['columns']+") from '"+fromfile+"' with csv NULL 'null';"+'\">>'+tempdatafile)
        system('echo "'+table['update_query']+'">>'+tempdatafile)


# Running the "copy from" commands for loading the db.
def loaddata():
    system("psql -U klp -d "+todatabase+" -f "+tempdatafile)


# order in which function should be called.
init()
create_sqlfiles()
loaddata()
