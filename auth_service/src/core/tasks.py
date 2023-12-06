import requests

from celery_config import app
from core.config import settings

@app.task(queue='profile_queue', autoretry_for=(Exception,), retry_backoff=True)
def register_new_profile(data):
    url = f'{settings.profile.url}/api/v1/users/'
    print(url)
    response = requests.post(url, json=data)
    response.raise_for_status()
