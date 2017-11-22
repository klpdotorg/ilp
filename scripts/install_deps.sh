#!/bin/bash

cd /home/ubuntu/ilp_deploy
/usr/bin/virtualenv --python=python3 ./venv
source venv/bin/activate
pip install -r requirements/base.txt
pip install gunicorn
python manage.py migrate
python manage.py loaddata apps/*/fixtures/*.json
python manage.py collectstatic -c --noinput
