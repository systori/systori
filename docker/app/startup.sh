#!/bin/bash

python3 manage.py migrate postgres_schema
python3 manage.py migrate company
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:8000