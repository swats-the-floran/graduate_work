import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


class TaskQueue(object):
    QUEUE_DEFAULT = 'default'


app.conf.task_default_queue = TaskQueue.QUEUE_DEFAULT
