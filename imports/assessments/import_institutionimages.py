from os import system, sys
import os
import inspect


if len(sys.argv) != 3:
    print("Please give database names as arguments. USAGE: " +
          "python import_institutionimages.py dubdubdub ilp")
    sys.exit()

fromdatabase = sys.argv[1]

todatabase = sys.argv[2]

basename = "images"
scriptdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
inputsqlfile = scriptdir+"/"+basename+"_getdata.sql"
loadsqlfile = scriptdir+"/"+basename+"_loaddata.sql"

tables = [
    {
        'name': 'assessments_institutionimages',
        'getquery': "\COPY (select img.image, img.is_verified, img.filename, img.story_id, story.school_id from stories_storyimage img, stories_story story where img.story_id=story.id) TO 'replacefilename' NULL 'null' DELIMITER ',' quote '\\\"' csv;",
        'tempquery': "CREATE TEMP TABLE temp_replacetablename(image text, is_verified boolean, filename text, story_id integer, school_id integer); \COPY temp_replacetablename(image, is_verified, filename, story_id, school_id) FROM 'replacefilename' with csv NULL 'null';",
        'insertquery': "INSERT INTO replacetablename(image, is_verified, filename, answergroup_id) select temp.image, temp. is_verified, temp.filename, temp.story_id from temp_replacetablename temp, assessments_answergroup_institution answergroup where temp.story_id=answergroup.id and temp.school_id = answergroup.institution_id;"
    }
]


# Create directory and files
def init():
    if not os.path.exists(scriptdir+"/load"):
        os.makedirs(scriptdir+"/load")
    open(inputsqlfile, 'wb', 0)
    open(loadsqlfile, 'wb', 0)


def create_sqlfiles():
    # Loop through the tables
    for table in tables:
        filename = scriptdir+'/load/'+basename+'_'+table['name']+'.csv'
        open(filename, 'wb', 0)
        os.chmod(filename, 0o666)
        if 'getquery' in table:
            command = 'echo "'+table['getquery'].replace('replacetablename', table['name']).replace('replacefilename', filename)+'">>'+inputsqlfile
            system(command)
        if 'tempquery' in table:
            command = 'echo "'+table['tempquery'].replace('replacetablename', table['name']).replace('replacefilename', filename)+'">>'+loadsqlfile
            system(command)
        if 'insertquery' in table:
            command = 'echo "'+table['insertquery'].replace('replacetablename', table['name']).replace('replacefilename', filename)+'">>'+loadsqlfile
            system(command)


def get_data():
    system('psql -U klp -d '+fromdatabase+' -f '+inputsqlfile)


def load_data():
    system('psql -U klp -d '+todatabase+' -f '+loadsqlfile)


# order in which function should be called.
init()
create_sqlfiles()
get_data()
load_data()
