#!/bin/bash
WORK_DIR=/home/ubuntu/ilp
cd $WORK_DIR
source venv/bin/activate || exit 1
pip3 install -r requirements/base.txt --exists-action w || exit 1
pip3 install gunicorn || exit 1
cp -fv /home/ubuntu/prod_settings.py ${WORK_DIR}/ilp/settings/
python3 manage.py migrate || exit 1
python3 manage.py loaddata apps/*/fixtures/*.json || exit 1
python3 manage.py collectstatic -c --noinput || exit 1
npm install -g newman
./runreadonlytests.sh environments/development_env.json
