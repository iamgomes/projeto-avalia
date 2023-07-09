import os
from celery import Celery

# Configuração para usar as configurações do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avalia.settings')

app = Celery('avalia')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')