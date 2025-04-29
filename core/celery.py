# core/celery.py

import os
from celery import Celery

# Set default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')
app.conf.enable_utc = False

app.conf.update(timezone='Asia/Kolkata')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks from your Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """
    Function to debug celery tasks. Prints out the task information
    """
    print(f'Request: {self.request!r}')