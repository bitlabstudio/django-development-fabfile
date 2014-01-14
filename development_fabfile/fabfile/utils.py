"""Utilities for the fabfile."""
from functools import wraps

from fabric.api import env, run
from fabric.colors import red
from fabric.utils import abort


def require_server(fn):
    """
    Checks if the user has called the task with a server name.

    Fabric tasks decorated with this decorator must be called like so::

        fab <server name> <task name>

    If no server name is given, the task will not be executed.

    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if env.machine is None:
            abort(red('ERROR: You must provide a server name to call this'
                      ' task!'))
        return fn(*args, **kwargs)
    return wrapper


def run_workon(command):
    """
    Starts the virtualenv before running the given command.

    :param command: A string representing a shell command that should be
      executed.
    """
    env.shell = "/bin/bash -l -i -c"
    return run('workon {0} && {1}'.format(env.venv_name, command))
