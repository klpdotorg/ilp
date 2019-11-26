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
        blocks = pandas.read_csv('apps/boundary/management/commands/csvs/KA_boundaries/KA_unique_blocks_all_translations.csv')
        print(blocks)
        cursor = connection.cursor()
        df = pandas.read_sql_query('select b1.id,b1.name from boundary_boundary b1, boundary_boundary b2 where b1.parent_id=b2.id AND b2.parent_id=2 and b1.boundary_type_id=\'SB\'',con=connection)
        df['lang_name'] = ""
        print(df)
        db_block_names = df["name"]
        df["english_match"]=""
        df["kannada_text"]=""
        for index, row in df.iterrows():
            result = process.extractOne(row['name'],blocks['block_name'])
            if result[1] > 85:
                sql = "UPDATE boundary_boundary SET lang_name=\'{0}\' WHERE id={1}".format(blocks['block_kannada_name'][result[2]], row['id'])
                cursor.execute(sql)
            else:
                print("No exact match found for the following. Please check:")
                print("For %s, the NEAREST match is: %s " % (row['name'],result))
                row["english_match"]=blocks['block_name'][result[2]]
                row["kannada_match_text"]=blocks['block_name_kannada'][result[2]]
        connection.commit()