import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

# Tasks live in app/celery/tasks.py, which autodiscover_tasks() wouldn't find (it only looks at <installed_app>.tasks)
app = Celery('app', include=['app.celery.tasks'])
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
