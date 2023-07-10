web: gunicorn avalia.wsgi --log-file -
celery: celery -A avalia  worker -l INFO --concurrency 1