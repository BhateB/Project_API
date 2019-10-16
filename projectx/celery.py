"""Celery init."""

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from config.environment import SETTINGS_MODULE

os.environ.setdefault('DJANGO_SETTINGS_MODULE', SETTINGS_MODULE)

app = Celery('projectx')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

if __name__ == '__main__':
    app.start()
