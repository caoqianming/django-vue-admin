#!/bin/bash
if [ v"$DJANGO_ENV" == 'vdev' ]; then
    python manage.py makemigrations system  
    python manage.py migrate
    python manage.py runserver 80
    else
    python manage.py migrate
    python manage.py collectstatic --noinput
    gunicorn server.wsgi:application -w 4 -k gthread -b 0.0.0.0:80
fi
