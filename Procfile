web: gunicorn avalia.wsgi --log-file -
worker: celery -A avalia worker --pool=prefork --concurrency=2 --loglevel=info