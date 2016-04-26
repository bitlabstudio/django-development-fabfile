import os
from setuptools import setup, find_packages
import development_fabfile as app


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''


setup(
    name="django-development-fabfile",
    version=app.__version__,
    description=read('DESCRIPTION'),
    long_description=read('README.rst'),
    license='The MIT License',
    platforms=['OS Independent'],
    keywords='django, fabric, development, environemnt, deployment',
    author='Martin Brochhaus',
    author_email='martin.brochhaus@bitmazk.com',
    url="https://github.com/bitmazk/django-development-fabfile",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django',
        'fabric3',
        'flake8_snippets'
    ],
)
