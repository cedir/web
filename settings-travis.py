# Django settings for apps project.

import os, sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ULI_URL = 'https://localhost:3000'

# Afip
AFIP_WSDL_URL = "https://wswhomo.afip.gov.ar/wsfev1/service.asmx?WSDL"
AFIP_WSAA_URL = "https://wsaahomo.afip.gov.ar/ws/services/LoginCms?wsdl"
CEDIR_CERT_PATH = "certificados/cedir_homologacion.crt"
CEDIR_PV_PATH = "certificados/cedir_homologacion.csr"
CEDIR_CUIT = "30709300152"
CEDIR_PTO_VENTA = 91
BRUNETTI_CERT_PATH = "certificados/brunetti_homologacion.crt"
BRUNETTI_PV_PATH = "certificados/brunetti_homologacion.csr"
BRUNETTI_CUIT = "20118070659"
BRUNETTI_PTO_VENTA = 6
CACHE_PATH = "comprobante/cache/tickets/"

DEBUG = True
DEFAULT_CHARSET = 'utf8'

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

LOGIN_URL = '/usuario/entrar/'

DATABASES = {
    'default': {
        'ENGINE':'django.db.backends.postgresql_psycopg2',           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME':'test_db',             # Or path to database file if using sqlite3.
        'USER':'postgres',             # Not used with sqlite3.
        'PASSWORD':'',         # Not used with sqlite3.
        'HOST':'',           # Set to empty string for localhost. Not used with sqlite3.
        'PORT':'5432',             # Set to empty string for default. Not used with sqlite3.
    }
}
if 'test' in sys.argv or 'test_coverage' in sys.argv:  # Covers regular testing and django-coverage
    DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'

FIXTURE_DIRS = (
    os.path.join(os.getcwd(), "fixtures"),
)

print(PROJECT_ROOT)
print(FIXTURE_DIRS)

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be avilable on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Argentina/Buenos_Aires'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
#USE_TZ = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = PROJECT_ROOT + u'/static/templates/media_files/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/media_files/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
#ADMIN_MEDIA_PREFIX = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = "/media/"

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    PROJECT_ROOT + u'/static/templates',
    #Alias /css /var/www/cedir/static/templates/css
    PROJECT_ROOT + u'/static', # media_files
    #Alias /images /var/www/cedir/static/templates/images
    #Alias /js /var/www/cedir/static/templates/js
    #Alias /flash /var/www/cedir/static/templates/flash
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'c3*36km04w7um-xb#+h13plm7=uc5#k5$kw@dc)f9%&hm&1kn2'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_URLS_REGEX = r'^/api/.*$'
CORS_ALLOW_CREDENTIALS = True

# You'll probably want to vary this depending on environment.
CORS_ORIGIN_WHITELIST = ('localhost:3000')


ROOT_URLCONF = 'urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wsgi.application'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.getcwd() + u'/static/templates', ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            #'loaders': [
            #    'django.template.loaders.eggs.Loader',
            #    'django.template.loaders.filesystem.Loader',
            #    'django.template.loaders.app_directories.Loader',
            #]
        },
    },
]

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'common',
    'security',
    'contenidos',
    'sala',
    'practica',
    'paciente',
    'obra_social',
    'medico',
    'caja',
    'anestesista',
    'turno',
    'estudio',
    'comprobante',
    'medicamento',
    'presentacion',
]


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        #'security.permissions.IsAuthenticatedOrOptions',    # uncomment to allow OPTIONS requests without being logged
    ),
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',)
    #'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    #'PAGE_SIZE': 100
}


FORMAT_DATETIME = u'%d/%m/%Y %H:%M:%S'
FORMAT_TIME = u'%H:%M:%S',
FORMAT_DATE = u'%d/%m/%Y'

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

LOG_PATH = 'logs/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'logging': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOG_PATH + 'debug.log',
        },
        'videos_file': {
            'level': 'INFO',
            'class': 'cloghandler.ConcurrentRotatingFileHandler',
            'maxBytes': 1024*1024*10,  # 10 MB
            'backupCount': 5,
            'formatter': 'logging',
            'filename':  LOG_PATH + 'videos.log'
        }
    },
    'loggers': {
        'videos': {
            'handlers': ['videos_file', 'console'],
            'level': 'INFO'
        }
    }
}

EMAIL_NOTIFICATION_ACCOUNTS = [u'email@address.com']

CAPTCHA_PUBLIC = '6LckIhUUAAAAAAsZYnp18fbeUoOPy6X5NOKFAVzf'
CAPTCHA_SECRET = ''
