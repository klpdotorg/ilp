#!/bin/bash
# enabling debug mode
set -x
whoami
ls -la 
WORK_DIR=/home/ubuntu/ilp
cd $WORK_DIR
whoami
ls -la 
source venv/bin/activate || exit 1
whoami
ls -la 
pip3 install -r requirements/base.txt --exists-action w || exit 1
pip3 install gunicorn || exit 1
cp -fv /home/ubuntu/prod_settings.py ${WORK_DIR}/ilp/settings/
python3 manage.py migrate || exit 1
python3 manage.py loaddata apps/*/fixtures/*.json || exit 1
python3 manage.py collectstatic -c --noinput || exit 1
