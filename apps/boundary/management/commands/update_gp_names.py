'''
Use this command to mass update gp names in the DB with a CSV file as input. 
The column names need to be id, const_ward_name in the CSV file
Doing this to mass update GP names from which brackets were stripped to 
eliminate some mistakes 
'''
from django.core.management.base import BaseCommand
from django.db import connection, transaction
import pandas
import pandas.io.sql as psql

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--file', nargs='?')

    def handle(self, *args, **options):
        file_name = options.get("file", None)
        if not file_name:
            print("Please pass in a file path for the CSV file with GP names")
            return False
        gps_file = pandas.read_csv(file_name)
        cursor = connection.cursor()
        for index, gp_row in gps_file.iterrows():
            sql = "UPDATE boundary_electionboundary SET const_ward_name=\'{0}\' WHERE id={1}".format(gp_row['const_ward_name'], gp_row['id'])
            print(sql)
            cursor.execute(sql)
        connection.commit()