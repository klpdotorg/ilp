'''
This file takes in a CSV of district names in English and a regional
lang as input. Right now, sample is Kannada. Compares the DB name field against
the English name field of the CSV. It updates the DB "lang_name" field in the 
boundary table with the proper
regional name IF it finds a match for the English name in the CSV file.
The column names are fixed -- namely name and lang_name. So CSVs should be
prepared with these column headings
'''
from django.core.management.base import BaseCommand
from django.db import connection, transaction
import pandas
import pandas.io.sql as psql
from fuzzywuzzy import fuzz
from fuzzywuzzy import process 

class Command(BaseCommand):
    def handle(self, *args, **options):
        translated_gps = pandas.read_csv('apps/boundary/management/commands/csvs/KA_boundaries/KA_gp_names_translations.csv')
        cursor = connection.cursor()
        gps_from_db = pandas.read_sql_query('select distinct eb.id as gp_id, eb.const_ward_name as gp_name, b1.id as district_id, b1.name as district_name, b2.id as block_id, b2.name as block_name from boundary_boundary b1, boundary_boundary b2, schools_institution schools, boundary_electionboundary eb where schools.gp_id=eb.id and eb.const_ward_type_id=\'GP\' and eb.state_id=2 and schools.admin1_id=b1.id and schools.admin2_id=b2.id',con=connection)
        gps_from_db["english_match"]=""
        gps_from_db["kannada_text"] = ""
        print(gps_from_db.columns)
        for index, db_gp_row in gps_from_db.iterrows():
            result = process.extractOne(db_gp_row['gp_name'],translated_gps['gp_name'])
            if result[1] == 100:
                sql = "UPDATE boundary_electionboundary SET const_ward_lang_name=\'{0}\' WHERE id={1}".format(translated_gps['gp_lang_name'][result[2]], db_gp_row['gp_id'])
                cursor.execute(sql)
            else:
                print("No exact match found for the following. Please check:")
                print("For %s, the NEAREST match is: %s " % (db_gp_row['gp_name'],result))
        connection.commit()