#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py migrate app --noinput || true
python manage.py migrate admin --noinput || true
python manage.py migrate sessions --noinput || true
python manage.py migrate django_celery_results --noinput || true
python manage.py migrate django_celery_beat --noinput || true

exec "$@"