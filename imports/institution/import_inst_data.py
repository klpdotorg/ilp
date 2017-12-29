from os import system, sys
import os
import inspect


if len(sys.argv) != 3:
    print("Please give database names as arguments. USAGE: python import_inst_data.py ems ilp")
    sys.exit()

fromdatabase = sys.argv[1]

todatabase = sys.argv[2]

basename = "inst"
scriptdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

mt_conv = "when 1 then 'kan' when 2 then 'urd' when 3 then 'tam' when 4 then 'tel' when 5 then 'eng' when 6 then 'mar' when 7 then 'hin' when 8 then 'kon' when 9 then 'sin' when 10    then 'oth' when 11 then 'guj' when 12 then 'unknown' when 13 then 'multi' when 14 then   'nep' when 15 then 'ori' when 16 then 'ben' when 17 then 'mal' when 18 then 'san' when   19 then 'lam'"

inputdatafile = scriptdir+"/"+basename+"_getdata.sql"
loaddatafile = scriptdir+"/"+basename+"_loaddata.sql"

tables = [
    {
        'name': 'schools_institution',
        'columns': 'id, name, admin0_id,admin1_id,admin2_id, admin3_id, category_id, gender_id, institution_type_id, management_id, status_id, address, area, landmark, instidentification,instidentification2, route_information',
        'query': "\COPY (select s.id, s.name, 2, admin1.id, admin2.id, admin3.id, s.cat_id, s.institution_gender, case admin3.boundary_type_id when 1 then 'primary' when 2 then 'pre' end, s.mgmt_id, 'AC', add.address, add.area, add.landmark, add.instidentification, add.instidentification2, add.route_information  from schools_institution s left outer join schools_institution_address add on (s.inst_address_id = add.id), schools_boundary admin3, schools_boundary admin2, schools_boundary admin1 where s.boundary_id=admin3.id and admin3.parent_id=admin2.id and admin2.parent_id=admin1.id and s.active=2) TO '"+scriptdir+"/load/schools_institution.csv' NULL 'null' DELIMITER   ',' quote '\\\"' csv;",
    },
    {
        'name': 'schools_institutionlanguage',
        'columns': 'id, institution_id, moi_id',
        'query': "\COPY (select lang.id,lang.institution_id,case lang.moi_type_id "+mt_conv+" end  from schools_institution_languages lang, schools_institution s where lang.institution_id=s.id  and s.active=2) TO '"+scriptdir+"/load/schools_institutionlanguage.csv' NULL 'null' DELIMITER   ',' quote '\\\"' csv;",
    }
]


# Create directory and files
def init():
    if not os.path.exists(scriptdir+"/load"):
        os.makedirs(scriptdir+"/load")
    open(inputdatafile, 'wb', 0)
    open(loaddatafile, 'wb', 0)
    system("psql -U klp -d "+fromdatabase+" -f "+scriptdir+"/cleanems.sql")


# Create the getdata.sql and loaddata.sql files
# getdata.sql file has the "Copy to" commands for populating the various csv files
# loaddata.sql file has the "copy from" commands for loading the data into the db
def create_sqlfiles():
    # Loop through the tables
    for table in tables:
        # create the "copy to" file to get data from ems
        system('echo "'+table['query']+'\">>'+inputdatafile)

        # create the "copy from" file to load data into db
        filename = scriptdir+'/load/'+table['name']+'.csv'
        open(filename, 'wb', 0)
        os.chmod(filename, 0o666)

        system('echo "\COPY '+table['name']+"("+table['columns']+") from '"+filename+"' with csv NULL 'null';"+'\">>'+loaddatafile)


# Running the "copy to" commands to populate the csvs.
def getdata():
    system("psql -U klp -d "+fromdatabase+" -f "+inputdatafile)


# Running the "copy from" commands for loading the db.
def loaddata():
    system("psql -U klp -d "+todatabase+" -f "+loaddatafile)


# order in which function should be called.
init()
create_sqlfiles()
getdata()
loaddata()
