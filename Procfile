web: gunicorn avalia.wsgi --log-file -
worker: celery -A avalia worker --pool=solo --concurrency=2 --loglevel=info