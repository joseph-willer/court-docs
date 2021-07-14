#!/bin/sh



echo "is this thing on"

python -m spacy download en_core_web_md

echo "loaded en_core_web_md"

python manage.py makemigrations
python manage.py migrate

python manage.py runserver 0.0.0.0:8000