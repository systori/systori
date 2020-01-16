#!/bin/bash

cd /app
python manage.py migrate postgres_schema
python manage.py migrate company
python manage.py migrate
python manage.py collectstatic --ignore=*.scss --noinput

# /etc/init.d/celeryd start
# /etc/init.d/celerybeat start

# gunicorn --bind 0.0.0.0:8000 systori.wsgi:application