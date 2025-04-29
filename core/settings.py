from pathlib import Path
from django.conf import settings
from django.contrib.messages import constants as messages
import os, boto3
from decouple import config
from django.core.files.storage import default_storage  # Force creation
from storages.backends.s3boto3 import S3Boto3Storage
from concurrent.futures import ThreadPoolExecutor
# from datetime import timedelta

# Create a global thread pool with a specified number of workers
THREAD_POOL_EXECUTOR = ThreadPoolExecutor(max_workers=3)

# Alerts
MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'primary',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger'
}

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)
PRODUCTION = True # Set to True for production
DEVELOPMENT = not PRODUCTION

if PRODUCTION:
    DEBUG = True
    ALLOWED_HOSTS = ["mission247.org","www.mission247.org","eventic.in"]  # Replace with your domain and load balancer DNS
    STATIC_ROOT = os.path.join(BASE_DIR, 'collected_static')  # Ensure static files are served
    # SECURE_SSL_REDIRECT = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Database (RDS PostgreSQL)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USERNAME'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST'),  # RDS endpoint
            'PORT': config('DB_PORT', default='5432'),
        }
    }
else:
    ALLOWED_HOSTS = ["*"]
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'WebApp',
            'USER': 'postgres',
            'PASSWORD': 'root',
            'HOST': 'db',  # Use the service name defined in docker-compose.yml
            'PORT': '5432',
        }
    }

SITE_ID = 1

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'django.contrib.sites',  # Required for django-allauth
    'whitenoise.runserver_nostatic', #Make sure to add this 
    # Apps
    'api.apps.ApiConfig',
    'authenticator.apps.AuthenticatorConfig',
    'dashboard.apps.DashboardConfig',
    'docs.apps.DocsConfig',
    'blog.apps.BlogConfig',
    'main.apps.MainConfig',
    'payment.apps.PaymentConfig',
    'user.apps.UserConfig',
    'vendor.apps.VendorConfig',
    'search.apps.SearchConfig',
    # Services
    'photographer.apps.PhotographerConfig',
    'videographer.apps.VideographerConfig',
    'invitation.apps.InvitationConfig',
    # 'credit.apps.CreditConfig',
    # Third Party Apps
    'django_user_agents', # For user agent tracking
    'rest_framework', # For API
    # 'rest_framework_simplejwt',  # For authentication
    # 'rest_framework_simplejwt.token_blacklist', # For logout
    'corsheaders', # For Cross Origin Resource Sharing
    # 'django_celery_results',
    # 'django_celery_beat',
    'storages', # S3 Storage
    # For social media login
    'allauth',
    'allauth.account', 
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google', 
    # Debug
    # 'debug_toolbar', #Development
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', #make sure to add this line
    # 'debug_toolbar.middleware.DebugToolbarMiddleware', #Development
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware", # For social media login
    # custom middleware
    # 'core.middleware.cached_user_data.CachedUserDataMiddleware', # For caching user data
    'django_user_agents.middleware.UserAgentMiddleware', # For user agent
]

# MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

ROOT_URLCONF = 'core.urls'

# USER_AGENTS_CACHE = 'default'  # Add caching if needed

ORIGINS = [
    'https://eventic.in',
    'https://mission247.org'
]

if DEVELOPMENT:
    ORIGINS.append('http://localhost:3000')
    ORIGINS.append('http://127.0.0.1:3000')
    ORIGINS.append('http://localhost:8000')
    ORIGINS.append('http://127.0.0.1:8000')
    


CORS_ALLOW_ALL_ORIGINS = False 
CORS_ALLOW_CREDENTIALS = True 
CORS_ALLOW_METHODS = ('GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS')
CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOWED_ORIGINS = ORIGINS
CORS_ALLOWED_ORIGIN_REGEXES = ORIGINS

CSRF_COOKIE_SAMESITE = 'Lax'  # or 'Strict'
CSRF_COOKIE_SECURE = True     # Set to True if using HTTPS
CSRF_USE_SESSIONS = False
CSRF_TRUSTED_ORIGINS = ORIGINS
CSRF_COOKIE_HTTPONLY = False # Must be False to allow JavaScript to read it 

SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = True

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# SECURE_SSL_REDIRECT = True #Production
# SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin' #Production
# SECURE_CROSS_ORIGIN_EMBEDDER_POLICY = 'require-corp' #Production

# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': (
#         'rest_framework_simplejwt.authentication.JWTAuthentication',
#     ),
#     'DEFAULT_PERMISSION_CLASSES': (
#         'rest_framework.permissions.IsAuthenticated',
#     ),
# }

# SIMPLE_JWT = {
#     'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),  # Set the token lifetime
#     'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
#     'ROTATE_REFRESH_TOKENS': True,
#     'BLACKLIST_AFTER_ROTATION': True,
# }

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # 'django.template.context_processors.debug', #Testing purposes
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.global_settings',  # For google analytics
            ],
            'libraries':{
                'auth_extras': 'core.templatetags.auth_extras',
            },
            'autoescape': 'xhtml_br',  # Set autoescape to 'xhtml_br'
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# if DEVELOPMENT:
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.postgresql',
#             'NAME': 'WebApp',
#             'USER': 'postgres',
#             'PASSWORD': 'root',
#             'HOST': 'db',  # Use the service name defined in docker-compose.yml
#             'PORT': '5432',
#         }
#     }
# else:
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.postgresql_psycopg2',
#             'NAME': config('DB_NAME'),
#             'USER': config('DB_USERNAME'),
#             'PASSWORD': config('DB_PASSWORD'),
#             'HOST': config('DB_HOST'),
#             'PORT': config('DB_PORT'),
#         }
#     }


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    # 'allauth.account.auth_backends.AuthenticationBackend', # `allauth` specific authentication methods, such as login by email
    # 'authenticator.backends.EmailOrUsernameModelBackend',  # Custom backend
]

# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': config('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY'),
            'secret': config('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET'),
            'key': '',
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True
    },
}

FERNET_KEY = b'-n6csdBeU6keZhXAYLHoh9sG_Drv3bwAEQOwIvck4no='

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' 
SERVER_EMAIL = 'company@eventic.in'
DEFAULT_FROM_EMAIL_NAME = 'Eventic'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('COMPANY_EMAIL_HOST_USER')  # Replace with your email
EMAIL_HOST_PASSWORD = config('COMPANY_EMAIL_HOST_PASSWORD')  # Replace with your email password
DEFAULT_FROM_EMAIL = 'Eventic <company@eventic.in>'
EMAIL_TIMEOUT = 5 # Set the timeout to 5 seconds

EMAIL_BACKENDS = {
    'default': {
        'host': 'smtp.gmail.com',
        'post': 587,
        'username': config('COMPANY_EMAIL_HOST_USER'),
        'password': config('COMPANY_EMAIL_HOST_PASSWORD'),
        'use_tls': True,
        'default_from_email_name': 'Eventic'
    },
    'contact': {
        'host': 'smtp.gmail.com',
        'post': 587,
        'username': config('CONTACT_EMAIL_HOST_USER'),
        'password': config('CONTACT_EMAIL_HOST_PASSWORD'),
        'use_tls': True,
        'default_from_email_name': 'Contact - Eventic'
    },
    'info': {
        'host': 'smtp.gmail.com',
        'post': 587,
        'username': config('INFO_EMAIL_HOST_USER'),
        'password': config('INFO_EMAIL_HOST_PASSWORD'),
        'use_tls': True,
        'default_from_email_name': 'Info - Eventic'
    }
}

# Allauth Settings
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'  # Options: 'mandatory', 'optional', 'none'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'  # Allow login with email or username
ACCOUNT_CONFIRM_EMAIL_ON_GET = True  # Automatically confirm email when link is clicked
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3  # Expiry time for confirmation links

ACCOUNT_EMAIL_SUBJECT_PREFIX = "Eventic - "
ACCOUNT_FORMS = {
    'reset_password': 'authenticator.forms.CustomResetPasswordForm',
}

CONTACT_PHONE = config('PHONE_NUMBER')
CONTACT_EMAIL = 'contact@eventic.in'

LOGIN_URL = 'auth:login'
LOGOUT_URL = 'auth:logout' 
LOGIN_REDIRECT_URL = 'auth:auth_redirect_view'  # Redirect after login
LOGOUT_REDIRECT_URL = 'auth:login'  # Redirect after logout
ACCOUNT_LOGOUT_REDIRECT_URL = "auth:auth_redirect_view"
ACCOUNT_SIGNUP_REDIRECT_URL = "auth:auth_redirect_view"  # or any custom redirect URL after signup
ACCOUNT_LOGIN_REDIRECT_URL = "auth:auth_redirect_view"  # or any custom redirect URL after login    
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '/'  # For unauthenticated users
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = 'auth:auth_redirect_view'  # For authenticated users

# Celery settings
# CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Use Redis as the broker
# CELERY_ACCEPT_CONTENT = ['application/json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'

# Celery beat settings
# CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler' # Use the database scheduler for periodic tasks

# Celery time zone
# CELERY_TIMEZONE = 'Asia/Kolkata'

# Celery result backend
# CELERY_RESULT_BACKEND = 'django-db'


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

USE_I18N = True

USE_L10N = True

USE_TZ = True

TIME_ZONE = 'Asia/Kolkata'


# Custom Settings
GOOGLE_ANALYTICS = True if PRODUCTION else False
GOOGLE_OAUTH = False if PRODUCTION else True
IN_DEVELOPMENT = DEVELOPMENT

# Set max upload size
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800 #50 MB

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/


# S3 Static and Media Settings
# Media files settings

if DEVELOPMENT: 
    STATIC_URL = '/static/'  # URL to access static files
    MEDIA_URL = '/media/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'collected_static')  # Add this line
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]  # Optional for additional static files
else:  
    # AWS S3 Storage
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY') 
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')  # Set your bucket name
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME')  # Set your region name
    AWS_QUERYSTRING_AUTH = False  # This will make the URLs publicly accessible
    AWS_S3_VERIFY = True

    # Optionally, set custom domain for S3 bucket
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

    AWS_S3_SIGNATURE_NAME = 's3v4'  # Set to 's3v4' if you want to use S3 v4
    AWS_S3_FILE_OVERWRITE = False  # Set to 'True' if you want to overwrite files
    AWS_DEFAULT_ACL = None  # Set to 'public-read' if you want files to be publicly accessible
    AWS_PRELOAD_METADATA = False

    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',  # Set caching to 1 day (in seconds)
    }
    
    STORAGES = {
        "default": {
            "BACKEND": "core.storages.MediaStorage",
        },
        "staticfiles": {
            "BACKEND": "core.storages.StaticStorage",
        },
    }
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'  # S3 media URL
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'  # S3 static URL


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

if DEVELOPMENT:
    INTERNAL_IPS = ['127.0.0.1']

# Razorpay Payment Gateway
RAZORPAY_KEY_ID = config('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = config('RAZORPAY_KEY_SECRET')

GEOIP_PATH = os.path.join(BASE_DIR, "GeoIP")

# Social media feeds
INSTAGRAM = config('INSTAGRAM')
FACEBOOK = config('FACEBOOK')
TWITTER = config('TWITTER')
YOUTUBE = config('YOUTUBE')
LINKEDIN = config('LINKEDIN')
WHATSAPP = config('WHATSAPP')


# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'verbose': {
#             'format': '{levelname} {asctime} {module} {message}',
#             'style': '{',
#         },
#     },
#     'handlers': {
#         'file': {
#             'level': 'ERROR',
#             'class': 'logging.FileHandler',
#             'filename': os.path.join(BASE_DIR, 'error.log'),  # Log errors to a file
#             'formatter': 'verbose',
#         },
#         'database': {
#             'level': 'ERROR',
#             'class': 'yourapp.logging.DatabaseLogHandler',  # Custom handler for database logging
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['file', 'database'],
#             'level': 'ERROR',
#             'propagate': True,
#         },
#     },
# }


