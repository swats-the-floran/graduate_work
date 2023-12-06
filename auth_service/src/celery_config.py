from celery import Celery
from core.config import settings


app = Celery('celery', include=['core.tasks'])
app.conf.broker_url = settings.redis_db.url
app.conf.result_backend = settings.redis_db.url