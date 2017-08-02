from django.core.management.base import BaseCommand, CommandError
from django.db import models
from django.core.management import call_command
from django.db import connection, transaction

class Command(BaseCommand):
    def handle(self, *args, **options):
            try:
                # rename table, then recreate
                cursor = connection.cursor()
                sql = 'DROP MATERIALIZED VIEW IF EXISTS mvw_boundary_hierarchy CASCADE'
                cursor.execute(sql)
                print sql
                
                cursor = connection.cursor()
                
             
                # insert data from temp table into new
                sql = 'CREATE materialized VIEW mvw_boundary_hierarchy AS \
                SELECT b3.id AS admin3_id, \
                    b3.name as admin3_name,\
                    b2.id AS admin2_id,\
                    b2.name AS admin2_name,\
                    b1.id AS admin1_id,\
                    b1.name AS admin1_name,\
                    b0.id AS admin0_id,\
                    b0.name AS admin0_name,\
                    b1.type_id AS type_id\
                FROM boundary_boundary b1,\
                    boundary_boundary b2,\
                    boundary_boundary b3,\
                    boundary_boundary b0\
                WHERE b3.parent_id = b2.id\
                    AND b2.parent_id = b1.id\
                    AND b1.parent_id = b0.id\
                    AND b0.parent_id=1'
                cursor.execute(sql)
                print sql  
            except Exception, e:
                print 'Last SQL statement: ' + sql
                transaction.rollback_unless_managed()
                raise
            else:
                transaction.commit_unless_managed()