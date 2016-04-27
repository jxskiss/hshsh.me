#!/usr/bin/env python2

from fabric.api import *
from fabric.context_managers import *
from os import listdir
from os.path import join, abspath, dirname, isfile, exists
from os.path import basename, splitext, getmtime
from datetime import date

_root = dirname(abspath(__file__))
_post = join(_root, 'content', 'post')


def _commit(msg):
    with settings(warn_only=True):
        local('git add -A')
        local('git commit -m "{}"'.format(msg))


def _push():
    local('git push origin master')
    local('git subtree push --prefix=public '
          'https://github.com/jxskiss/hshsh.me.git gh-pages')


def nbconvert():
    nbdir = join(_root, 'data', 'ipynbs')
    if not exists(nbdir):
        return
    nbfiles = filter(isfile, (join(nbdir, fn) for fn in listdir(nbdir)))
    count = 0
    with settings(warn_only=True):
        for fn in nbfiles:
            mdfile = join(_post, splitext(basename(fn))[0] + '.md')
            if getmtime(mdfile) >= getmtime(fn):
                continue
            local('jupyter nbconvert --stdout --to html --template basic '
                  '{} > {}'.format(fn, join(
                    _post, splitext(basename(fn))[0] + '.md')))
            count += 1
        print('nbconvert: {} new notebooks converted.'.format(count))


def build(ipynb='convert'):
    if ipynb == 'convert':
        nbconvert()
    with settings(warn_only=True):
        local('hugo')


def deploy(type_='publish'):
    msg = 'Rebuilding site {}'.format(date.today().isoformat())
    if not type_ == 'publish':
        msg = input("Commit message: ")
    _commit(msg)
    _push()
