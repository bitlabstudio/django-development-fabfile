"""Settings that need to be set in order to run the tests."""
import os

from fabric.api import env


DEBUG = True

SITE_ID = 1

APP_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..'))


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(APP_ROOT, '../app_static')
MEDIA_ROOT = os.path.join(APP_ROOT, '../app_media')
STATICFILES_DIRS = (
    os.path.join(APP_ROOT, 'static'),
)

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'APP_DIRS': True,
    'DIRS': [os.path.join(APP_ROOT, 'tests/test_app/templates')],
    'OPTIONS': {
        'context_processors': (
            'django.contrib.auth.context_processors.auth',
            'django.template.context_processors.request',
        )
    }
}]

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

EXTERNAL_APPS = [
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.sites',
]

INTERNAL_APPS = [
    'development_fabfile',
]

INSTALLED_APPS = EXTERNAL_APPS + INTERNAL_APPS

SECRET_KEY = 'foobar'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite',
    }
}

# FABFILE SETTINGS

# ============================================================================
# General settings
# ============================================================================

# This should be the folder name of your Django project
PROJECT_NAME = 'projectname'

# Path to your test_settings.py
TEST_SETTINGS_PATH = 'myproject.settings.test_settings'

# This should be the name of the virtualenv on your local machine and on your
# servers
VENV_NAME = PROJECT_NAME

DB_DUMP_FILENAME = '{0}.dump'.format(PROJECT_NAME)
MEDIA_DUMP_FILENAME = '{0}_media.tar.gz'.format(PROJECT_NAME)

# Set this to true if you want to execute makemessages during a deployment
MAKEMESSAGES_ON_DEPLOYMENT = False

# Set this to true if you want to execute compilemessages during a deployment
COMPILEMESSAGES_ON_DEPLOYMENT = False

# Add other code snippets you want to be found. Add a file type to the dict and
# define a regex, which should be processed
SYNTAX_CHECK = {
    '*.js': '(console.log|alert)',
}
# Add files or directories to exclude in the syntax check
SYNTAX_CHECK_EXCLUDES = [
    './submodules',
    'static/js/libs/',
    'node_modules',
]

JSHINT_CHECK_EXCLUDES = SYNTAX_CHECK_EXCLUDES

# Those files/dirs will be excluded in the coverage report
COVERAGE_EXCLUDES = (
    '*__init__*,*manage.py,*wsgi*,*urls*,*/settings/*,*/migrations/*,'
    '*/tests/*,*admin*,*/south_migrations/*')


# ============================================================================
# Local settings
# ============================================================================

# This should be the superuser of your postgres installation. Usually this is
# either postgres or your login username.
LOCAL_PG_ADMIN_ROLE = 'postgres'
LOCAL_PG_USE_LOCALHOST = True
LOCAL_COVERAGE_PATH = os.path.join(os.path.dirname(__file__), '../../coverage')

# ============================================================================
# Server settings
# ============================================================================

# This should be the name of your user that has sudo access on the server
LOGIN_USER_PROD = PROJECT_NAME
HOST_PROD = 'DOMAIN OR IP HERE'

RSYNC_EXCLUDES = [
    'local_settings.py',
    'circus.ini',
]


# These are some paths that, by convention, you set on your servers.
# You should keep them identical for all tiers (dev, stage, prod).
def get_fab_setting(setting_name):
    if setting_name == 'SERVER_REPO_ROOT':
        return '/home/{0}/src/{1}/'.format(env.user, PROJECT_NAME)

    if setting_name == 'SERVER_REPO_PROJECT_ROOT':
        # This must have trailing slash because of rsync
        return '{0}{1}/'.format(
            get_fab_setting('SERVER_REPO_ROOT'), PROJECT_NAME)

    if setting_name == 'SERVER_APP_ROOT':
        return '/home/{0}/project/'.format(env.user)

    if setting_name == 'SERVER_PROJECT_ROOT':
        return '/home/{0}/project/'.format(env.user)

    if setting_name == 'SERVER_REQUIREMENTS_PATH':
        return '{0}requirements.txt'.format(
            get_fab_setting('SERVER_REPO_PROJECT_ROOT'))

    if setting_name == 'SERVER_MEDIA_ROOT':
        return '/home/{0}/project_assets/media/'.format(env.user)

    if setting_name == 'SERVER_DB_BACKUP_DIR':
        return '/home/{0}/backups/{1}/postgres/'.format(
            env.user, PROJECT_NAME)

    if setting_name == 'SERVER_MEDIA_BACKUP_DIR':
        return '/home/{0}/backups/{1}/media/'.format(
            env.user, PROJECT_NAME)

    if setting_name == 'SERVER_WSGI_FILE':
        return '{0}{1}/wsgi.py'.format(
            get_fab_setting('SERVER_PROJECT_ROOT'), PROJECT_NAME)

    if setting_name == 'SERVER_LOCAL_ETC_DIR':
        return '/home/{0}/local/etc/'.format(env.user)


def FAB_SETTING(x):
    return get_fab_setting(x)
