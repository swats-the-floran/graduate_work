import os

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DB_ENGINE", default="django.db.backends.postgresql"),
        "NAME": os.environ.get("PROFILE_PG_DB"),
        "USER": os.environ.get("PROFILE_PG_USER"),
        "PASSWORD": os.environ.get("PROFILE_PG_PASS"),
        "HOST": os.environ.get("PROFILE_PG_HOST", default="db"),
        "PORT": os.environ.get("PROFILE_PG_PORT", default=5433),
        "OPTIONS": {"options": "-c search_path=public,content"},
    },
}
