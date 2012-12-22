"""Fab tasks that execute things on a remote server."""
from django.conf import settings

from fabric.api import run

from development_fabfile.fabfile.utils import require_server


@require_server
def run_restart_apache():
    """
    Restarts apache on the given server.

    Usage::

        fab <server> run_restart_apache

    """
    run('{0}restart'.format(settings.SERVER_APACHE_BIN_DIR))
