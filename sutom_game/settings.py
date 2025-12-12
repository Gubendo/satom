# settings.py - production-ready version

from pathlib import Path
import os
import dj_database_url
import environ

env = environ.Env()
environ.Env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent

# ENV mode
ENV = env("ENV", default="local")
DEBUG = env.bool("DEBUG", default=False)

# Secret key
SECRET_KEY = env("DJANGO_SECRET_KEY", default="super-secret-key")

# Allowed hosts
# Récupère la variable d'env séparée par des virgules, ou fallback à hosts connus
allowed_hosts_env = env("DJANGO_ALLOWED_HOSTS", default="")
ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_env.split(",") if h.strip()]
ALLOWED_HOSTS += [
    "127.0.0.1",
    "localhost",
    "satom-production.up.railway.app",
]

# Database
if ENV == "production":
    DATABASES = {
        "default": dj_database_url.config(
            default=os.environ.get("DATABASE_URL"),
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

if ENV == "production":
    CSRF_TRUSTED_ORIGINS = [
        "https://satom-production.up.railway.app",
    ]
else:
    CSRF_TRUSTED_ORIGINS = []
    
# Apps
INSTALLED_APPS = [
    'users',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'hello_world',
    'satom',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sutom_game.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "sutom_game/templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sutom_game.wsgi.application'

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Auth
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'dashboard'

# Misc
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SESSION_SAVE_EVERY_REQUEST = True
