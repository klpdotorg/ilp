from os import system, sys
import os
import inspect

if len(sys.argv) != 3:
    print("Please give csv filename and database name as arguments. USAGE: python updateinstitutiongpdata.py gp_schoolmapping.csv ilp")
    sys.exit()


basename = "gpmapping"
scriptdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

fromfile = sys.argv[1]
todatabase = sys.argv[2]

tempdatafile = scriptdir+"/"+basename+"_tempdata.sql"

tables = [
        {
            'name': 'update_instgpdata',
            'tablename': 'schools_institution',
            'temptablename': 'temp_gpdata',
            'createcolumns': 'institution_id integer, gp_id integer',
            'columns': 'institution_id, gp_id',
            'update_query': "UPDATE schools_institution set gp_id=temp.gp_id from temp_gpdata temp, boundary_electionboundary eb where schools_institution.id=temp.institution_id and eb.id=temp.gp_id and eb.const_ward_type_id ='GP';"
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
