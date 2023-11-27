import os

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DB_ENGINE", default="django.db.backends.postgresql"),
        "NAME": os.environ.get("POSTGRES_DB"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST", default="db"),
        "PORT": os.environ.get("POSTGRES_PORT", default=5432),
        "OPTIONS": {"options": "-c search_path=public,content"},
    },
}
