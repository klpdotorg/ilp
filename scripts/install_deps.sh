#!/bin/bash

/usr/bin/python -m venv venv
source venv/bin/activate
pip install -r requirements/base.txt
python manage.py collectstatic
