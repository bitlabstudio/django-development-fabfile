"""Fab tasks that execute things on a remote server."""
import sys

import django
from django.conf import settings

from distutils.version import StrictVersion
from fabric.api import cd, env, local, run

from .local import drop_db, create_db, import_db, import_media, reset_passwords
from .utils import require_server, run_workon


PYTHON_VERSION = '{}.{}'.format(sys.version_info.major, sys.version_info.minor)

if getattr(settings, 'PEM_KEY_DIR', False):
    env.key_filename = settings.PEM_KEY_DIR


@require_server
def run_collectstatic():
    """
    Runs `./manage.py collectstatic` on the given server.

    Usage::

        fab <server> run_collectstatic

    """
    with cd(settings.FAB_SETTING('SERVER_PROJECT_ROOT')):
        run_workon('python{} manage.py collectstatic --noinput'.format(
            PYTHON_VERSION))


@require_server
def run_compilemessages():
    """
    Executes ./manage.py compilemessages on the server.

    Usage::

        fab <server name> run_compilemessages

    """

    with cd(settings.FAB_SETTING('SERVER_PROJECT_ROOT')):
        run_workon('python{} manage.py compilemessages'.format(PYTHON_VERSION))


@require_server
def run_deploy_website(restart_apache=False, restart_uwsgi=False,
                       restart_nginx=False):
    """
    Executes all tasks necessary to deploy the website on the given server.

    Usage::

        fab <server> run_deploy_website

    """
    run_git_pull()
    run_pip_install()
    run_rsync_project()
    run_syncdb()
    run_collectstatic()
    if getattr(settings, 'MAKEMESSAGES_ON_DEPLOYMENT', False):
        run_makemessages()
    if getattr(settings, 'COMPILEMESSAGES_ON_DEPLOYMENT', False):
        run_compilemessages()
    if restart_apache:
        run_restart_apache()
    if restart_uwsgi:
        run_restart_uwsgi()
    if restart_nginx:
        run_restart_nginx()
    else:
        run_touch_wsgi()


@require_server
def run_download_db(filename=None):
    """
    Downloads the database from the server into your local machine.

    In order to import the downloaded database, run ``fab import_db``

    Usage::

        fab prod run_download_db
        fab prod run_download_db:filename=foobar.dump

    """
    if not filename:
        filename = settings.DB_DUMP_FILENAME
    if env.key_filename:
        ssh = settings.PROJECT_NAME
    else:
        ssh = '{0}@{1}'.format(env.user, env.host_string)
    local('scp {0}:{1}{2} .'.format(
        ssh, settings.FAB_SETTING('SERVER_DB_BACKUP_DIR'), filename))


@require_server
def run_download_media(filename=None):
    """
    Downloads the media dump from the server into your local machine.

    In order to import the downloaded media dump, run ``fab import_media``

    Usage::

        fab prod run_download_media
        fab prod run_download_media:filename=foobar.tar.gz

    """
    if not filename:
        filename = settings.MEDIA_DUMP_FILENAME
    if env.key_filename:
        ssh = settings.PROJECT_NAME
    else:
        ssh = '{0}@{1}'.format(env.user, env.host_string)
    local('scp {0}:{1}{2} .'.format(
        ssh, settings.FAB_SETTING('SERVER_MEDIA_BACKUP_DIR'), filename))


@require_server
def run_export_db(filename=None):
    """
    Exports the database on the server.

    Usage::

        fab prod run_export_db
        fab prod run_export_db:filename=foobar.dump

    """
    if not filename:
        filename = settings.DB_DUMP_FILENAME
    with cd(settings.FAB_SETTING('SERVER_PROJECT_ROOT')):
        run_workon('fab export_db:remote=True,filename={}'.format(filename))


@require_server
def run_export_media(filename=None):
    """
    Exports the media folder on the server.

    Usage::

        fab prod run_export_media
        fab prod run_export_media:filename=foobar.tar.gz

    """
    if not filename:
        filename = settings.MEDIA_DUMP_FILENAME

    with cd(settings.FAB_SETTING('SERVER_MEDIA_ROOT')):
        run('rm -rf {0}'.format(filename))
        run('tar -czf {0} *'.format(filename))
        run('mv {0} {1}'.format(
            filename, settings.FAB_SETTING('SERVER_MEDIA_BACKUP_DIR')))


@require_server
def run_git_pull():
    """
    Pulls the latest code and updates submodules.

    Usage::

        fab <server> run_git_pull

    """
    with cd(settings.FAB_SETTING('SERVER_REPO_ROOT')):
        run('git pull && git submodule init && git submodule update')


@require_server
def import_remote_db():
    """
    Downloads a db and imports it locally.

    """
    run_export_db()
    run_download_db()
    drop_db()
    create_db()
    import_db()
    reset_passwords()


@require_server
def import_remote_media():
    """
    Downloads media and imports it locally.

    """
    run_export_media()
    run_download_media()
    import_media()


@require_server
def run_makemessages():
    """
    Executes ./manage.py makemessages -s --all on the server.

    Usage::

        fab <server name> run_makemessages

    """
    with cd(settings.FAB_SETTING('SERVER_PROJECT_ROOT')):
        run_workon('python{} manage.py makemessages -s --all'.format(
            PYTHON_VERSION))


@require_server
def run_pip_install(upgrade=0):
    """
    Installs the requirement.txt file on the given server.

    Usage::

        fab <server> run_pip_install
        fab <server> run_pip_install:upgrade=1

    :param upgrade: If set to 1, the command will be executed with the
      ``--upgrade`` flag.

    """
    command = 'pip install -r {0}'.format(
        settings.FAB_SETTING('SERVER_REQUIREMENTS_PATH'))
    if upgrade:
        command += ' --upgrade'
    run_workon(command)


@require_server
def run_restart_apache():
    """
    Restarts apache on the given server.

    Usage::

        fab <server> run_restart_apache

    """
    run('{0}restart'.format(settings.FAB_SETTING('SERVER_APACHE_BIN_DIR')))


@require_server
def run_restart_uwsgi():
    """
    Restarts uwsgi on the given server.

    Usage::

        fab <server> run_restart_uwsgi

    """

    with cd(settings.FAB_SETTING('SERVER_LOCAL_ETC_DIR')):
        run('supervisorctl restart uwsgi')


@require_server
def run_restart_nginx():
    """
    Restarts uwsgi on the given server.

    Usage::

        fab <server> run_restart_nginx

    """

    with cd(settings.FAB_SETTING('SERVER_LOCAL_ETC_DIR')):
        run('supervisorctl restart nginx')


@require_server
def run_rsync_project():
    """
    Copies the project from the git repository to it's destination folder.

    This has the nice side effect of rsync deleting all ``.pyc`` files and
    removing other files that might have been left behind by sys admins messing
    around on the server.

    Usage::

        fab <server> run_rsync_project

    """
    excludes = ''
    for exclude in settings.RSYNC_EXCLUDES:
        excludes += " --exclude '{0}'".format(exclude)
    command = "rsync -avz --stats --delete {0} {1} {2}".format(
        excludes, settings.FAB_SETTING('SERVER_REPO_PROJECT_ROOT'),
        settings.FAB_SETTING('SERVER_APP_ROOT'))
    run(command)


@require_server
def run_syncdb():
    """
    Runs `./manage.py syncdb --migrate` on the given server.

    Usage::

        fab <server> run_syncdb

    """
    with cd(settings.FAB_SETTING('SERVER_PROJECT_ROOT')):
        if StrictVersion(django.get_version()) < StrictVersion('1.7'):
            run_workon('python{} manage.py syncdb --migrate --noinput'.format(
                PYTHON_VERSION))
        else:
            run_workon('python{} manage.py migrate'.format(PYTHON_VERSION))


@require_server
def run_touch_wsgi():
    """
    Runs `touch <path>/wsgi.py` on the given server.

    Usage::

        fab <server> run_touch_wsgi

    """
    run('touch {0}'.format(settings.FAB_SETTING('SERVER_WSGI_FILE')))


@require_server
def run_upload_db(filename=None):
    """
    Uploads your local database to the server.

    You can create a local dump with ``fab export_db`` first.

    In order to import the database on the server you still need to SSH into
    the server.

    Usage::

        fab prod run_upload_db
        fab prod run_upload_db:filename=foobar.dump

    """
    if not filename:
        filename = settings.DB_DUMP_FILENAME
    if env.key_filename:
        ssh = settings.PROJECT_NAME
    else:
        ssh = '{0}@{1}'.format(env.user, env.host_string)
    local('scp {0} {1}:{3}'.format(
        filename, ssh, settings.FAB_SETTING('SERVER_DB_BACKUP_DIR')))
