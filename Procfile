web: gunicorn zntrlhub_backend.wsgi --log-file -
release: sh entrypoint.sh
beat: sh -c "rm -f './celerybeat.pid' && python manage.py setup_periodic_tasks && celery -A zntrlhub_backend beat -l INFO"
worker: celery -A zntrlhub_backend worker -l INFO