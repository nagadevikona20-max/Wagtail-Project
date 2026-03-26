import os
from .base import *

DEBUG = False

# Secret key from environment variable (required in production)
SECRET_KEY = os.environ.get('SECRET_KEY', 'changeme-set-a-real-secret-key-in-render-env')

# Allowed hosts - allow all Render domains by default
_allowed = os.environ.get('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [h.strip() for h in _allowed.split(',') if h.strip()] if _allowed else ['*']

# Trust Render's HTTPS proxy for CSRF
CSRF_TRUSTED_ORIGINS = ['https://*.onrender.com'] + [
    f"https://{h}" for h in ALLOWED_HOSTS if h != '*'
]

# Whitenoise for compressed, cached static files
STORAGES["staticfiles"]["BACKEND"] = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Tell Django it's behind an HTTPS proxy (Render's load balancer)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

try:
    from .local import *
except ImportError:
    pass
