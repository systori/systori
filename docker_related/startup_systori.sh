#!/bin/bash


# pipenv install --dev
# echo "pipenv install done."
pipenv run python manage.py runserver 0.0.0.0:8000
echo "exit"