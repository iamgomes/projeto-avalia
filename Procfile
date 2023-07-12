web: gunicorn avalia.wsgi --log-file -
worker: celery -A avalia.celery worker -l INFO