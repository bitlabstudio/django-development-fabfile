"""Fabfile for tasks that only manipulate things on the local machine."""
from django.conf import settings

from fabric.api import local
from fabric.api import settings as fab_settings
from fabric.colors import green, red


def delete_db():
    """Deletes all data in the database."""
    local(' ./manage.py reset_db --router=default --noinput')


def flake8():
    """Runs flake8 against the codebase."""
    return local('flake8 --ignore=E126 --statistics .')


def lessc():
    """
    Compiles all less files.

    This is useful if you are using the Twitter Bootstrap Framework.

    TODO: Write a blog post about this.

    """
    local('lessc {0}/static/css/bootstrap.less'
          ' {0}/static/css/bootstrap.css'.format(settings.PROJECT_NAME))
    local('lessc {0}/static/css/responsive.less'
          ' {0}/static/css/bootstrap-responsive.css'.format(
            settings.PROJECT_NAME))


def rebuild():
    """
    Deletes and re-creates your DB. Needs django-extensions and South.

    """
    delete_db()
    local('python2.7 manage.py syncdb --all --noinput')
    local('python2.7 manage.py migrate --fake')


def test(options=None, integration=1,
         test_settings='myproject.settings.test_settings'):
    """
    Runs manage.py tests.

    Usage::

        fab test
        fab test:app
        fab test:app.tests.forms_tests:TestCaseName
        fab test:integration=0

    """
    command = ("./manage.py test -v 2 --traceback --failfast" +
               " --settings={0}".format(test_settings))
    if int(integration) == 0:
        command += " --exclude='integration_tests'"
    if options:
        command += ' {0}'.format(options)
    with fab_settings(warn_only=True):
        result = local(command, capture=False)
    if result.failed:
        print red('Some tests failed')
    else:
        print green('All tests passed')
