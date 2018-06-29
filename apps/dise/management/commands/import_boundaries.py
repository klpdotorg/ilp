import os
import sys
import csv
import psycopg2
import re
from django.core.management.base import BaseCommand
from django.core.exceptions import MultipleObjectsReturned
from django.db import transaction
from django.conf import settings
from common.models import Status, InstitutionType
from boundary.models import Boundary, BoundaryType


class Command(BaseCommand):
    active_status = Status.objects.get(char_id='AC')
    boundaries = ["district", "block", "cluster"]
    select_queries = { "district": "select district, slug from dise_replaceyear_district_aggregations where lower(state_name) = %s",
                        "block": "select block_name, slug, district from dise_replaceyear_block_aggregations where lower(state_name) = %s",
                        "cluster": "select cluster_name, slug, block_name from dise_replaceyear_cluster_aggregations where lower(state_name) = %s"}

       
    #help = """Import data from DISE 

    #./manage.py importboundaries dise_dbname dise_db_username dise_db_passwd dise_db_host state academic_year"""

    def add_arguments(self, parser):
        parser.add_argument('dbname')
        parser.add_argument('user')
        parser.add_argument('passwd')
        parser.add_argument('host')
        parser.add_argument('state')
        parser.add_argument('academic_year')

    def connectDISE(self,dbname,user,passwd,host):
        connectionstring = "dbname="+dbname+" user="+user+" password="+passwd+" host="+host
        connection = psycopg2.connect(connectionstring)
        cursor = connection.cursor()
        return connection, cursor

    def insertBoundary(self, name, slug, parent_name, boundary_type_name):
        print("Trying to create: "+name)
        if boundary_type_name == 'district':
            parent_type = BoundaryType.objects.get(pk='ST')
        elif boundary_type_name == 'block':
            parent_type = BoundaryType.objects.get(pk='SD')
        else:
            parent_type = BoundaryType.objects.get(pk='SB')

        try:
            parent_boundary = Boundary.objects.get(name__iexact=parent_name, boundary_type = parent_type)
        except MultipleObjectsReturned:
            print("MULTIPLE FOUND :"+parent_name+" "+parent_type.char_id)
            parent_boundary = Boundary.objects.filter(name__iexact=parent_name, boundary_type = parent_type)
            for parent in parent_boundary:
                print(parent.id)
            parent_boundary = parent_boundary[0]
        except Boundary.DoesNotExist:
            print("Parent Boundary not found "+parent_name)                  
            return

        boundary_type_name = "school "+boundary_type_name
        boundary_type = BoundaryType.objects.get(name__iexact= boundary_type_name)
        type = InstitutionType.objects.get(pk='primary')
        print(name+" "+slug+" "+str(parent_boundary.id))
        boundary,created = Boundary.objects.get_or_create(name = name,
                                dise_slug = slug,
                                parent = parent_boundary,
                                boundary_type = boundary_type,
                                status = self.active_status,
                                type = type)
        print("created: "+str(created)+" boundary id: "+str(boundary.id))


    def handle(self, *args, **options):
        state= options['state'].lower()
        academic_year= options['academic_year']
        
        connection, cursor = self.connectDISE(options["dbname"],options["user"],options["passwd"],options["host"])
        for boundary_type in self.boundaries:
            print(boundary_type)
            q = self.select_queries[boundary_type].replace('replaceyear',academic_year)
            cursor.execute(q,(state,))
            for row in cursor:
                 name = row[0]
                 slug = row[1]
                 if boundary_type == 'district':
                     parent_name = state 
                 else:
                     parent_name = row[2]
                     #newslug = re.split('-',slug)
                     #if len(newslug) > 2:
                        #print("old slug: "+slug+" ,newslug: "+str(newslug))
                        #slug = newslug[1]
                        #for i in range(2,len(newslug)):
                            #slug = slug + "-"+newslug[i]
                 self.insertBoundary(name.lower(),slug,parent_name.lower(), boundary_type)
