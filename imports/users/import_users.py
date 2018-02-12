from os import system, sys
import os, inspect


if len(sys.argv) != 3:
    print("Please give database names as arguments. USAGE:" +
          "python import_users.py dubdubdub ilp")
    sys.exit()

fromdatabase = sys.argv[1]

todatabase = sys.argv[2]

basename = "users"
scriptdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
inputsqlfile = scriptdir+"/"+basename+"_getdata.sql"
loadsqlfile = scriptdir+"/"+basename+"_loaddata.sql"

tables = [
    {
        'table_name': 'users_user',
        'name': 'users_user',
        'getquery': "\COPY (select id, password, last_login, is_superuser, email, mobile_no, null, first_name, last_name, case user_type when 'teachers' then 'TR' when 'local-leaders' then 'LL' when 'parents' then 'PR' when 'sdmc-member' then 'SM' when 'educated-youth' then 'EY' when 'crp' then 'CRP' when 'elected-representative' then 'ER' when 'cbo-member' then 'CM' when 'headmaster' then 'HM' when 'akshara-staff' then 'AS' when 'BFC' then 'AS' when 'No' then null else user_type end, is_active, about, changed, created, dob, email_verification_code, fb_url, image, is_email_verified, is_mobile_verified, opted_email, photos_url, sms_verification_pin, source, twitter_handle, website, youtube_url from users_user where mobile_no not like '%,%') TO 'replacefilename' NULL 'null' DELIMITER ',' quote '\\\"' csv;",
        'insertquery': "\COPY replacetablename(id, password, last_login, is_superuser, email, mobile_no, mobile_no1, first_name, last_name, user_type_id, is_active, about, changed, created, dob, email_verification_code, fb_url, image, is_email_verified, is_mobile_verified, opted_email, photos_url, sms_verification_pin, source, twitter_handle, website, youtube_url) FROM 'replacefilename' with csv NULL 'null';"
    },
    {
        'table_name': 'users_user',
        'name': 'users_user_update',
        'getquery': "\COPY (select id, password, last_login, is_superuser, email, split_part(mobile_no,',',1), split_part(mobile_no,',',2), first_name, last_name, case user_type when 'teachers' then 'TR' when 'local-leaders' then 'LL' when 'parents' then 'PR' when 'sdmc-member' then 'SM' when 'educated-youth' then 'EY' when 'crp' then 'CRP' when 'elected-representative' then 'ER' when 'cbo-member' then 'CM' when 'headmaster' then 'HM' when 'akshara-staff' then 'AS' when 'No' then null end, is_active, about, changed, created, dob, email_verification_code, fb_url, image, is_email_verified, is_mobile_verified, opted_email, photos_url, sms_verification_pin, source, twitter_handle, website, youtube_url from users_user where mobile_no like '%,%') TO 'replacefilename' NULL 'null' DELIMITER ',' quote '\\\"' csv;",
        'tempquery': "CREATE TEMP TABLE temp_replacetablename(id integer, password text, last_login timestamp, is_superuser boolean, email text, mobile_no text, mobile_no1 text, first_name text, last_name text, user_type text, is_active boolean, about text, changed timestamp, created timestamp, dob date, email_verification_code text, fb_url text, image text, is_email_verified boolean, is_mobile_verified boolean, opted_email boolean, photos_url text, sms_verification_pin integer, source text, twitter_handle text, website text, youtube_url text); \COPY temp_replacetablename(id, password, last_login, is_superuser, email, mobile_no, mobile_no1, first_name, last_name, user_type, is_active, about, changed, created, dob, email_verification_code, fb_url, image, is_email_verified, is_mobile_verified, opted_email, photos_url, sms_verification_pin, source, twitter_handle, website, youtube_url) FROM 'replacefilename' with csv NULL 'null';",
        'insertquery': "INSERT INTO replacetablename(id, password, last_login, is_superuser, email, mobile_no, mobile_no1, first_name, last_name, user_type_id, is_active, about, changed, created, dob, email_verification_code, fb_url, image, is_email_verified, is_mobile_verified, opted_email, photos_url, sms_verification_pin, source, twitter_handle, website, youtube_url) select id, password, last_login, is_superuser, email, mobile_no, mobile_no1, first_name, last_name, user_type, is_active, about, changed, created, dob, email_verification_code, fb_url, image, is_email_verified, is_mobile_verified, opted_email, photos_url, sms_verification_pin, source, twitter_handle, website, youtube_url from temp_replacetablename where mobile_no not in (select mobile_no from users_user);",
        'updatequery': "UPDATE replacetablename set mobile_no1=temp.mobile_no1 from (select mobile_no, mobile_no1 from temp_replacetablename)temp where replacetablename.mobile_no = temp.mobile_no and replacetablename.mobile_no1 is null;"
    },
    {
        'table_name': 'users_user_groups',
        'name': 'users_user_groups',
        'insertquery': "INSERT INTO replacetablename(user_id, group_id) select users.id,groups.id from users_user users, auth_group groups where groups.name in ('ilp_auth_user', 'ilp_konnect_user');"
    },
    {
        'table_name': 'users_userboundary',
        'name':'users_userboundary',
        'getquery': "\COPY (select distinct id, boundary_id, user_id from schools_boundaryusers) TO 'replacefilename' NULL 'null' DELIMITER ',' quote '\\\"' csv;",
        'tempquery': "CREATE TEMP TABLE temp_replacetablename(id integer, boundary_id integer, user_id integer); \COPY temp_replacetablename(id, boundary_id, user_id) FROM 'replacefilename' with csv NULL 'null';",
        'insertquery': "INSERT INTO replacetablename(id, boundary_id, user_id) select temp.id, temp.boundary_id, temp.user_id from temp_replacetablename temp, users_user user1, boundary_boundary b  where temp.user_id=user1.id and temp.boundary_id=b.id;"
    },
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
            command = 'echo "'+table['getquery'].replace('replacetablename', table['table_name']).replace('replacefilename', filename)+'">>'+inputsqlfile
            system(command)
        if 'tempquery' in table:
            command = 'echo "'+table['tempquery'].replace('replacetablename', table['table_name']).replace('replacefilename', filename)+'">>'+loadsqlfile
            system(command)
        if 'insertquery' in table:
            command = 'echo "'+table['insertquery'].replace('replacetablename', table['table_name']).replace('replacefilename', filename)+'">>'+loadsqlfile
            system(command)
        if 'updatequery' in table:
            command = 'echo "'+table['updatequery'].replace('replacetablename', table['table_name']).replace('replacefilename', filename)+'">>'+loadsqlfile
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
