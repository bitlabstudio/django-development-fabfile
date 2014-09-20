"""
Different server options that can be used when running fab tasks.

For example, if you want to export the database from the staging server
you can call the fab task like so::

    fab stage run_export_db

"""
from django.conf import settings

from fabric.api import env


def common_conf():
    """Sets some default values in the environment."""
    env.port = '22'
    env.pg_admin_role = 'postgres'
    env.venv_name = settings.VENV_NAME
common_conf()


def local_machine():
    """Option to do something on local machine."""
    common_conf()
    env.machine = 'local'
    env.pg_admin_role = settings.LOCAL_PG_ADMIN_ROLE
    env.db_backup_dir = settings.DJANGO_PROJECT_ROOT
    env.media_backup_dir = settings.DJANGO_PROJECT_ROOT

    # Not sure what this is good for. Not used in our fabfile.
    # env.media_root = settings.DJANGO_MEDIA_ROOT
    #env.local_db_password = settings.DJANGO_DB_PASSWORD

    env.db_role = getattr(settings, 'DB_ROLE_LOCAL', settings.DB_ROLE)
    env.db_name = getattr(settings, 'DB_NAME_LOCAL', settings.DB_NAME)


def dev():
    """Option to do something on the development server."""
    common_conf()
    env.user = settings.LOGIN_USER_DEV
    env.machine = 'dev'
    env.host_string = settings.HOST_DEV
    env.hosts = [env.host_string, ]
    env.db_role = getattr(settings, 'DB_ROLE_DEV', settings.DB_ROLE)
    env.db_name = getattr(settings, 'DB_NAME_DEV', settings.DB_NAME)


def stage():
    """Option to do something on the staging server."""
    common_conf()
    env.user = settings.LOGIN_USER_STAGE
    env.machine = 'stage'
    env.host_string = settings.HOST_STAGE
    env.hosts = [env.host_string, ]
    env.db_role = getattr(settings, 'DB_ROLE_STAGE', settings.DB_ROLE)
    env.db_name = getattr(settings, 'DB_NAME_STAGE', settings.DB_NAME)


def prod():
    """Option to do something on the production server."""
    common_conf()
    env.user = settings.LOGIN_USER_PROD
    env.machine = 'prod'
    env.host_string = settings.HOST_PROD
    env.hosts = [env.host_string, ]
    env.db_role = getattr(settings, 'DB_ROLE_PROD', settings.DB_ROLE)
    env.db_name = getattr(settings, 'DB_NAME_PROD', settings.DB_NAME)
