"""Fab tasks that execute things on a remote server."""
from django.conf import settings

from fabric.api import cd, run

from development_fabfile.fabfile.utils import require_server, run_workon


@require_server
def run_collectstatic():
    """
    Runs `./manage.py collectstatic` on the given server.

    Usage::

        fab <server> run_collectstatic

    """
    with cd(settings.SERVER_PROJECT_ROOT):
        run_workon('python2.7 manage.py collectstatic --noinput')


@require_server
def run_deploy_website():
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
    run_restart_apache()


@require_server
def run_git_pull():
    """
    Pulls the latest code and updates submodules.

    Usage::

        fab <server> run_git_pull

    """
    with cd(settings.SERVER_REPO_ROOT):
        run('git pull && git submodule init && git submodule update')


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
    command = 'pip install -r {0}'.format(settings.SERVER_REQUIREMENTS_PATH)
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
    run('{0}restart'.format(settings.SERVER_APACHE_BIN_DIR))


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
        excludes, settings.SERVER_REPO_PROJECT_ROOT, settings.SERVER_APP_ROOT)
    run(command)


@require_server
def run_syncdb():
    """
    Runs `./manage.py syncdb --migrate` on the given server.

    Usage::

        fab <server> run_syncdb

    """
    with cd(settings.SERVER_PROJECT_ROOT):
        run_workon('python2.7 manage.py syncdb --migrate --noinput')
