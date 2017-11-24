#!/bin/bash

cd /home/ubuntu/ilp_deploy
source venv/bin/activate || exit 1
pip3 install -r requirements/base.txt || exit 1
pip3 install gunicorn || exit 1
python3 manage.py migrate
python3 manage.py loaddata apps/*/fixtures/*.json
python3 manage.py collectstatic -c --noinput
