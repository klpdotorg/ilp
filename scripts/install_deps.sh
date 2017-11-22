#!/bin/bash

cd /home/ubuntu/ilp
/usr/bin/virtualenv --python=python3 venv
source venv/bin/activate
pip install -r requirements/base.txt
python manage.py collectstatic -c --noinput
