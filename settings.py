# Django settings for apps project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEFAULT_CHARSET = 'utf8'

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
	'ENGINE':'django.db.backends.postgresql_psycopg2',           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
	'NAME':'PruebasCedirFE',             # Or path to database file if using sqlite3.
	'USER':'postgres',             # Not used with sqlite3.
	'PASSWORD':'******',         # Not used with sqlite3.
	'HOST':'localhost',           # Set to empty string for localhost. Not used with sqlite3.
	'PORT':'5432',             # Set to empty string for default. Not used with sqlite3.
    }
}

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

PROJECT_ROOT = u'/home/wbrunetti/Documents/cedir'

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
    u'/usr/local/lib/python2.7/dist-packages/django/contrib/admin/static',
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

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.eggs.Loader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
#   'django.middleware.cache.CacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware', por def esta esta descomentada
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    PROJECT_ROOT + u'/static/templates',
    #"/var/www/django_projects/cedir/admin/templates",
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'contenidos',
    'managers',
    'sala',
    'practica',
    'paciente',
    'obra_social',
    'medico',
    'turno',
    'estudio',
    "comprobante",
)

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

LOG_PATH = '/var/log/www.cedirsalud.com.ar/'

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
