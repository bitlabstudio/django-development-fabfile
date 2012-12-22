"""Fab tasks that execute things on a remote server."""
from django.conf import settings

from fabric.api import cd, run

from development_fabfile.fabfile.utils import require_server


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
def run_restart_apache():
    """
    Restarts apache on the given server.

    Usage::

        fab <server> run_restart_apache

    """
    run('{0}restart'.format(settings.SERVER_APACHE_BIN_DIR))
