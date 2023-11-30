import os
from .settings import BASE_DIR

STATIC_URL = 'static/'
MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')