#!/bin/sh


python -m spacy download en_core_web_sm

python manage.py runserver 0.0.0.0:8000