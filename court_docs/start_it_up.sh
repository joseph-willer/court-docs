#!/bin/sh



echo "is this thing on"

python -m spacy download en_core_web_sm

python manage.py makemigrations
python manage.py migrate

python manage.py runserver 0.0.0.0:8000