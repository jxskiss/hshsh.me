#!/usr/bin/env python2

from fabric.api import *
from fabric.context_managers import *
from datetime import date


def _commit(msg):
    with settings(warn_only=True):
        local('git add -A')
        local('git commit -m "{}"'.format(msg))


def _push():
    local('git push origin master')
    local('git subtree push --prefix=public '
          'https://github.com/jxskiss/hshsh.me.git gh-pages')


def build():
    with settings(warn_only=True):
        local('hugo')


def deploy(type_='publish'):
    msg = 'Rebuilding site {}'.format(date.today().isoformat())
    if not type_ == 'publish':
        msg = input("Commit message: ")
    _commit(msg)
    _push()
