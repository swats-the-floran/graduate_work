#!/usr/bin/env bash

set -e

python manage.py makemessages --locale=en
python manage.py compilemessages -l en -l ru

python manage.py makemigrations
python manage.py migrate

python manage.py collectstatic --no-input

uwsgi --strict --ini /opt/app/uwsgi.ini
