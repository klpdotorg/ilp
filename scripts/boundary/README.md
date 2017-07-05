Prerequisites:

This script assumes that the dubdubdub DB is present and loaded as well as the new unified DB is created. Please run:

python manage.py migrate
python manage.py loaddata ....

before running this script.

Also KLP user is assumed for postgres.

To run:

Run ./populateBoundaryTables.sh <dubdubdub dbname> <ilp db name>

Example: ./populateBoundaryTables.sh dubdubdub ilp

Then run:

./updatediseslugs.sh <ilp db name>

This script will update all the dise slugs.
