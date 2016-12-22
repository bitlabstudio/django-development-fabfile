"""Fabfile for tasks that only manipulate things on the local machine."""
import django
import os
import re
import sys

from django.conf import settings

from distutils.version import StrictVersion
from fabric.api import hide, lcd, local
from fabric.api import settings as fab_settings
from fabric.colors import green, red
from fabric.utils import abort, warn, puts
from fabric.state import env

from .servers import local_machine


USER_AND_HOST = '-U {0}'.format(settings.LOCAL_PG_ADMIN_ROLE)
if getattr(settings, 'LOCAL_PG_USE_LOCALHOST', True):
    USER_AND_HOST += ' -h localhost'

HOST = ''
if getattr(settings, 'LOCAL_PG_USE_LOCALHOST', True):
    HOST = ' -h localhost'


DB_PASSWORD = settings.DATABASES['default']['PASSWORD']

PYTHON_VERSION = '{}.{}'.format(sys.version_info.major, sys.version_info.minor)


def check():
    """Runs flake8, check_coverage and test."""
    flake8()
    syntax_check()
    jshint()
    test()
    check_coverage()


def check_coverage():
    """Checks if the coverage is 100%."""
    with lcd(settings.LOCAL_COVERAGE_PATH):
        total_line = local('grep -n Total index.html', capture=True)
        match = re.search(r'^(\d+):', total_line)
        total_line_number = int(match.groups()[0])
        percentage_line_number = total_line_number + 5
        percentage_line = local(
            'awk NR=={0} index.html'.format(percentage_line_number),
            capture=True)
        match = re.search(r'(\d.+)%', percentage_line)
        try:
            percentage = float(match.groups()[0])
        except ValueError:
            # If there's no dotting try another search
            match = re.search(r'(\d+)%', percentage_line)
            percentage = float(match.groups()[0])
    if percentage < 100:
        abort(red('Coverage is {0}%'.format(percentage)))
    print(green('Coverage is {0}%'.format(percentage)))


def create_db(with_postgis=False):
    """
    Creates the local database.

    :param with_postgis: If ``True``, the postgis extension will be installed.

    """
    local_machine()
    local('psql {0} -c "CREATE USER {1} WITH PASSWORD \'{2}\'"'.format(
        USER_AND_HOST, env.db_role, DB_PASSWORD))
    local('psql {0} -c "CREATE DATABASE {1} ENCODING \'UTF8\'"'.format(
        USER_AND_HOST, env.db_name))
    if with_postgis:
        local('psql {0} {1} -c "CREATE EXTENSION postgis"'.format(
            USER_AND_HOST, env.db_name))
    local('psql {0} -c "GRANT ALL PRIVILEGES ON DATABASE {1}'
          ' to {2}"'.format(USER_AND_HOST, env.db_name, env.db_role))
    local('psql {0} -c "GRANT ALL PRIVILEGES ON ALL TABLES'
          ' IN SCHEMA public TO {1}"'.format(
              USER_AND_HOST, env.db_role))


def delete_db():
    """
    Deletes all data in the database.

    You need django-extensions in order to use this.
    However, please note that this is not as thorough as a real database drop.

    """
    local(' ./manage.py reset_db --router=default --noinput')


def export_db(filename=None, remote=False):
    """
    Exports the database.

    Make sure that you have this in your ``~/.pgpass`` file:

    localhost:5433:*:<db_role>:<password>

    Also make sure that the file has ``chmod 0600 .pgpass``.

    Usage::

        fab export_db
        fab export_db:filename=foobar.dump

    """
    local_machine()
    if not filename:
        filename = settings.DB_DUMP_FILENAME
    if remote:
        backup_dir = settings.FAB_SETTING('SERVER_DB_BACKUP_DIR')
        host_arg = ''
    else:
        backup_dir = ''
        host_arg = HOST

    local('pg_dump -c -Fc -O -h localhost -U {0}{1} {2} -f {3}{4}'.format(
        env.db_role, host_arg, env.db_name, backup_dir, filename))


def drop_db():
    """Drops the local database."""
    local_machine()
    with fab_settings(warn_only=True):
        local('psql {0} -c "DROP DATABASE {1}"'.format(
            USER_AND_HOST, env.db_name))
        local('psql {0} -c "DROP USER {1}"'.format(
            USER_AND_HOST, env.db_role))


def jshint():
    """Runs jshint checks."""
    with fab_settings(warn_only=True):
        needs_to_abort = False
        # because jshint fails with exit code 2, we need to allow this as
        # a successful exit code in our env
        if 2 not in env.ok_ret_codes:
            env.ok_ret_codes.append(2)
        output = local(
            'find -name "{}" -print'.format('*.js'),
            capture=True,
        )
        files = output.split()
        jshint_installed = local('command -v jshint', capture=True)
        if not jshint_installed.succeeded:
            warn(red(
                "To enable an extended check of your js files, please"
                " install jshint by entering:\n\n    npm install -g jshint"
            ))
        else:
            for file in files:
                if hasattr(settings, 'JSHINT_CHECK_EXCLUDES'):
                    excludes = settings.JSHINT_CHECK_EXCLUDES
                else:
                    excludes = settings.SYNTAX_CHECK_EXCLUDES
                if any(s in file for s in excludes):
                    continue
                jshint_result = local(
                    'jshint {0}'.format(file),
                    capture=True
                )
                if jshint_result:
                    warn(red('JS errors detected in file {0}'.format(
                        file
                    )))
                    puts(jshint_result)
                    needs_to_abort = True
        if needs_to_abort:
            abort(red('There have been errors. Please fix them and run'
                      ' the check again.'))
        else:
            puts(green('jshint found no errors. Very good!'))


def syntax_check():
    """Runs flake8 against the codebase."""
    with fab_settings(warn_only=True):
        for file_type in settings.SYNTAX_CHECK:
            needs_to_abort = False
            # because egrep fails with exit code 1, we need to allow this as
            # a successful exit code in our env
            if 1 not in env.ok_ret_codes:
                env.ok_ret_codes.append(1)
            output = local(
                'find -name "{}" -print'.format(file_type),
                capture=True,
            )
            files = output.split()
            for file in files:
                if any(s in file for s in settings.SYNTAX_CHECK_EXCLUDES):
                    continue
                result = local('egrep -i -n "{0}" {1}'.format(
                    settings.SYNTAX_CHECK[file_type], file), capture=True)
                if result:
                    warn(red("Syntax check found in '{0}': {1}".format(
                        file, result)))
                    needs_to_abort = True
            if needs_to_abort:
                abort(red('There have been errors. Please fix them and run'
                          ' the check again.'))
            else:
                puts(green('Syntax check found no errors. Very good!'))


def flake8():
    """Runs flake8 against the codebase."""
    return local('flake8 --ignore=E126 --statistics '
                 '--exclude=submodules,south_migrations,migrations,'
                 'node_modules .')


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
    local_machine()
    if not filename:
        filename = settings.DB_DUMP_FILENAME
    with fab_settings(warn_only=True):
        local('pg_restore -O -c -U {0}{1} -d {2} {3}'.format(
            env.db_role, HOST, env.db_name, filename))


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


def lessc(responsive=False):
    """
    Compiles all less files.

    This is useful if you are using the Twitter Bootstrap Framework.

    """
    local('lessc {0}/static/css/bootstrap.less'
          ' {0}/static/css/bootstrap.css'.format(settings.PROJECT_NAME))
    if responsive:
        local('lessc {0}/static/css/responsive.less'
              ' {0}/static/css/bootstrap-responsive.css'.format(
                  settings.PROJECT_NAME))


def rebuild():
    """
    Deletes and re-creates your DB. Needs django-extensions and South.

    """
    drop_db()
    create_db()
    if StrictVersion(django.get_version()) < StrictVersion('1.7'):
        local('python{} manage.py syncdb --all --noinput'.format(
            PYTHON_VERSION))
        local('python{} manage.py migrate --fake'.format(PYTHON_VERSION))
    else:
        local('python{} manage.py migrate'.format(PYTHON_VERSION))


def reset_passwords():
    """Resets all passwords to `test123`."""
    local('python{} manage.py set_fake_passwords --password=test123'.format(
        PYTHON_VERSION))


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
    command = ("coverage run --source='.' manage.py test -v 2" +
               " --failfast --settings={0} --pattern='*_tests.py'".format(
                   test_settings))
    if int(integration) == 0:
        command += " --exclude='integration_tests'"
    if int(selenium) == 0:
        command += " --exclude='selenium_tests'"
    if options:
        command += ' {0}'.format(options)
    with fab_settings(warn_only=True):
        local(command, capture=False)
    local('coverage html -d coverage --omit="{}"'.format(
        settings.COVERAGE_EXCLUDES))
