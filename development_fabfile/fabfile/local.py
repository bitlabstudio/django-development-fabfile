"""Fabfile for tasks that only manipulate things on the local machine."""
import os
import re

from django.conf import settings

from fabric.api import hide, lcd, local
from fabric.api import settings as fab_settings
from fabric.colors import green, red
from fabric.utils import abort


USER_AND_HOST = '-U {0}'.format(settings.LOCAL_PG_ADMIN_ROLE)
if getattr(settings, 'LOCAL_PG_USE_LOCALHOST', True):
    USER_AND_HOST += ' -h localhost'

DB_PASSWORD = settings.DATABASES['default']['PASSWORD']


def check():
    """Runs flake8, check_coverage and test."""
    flake8()
    test()
    check_coverage()


def check_coverage():
    """Checks if the coverage is 100%."""
    with lcd(settings.LOCAL_COVERAGE_PATH):
        total_line = local('grep -n Total index.html', capture=True)
        match = re.search(r'^(\d+):', total_line)
        total_line_number = int(match.groups()[0])
        percentage_line_number = total_line_number + 4
        percentage_line = local(
            'awk NR=={0} index.html'.format(percentage_line_number),
            capture=True)
        match = re.search(r'<td>(\d.+)%</td>', percentage_line)
        percentage = float(match.groups()[0])
    if percentage < 100:
        abort(red('Coverage is {0}%'.format(percentage)))
    print(green('Coverage is {0}%'.format(percentage)))


def create_db(with_postgis=False):
    """
    Creates the local database.

    :param with_postgis: If ``True``, the postgis extension will be installed.

    """
    local('psql {0} -c "CREATE USER {1} WITH PASSWORD \'{2}\'"'.format(
        USER_AND_HOST, settings.DB_ROLE, DB_PASSWORD))
    local('psql {0} -c "CREATE DATABASE {1} ENCODING \'UTF8\'"'.format(
        USER_AND_HOST, settings.DB_NAME))
    if with_postgis:
        local('psql {0} {1} -c "CREATE EXTENSION postgis"'.format(
            USER_AND_HOST, settings.DB_NAME))
    local('psql {0} -c "GRANT ALL PRIVILEGES ON DATABASE {1}'
          ' to {1}"'.format(USER_AND_HOST, settings.DB_ROLE))
    local('psql {0} {1} -c "GRANT ALL PRIVILEGES ON ALL TABLES'
          ' IN SCHEMA public TO {2}"'.format(
              USER_AND_HOST, settings.DB_NAME, settings.DB_ROLE))


def delete_db():
    """
    Deletes all data in the database.

    You need django-extensions in order to use this.
    However, please note that this is not as thorough as a real database drop.

    """
    local(' ./manage.py reset_db --router=default --noinput')


def export_db(filename=None):
    """
    Exports the database.

    Make sure that you have this in your ``~/.pgpass`` file:

    localhost:5433:*:<db_role>:<password>

    Also make sure that the file has ``chmod 0600 .pgpass``.

    Usage::

        fab export_db
        fab export_db:filename=foobar.dump

    """
    if not filename:
        filename = settings.DB_DUMP_FILENAME
    local('pg_dump -c -Fc -O -U {0} -f {1}'.format(
        settings.DB_ROLE, filename))


def drop_db():
    """Drops the local database."""
    with fab_settings(warn_only=True):
        local('psql {0} -c "DROP DATABASE {1}"'.format(
            USER_AND_HOST, settings.DB_NAME))
        local('psql {0} -c "DROP USER {1}"'.format(
            USER_AND_HOST, settings.DB_ROLE))


def flake8():
    """Runs flake8 against the codebase."""
    return local('flake8 --ignore=E126 --statistics '
                 '--exclude=submodules,migrations .')


def import_db(filename=None):
    """
    Imports the database.

    Make sure that you have this in your ``~/.pgpass`` file:

    localhost:5433:*:publishizer_publishizer:publishizer

    Also make sure that the file has ``chmod 0600 .pgpass``.

    Usage::

        fab import_db
        fab import_db:filename=foobar.dump

    """
    if not filename:
        filename = settings.DB_DUMP_FILENAME
    with fab_settings(warn_only=True):
        local('pg_restore -O -c -U {0} -d {1} {2}'.format(
            settings.DB_ROLE, settings.DB_NAME, filename))


def import_media(filename=None):
    """
    Extracts media dump into your local media root.

    Please note that this might overwrite existing local files.

    Usage::

        fab import_media
        fab import_media:filename=foobar.tar.gz

    """
    if not filename:
        filename = settings.MEDIA_DUMP_FILENAME

    project_root = os.getcwd()

    with fab_settings(hide('everything'), warn_only=True):
        is_backup_missing = local('test -e "$(echo %s)"' % os.path.join(
            project_root, filename)).failed
    if is_backup_missing:
        abort(red('ERROR: There is no media backup that could be imported in'
                  ' {0}. We need a file called {1} in that folder.'.format(
                      project_root, filename)))

    # copy the dump into the media root folder
    with lcd(project_root):
        local('cp {0} {1}'.format(filename, settings.MEDIA_ROOT))

    # extract and remove media dump
    with lcd(settings.MEDIA_ROOT):
        local('tar -xvf {0}'.format(filename))
        local('rm -rf {0}'.format(filename))


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
    drop_db()
    create_db()
    local('python2.7 manage.py syncdb --all --noinput')
    local('python2.7 manage.py migrate --fake')


def reset_passwords():
    """Resets all passwords to `test123`."""
    local('python2.7 manage.py set_fake_passwords --password=test123')


def test(options=None, integration=1, selenium=1, test_settings=None):
    """
    Runs manage.py tests.

    Usage::

        fab test
        fab test:app
        fab test:app.tests.forms_tests:TestCaseName
        fab test:integration=0
        fab test:selenium=0

    """
    if test_settings is None:
        test_settings = settings.TEST_SETTINGS_PATH
    command = ("./manage.py test -v 2 --traceback --failfast" +
               " --settings={0}".format(test_settings))
    if int(integration) == 0:
        command += " --exclude='integration_tests'"
    if int(selenium) == 0:
        command += " --exclude='selenium_tests'"
    if options:
        command += ' {0}'.format(options)
    with fab_settings(warn_only=True):
        result = local(command, capture=False)
    if result.failed:
        abort(red('Some tests failed'))
    else:
        print green('All tests passed')
