Django Development Fabfile
==========================

A fabfile to ease many tasks during development and deployment of Django
projects.


Installation
------------

Just add ``django-development-fabfile`` to your ``requirements.txt`` and
install it via ``pip install -r requirements.txt``.

Then create the following files in your project root (usually the folder where
your ``manage.py`` file resides)::

    fabfile/
    -- __init__.py
    -- your_own_fab_tasks.py

In your ``fabfile/__init__.py`` put the following code::

    # flake8: noqa
    from myproject import settings
    from django.core.management import setup_environ
    setup_environ(settings)

    from development_fabfile.fabfile import *
    from .your_own_fab_tasks import *

In your ``settings.py`` at the very bottom add the following::

    from fabfile_settings import *  # NOQA

Then create a ``fabfile_settings.py`` next to your ``settings.py`` and add
all necessary settings. As a starting point you can copy the
``fabfile_settings.py.sample`` of this project and change all values to your
project.
