web: gunicorn avalia.wsgi --log-file -
celery: celery -A avalia  worker --loglevel=info --concurrency 1