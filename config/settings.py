from pathlib import Path
import base64
import os
import sys
import tempfile
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-change-this-secret-key-before-deployment")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
# Use ordinary static-file storage for local runs and Django tests.
# Production uses WhiteNoise manifest storage after collectstatic.
IS_TESTING = any(arg in {"test", "pytest"} for arg in sys.argv)

_allowed_hosts = [host.strip() for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if host.strip()]
# Vercel provides deployment hostnames without a scheme.
for deployment_host in (os.environ.get("VERCEL_URL", ""), os.environ.get("VERCEL_PROJECT_PRODUCTION_URL", "")):
    deployment_host = deployment_host.strip()
    if deployment_host and deployment_host not in _allowed_hosts:
        _allowed_hosts.append(deployment_host)
ALLOWED_HOSTS = _allowed_hosts
if not DEBUG and SECRET_KEY == "dev-only-change-this-secret-key-before-deployment":
    raise ImproperlyConfigured("Set DJANGO_SECRET_KEY to a strong random value before production deployment.")

CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if origin.strip()]
for deployment_host in (os.environ.get("VERCEL_URL", ""), os.environ.get("VERCEL_PROJECT_PRODUCTION_URL", "")):
    deployment_host = deployment_host.strip()
    if deployment_host:
        deployment_origin = f"https://{deployment_host}"
        if deployment_origin not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(deployment_origin)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "portal.apps.PortalConfig",
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
ROOT_URLCONF = "config.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.debug",
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

if os.environ.get("DB_ENGINE", "sqlite").lower() == "mysql":
    db_host = os.environ.get("DB_HOST") or os.environ.get("MYSQLHOST", "127.0.0.1")
    mysql_options = {"charset": "utf8mb4", "connect_timeout": 10}

    # Aiven supplies a private CA certificate. Vercel environment variables
    # cannot provide a file directly, so decode DB_SSL_CA_B64 into /tmp,
    # which is writable by Vercel Functions.
    ssl_ca_b64 = "".join(os.environ.get("DB_SSL_CA_B64", "").split())
    ssl_ca_path = os.environ.get("DB_SSL_CA", "").strip()
    if ssl_ca_b64:
        try:
            ca_bytes = base64.b64decode(ssl_ca_b64, validate=True)
        except (ValueError, base64.binascii.Error) as exc:
            raise ImproperlyConfigured("DB_SSL_CA_B64 must contain a valid Base64-encoded PEM CA certificate.") from exc
        if b"-----BEGIN CERTIFICATE-----" not in ca_bytes:
            raise ImproperlyConfigured("DB_SSL_CA_B64 does not appear to contain a PEM certificate.")
        ca_file = Path(tempfile.gettempdir()) / "placementpilot-aiven-ca.pem"
        temp_ca_file = ca_file.with_suffix(".tmp")
        temp_ca_file.write_bytes(ca_bytes)
        temp_ca_file.replace(ca_file)
        try:
            os.chmod(ca_file, 0o600)
        except OSError:
            pass
        ssl_ca_path = str(ca_file)

    if ssl_ca_path:
        mysql_options.update({"ssl_ca": ssl_ca_path, "ssl_verify_cert": True, "ssl_verify_identity": True})
    elif db_host.endswith(".aivencloud.com"):
        raise ImproperlyConfigured("Aiven MySQL requires DB_SSL_CA_B64 (Base64-encoded CA certificate) or DB_SSL_CA (certificate file path).")

    # Short-lived serverless invocations should not retain many idle DB sessions.
    default_conn_age = "0" if os.environ.get("VERCEL") == "1" else "60"
    DATABASES = {"default": {
        "ENGINE": "django.db.backends.mysql",
       "NAME": (os.environ.get("DB_NAME") or os.environ.get("MYSQLDATABASE", "placementpilot")).strip(),
        "USER": os.environ.get("DB_USER") or os.environ.get("MYSQLUSER", "root"),
        "PASSWORD": os.environ.get("DB_PASSWORD") or os.environ.get("MYSQLPASSWORD", ""),
        "HOST": db_host,
        "PORT": os.environ.get("DB_PORT") or os.environ.get("MYSQLPORT", "3306"),
        "OPTIONS": mysql_options,
        "CONN_MAX_AGE": int(os.environ.get("DB_CONN_MAX_AGE", default_conn_age)),
    }}
else:
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG or IS_TESTING
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        )
    },
}
MEDIA_URL = "/media/"
MEDIA_ROOT = Path(os.environ.get("MEDIA_ROOT", str(BASE_DIR / "media")))
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "home"
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 6 * 1024 * 1024

# Vercel terminates HTTPS at its edge; trust the forwarded scheme in production.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
