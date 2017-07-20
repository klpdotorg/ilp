### Pre-requisites

This script assumes that the dubdubdub DB is present. Please see dubdubdub setup instructions as to how to create DB from a dump. Latest dubdubdub dumps are available on klp.org.in /home/vamsee/backups/. The script also assumes that the new unified DB is created. Pull latest code from 'master'. Please run:

    python manage.py migrate
    python manage.py loaddata apps/*/fixtures/*.json

before running this script.

Also KLP user is assumed for postgres.

### To run:

Run:
    
    chmod 777 *.sh
    ./populateBoundaryTables.sh <dubdubdub dbname> <electedrep dbname> <ilp db name> <temp dir to store files>

Example: ./populateBoundaryTables.sh dubdubdub electrep_new ilp /Users/johndoe/csvs

Then run:

./updatediseslugs.sh <ilp db name>

This script will update all the dise slugs.
