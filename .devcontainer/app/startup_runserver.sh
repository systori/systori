#!/bin/bash

python manage.py migrate postgres_schema
python manage.py migrate company
python manage.py migrate
python manage.py collectstatic --ignore=*.scss --noinput
python manage.py runserver 0.0.0.0:8000