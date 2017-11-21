#!/bin/bash

cd /home/ubuntu/ilp
/usr/bin/python -m virtualenv venv
source venv/bin/activate
pip install -r requirements/base.txt
python manage.py collectstatic -c --noinput
