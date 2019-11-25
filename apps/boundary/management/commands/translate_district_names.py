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
        rdpr_districts = pandas.read_csv('apps/boundary/management/commands/csvs/KA_boundaries/KA_unique_districts_all_translations.csv')
        print(rdpr_districts)
        cursor = connection.cursor()
        df = pandas.read_sql_query('select id,name from boundary_boundary where parent_id=2 and boundary_type_id=\'SD\'',con=connection)
        df['lang_name'] = ""
        print(df)
        db_district_names = df["name"]
        print(db_district_names)
        for index, row in df.iterrows():
            result = process.extractOne(row['name'], rdpr_districts['english_name'])
            # Picking 85 as the boundary for acceptable translations because
            # for most regional names this works. Any output of this script
            # needs to get reviewed anyway for accuracy.
            if result[1] > 85:
                # print("For %s, the BEST match is: %s " % (row['name'],result))
                df.at[index,'lang_name'] = rdpr_districts['lang_name'][result[2]]
                sql = "UPDATE boundary_boundary SET lang_name=\'{0}\' WHERE id={1}".format(rdpr_districts['lang_name'][result[2]], row['id'])
                cursor.execute(sql)
            else:
                print("For %s, the NEAREST match is: %s " % (row['name'],result))
        connection.commit()
        result_df = pandas.read_sql_query('select id,name, lang_name from boundary_boundary where parent_id=2 and boundary_type_id=\'SD\'',con=connection)
        print(result_df)