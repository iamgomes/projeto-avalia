web: gunicorn avalia.wsgi --log-file -
worker: celery -A avalia worker --concurrency=1 --loglevel=info