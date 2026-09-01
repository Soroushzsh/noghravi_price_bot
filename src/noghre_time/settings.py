import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def _load_local_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        key, separator, value = line.strip().partition("=")
        if separator and key and not key.startswith("#"):
            os.environ.setdefault(key, value)


_load_local_env(BASE_DIR / ".env.django")
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "development-only-change-me")
DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"
if not DEBUG and SECRET_KEY in {"development-only-change-me", "replace-with-a-long-random-secret"}:
    raise ImproperlyConfigured("Set DJANGO_SECRET_KEY to a long random value in production")
ALLOWED_HOSTS = [host.strip() for host in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if host.strip()]
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if origin.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "website",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "noghre_time.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {
        "context_processors": [
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
            "website.context_processors.site_context",
        ],
    },
}]
WSGI_APPLICATION = "noghre_time.wsgi.application"
ASGI_APPLICATION = "noghre_time.asgi.application"

DATABASE_PATH = os.getenv("DATABASE_PATH", "/data/silver_price_bot.db")
if not Path(DATABASE_PATH).is_absolute():
    Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": DATABASE_PATH, "OPTIONS": {"timeout": 20}, "TEST": {"NAME": os.getenv("DJANGO_TEST_DB", "/tmp/noghre-time-test.sqlite3")}}}

LANGUAGE_CODE = "fa"
TIME_ZONE = os.getenv("DISPLAY_TIMEZONE", "Asia/Tehran")
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "/admin/login/"
SITE_URL = os.getenv("SITE_URL", "http://localhost:8000").rstrip("/")
BALE_CHANNEL_URL = os.getenv("BALE_CHANNEL_URL", "")
STALE_AFTER_SECONDS = int(os.getenv("STALE_AFTER_SECONDS", "1800"))
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
