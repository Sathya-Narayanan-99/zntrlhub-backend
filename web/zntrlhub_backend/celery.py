import os
from django.conf import settings
from celery import Celery
  
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zntrlhub_backend.settings')
  
app = Celery('zntrlhub_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
  
# Load task modules from all registered Django app configs.
app.autodiscover_tasks(settings.INSTALLED_APPS)
