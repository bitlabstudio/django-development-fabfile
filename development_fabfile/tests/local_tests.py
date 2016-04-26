"""Tests for local fab commands."""
from django.test import TestCase

from ..fabfile.local import check, flake8, jshint


class JshintTestCase(TestCase):
    def test_command(self):
        jshint()


class Flake8TestCase(TestCase):
    def test_command(self):
        flake8()


class CheckTestCase(TestCase):
    def test_command(self):
        with self.assertRaises(SystemExit):
            check()
