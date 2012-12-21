"""Fabfile for tasks that only manipulate things on the local machine."""
from django.conf import settings
from fabric.api import local


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
