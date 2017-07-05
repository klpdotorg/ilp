###Prerequisites:

This script assumes that the dubdubdub DB is present and loaded as well as the new unified DB is created. Please run:

python manage.py migrate
python manage.py loaddata apps/*/fixtures/*.json

before running this script.

Also KLP user is assumed for postgres.

###To run:

TEMP BUG: Open scripts/boundary/sql/exportBoundaryData.sql and importBoundaryTable.sql. At the end of the copy command, please fill out an appropriate file path for your machine. Trying to fix bug with passing file paths to psql from shell scripts. Till then, this workaround has to be done before running scripts.

Run ./populateBoundaryTables.sh <dubdubdub dbname> <ilp db name>

Example: ./populateBoundaryTables.sh dubdubdub ilp

Then run:

./updatediseslugs.sh <ilp db name>

This script will update all the dise slugs.
