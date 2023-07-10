web: gunicorn avalia.wsgi --log-file -
celery: celery -A avalia  worker --pool=solo -l info --concurrency 1