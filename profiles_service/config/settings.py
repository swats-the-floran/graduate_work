import os

from pathlib import Path

from dotenv import load_dotenv
from split_settings.tools import include

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("PROFILE_SERVICE_SECRET")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG")

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost").split(",")


# Application definition
include("components/apps_settings.py")

include("components/middlewares.py")

# Database
include("components/db.py")

# Password validation
include("components/auth.py")


# Internationalization
include("components/internationalization.py")


# Static files (CSS, JavaScript, Images)
include("components/static.py")

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOCALE_PATHS = ["movies/locale"]
