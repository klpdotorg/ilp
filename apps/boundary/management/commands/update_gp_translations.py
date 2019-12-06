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
    def add_arguments(self, parser):
        parser.add_argument('file')

    def handle(self, *args, **options):
        file_name = options.get('file', None).title()
        if not file_name:
            print("Please pass in a file path for the CSV file with translations")
            return False
        translated_gps = pandas.read_csv(file_name)
        cursor = connection.cursor()
        for index, db_gp_row in translated_gps.iterrows():
            sql = "UPDATE boundary_electionboundary SET const_ward_lang_name=\'{0}\' WHERE id={1}".format(db_gp_row['gp_lang_name'], db_gp_row['gp_id'])
            print(sql)
            cursor.execute(sql)
        connection.commit()