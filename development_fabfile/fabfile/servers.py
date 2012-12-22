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
    env.user = settings.LOGIN_USER
    env.port = '22'
    env.pg_admin_role = 'postgres'
    env.machine = None
    env.venv_name = settings.VENV_NAME
    env.repo_root = settings.SERVER_REPO_ROOT
    env.project_root = settings.SERVER_PROJECT_ROOT
    env.db_backup_dir = settings.SERVER_DB_BACKUP_DIR
    env.media_backup_dir = settings.SERVER_MEDIA_BACKUP_DIR
    env.media_root = settings.SERVER_MEDIA_ROOT
common_conf()


def local_machine():
    """Option to do something on local machine."""
    common_conf()
    env.machine = 'local'
    env.pg_admin_role = settings.LOCAL_PG_ADMIN_ROLE
    env.db_backup_dir = settings.DJANGO_PROJECT_ROOT
    env.media_backup_dir = settings.DJANGO_PROJECT_ROOT
    env.media_root = settings.DJANGO_MEDIA_ROOT
    env.local_db_password = settings.DJANGO_DB_PASSWORD


def dev():
    """Option to do something on the development server."""
    common_conf()
    env.machine = 'dev'
    env.host_string = settings.HOST_DEV
    env.hosts = [env.host_string, ]


def stage():
    """Option to do something on the staging server."""
    common_conf()
    env.machine = 'stage'
    env.host_string = settings.HOST_STAGE
    env.hosts = [env.host_string, ]


def prod():
    """Option to do something on the production server."""
    common_conf()
    env.machine = 'prod'
    env.host_string = settings.HOST_PROD
    env.hosts = [env.host_string, ]
