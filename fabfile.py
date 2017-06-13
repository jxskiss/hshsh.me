#!/usr/bin/env python2
"""
Reference: Deployment via gh-pages branch
    https://gohugo.io/tutorials/github-pages-blog/
"""

from fabric.api import *
from fabric.context_managers import *
from os import listdir
from os.path import join, abspath, dirname, isfile, exists
from os.path import basename, splitext, getmtime
from datetime import date

_root = dirname(abspath(__file__))
_post = join(_root, 'content', 'post')


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


def worktree():
    with settings(warn_only=True):
        local('rm -rf public')
        local('git worktree prune')
        local('git worktree add -B gh-pages public origin/gh-pages')


def build(ipynb='convert'):
    if ipynb == 'convert':
        nbconvert()
    with settings(warn_only=True):
        local('hugo')


def publish(msg=''):
    if not msg:
        msg = 'Rebuilding site {}'.format(date.today().isoformat())
    with lcd('public'):
        with settings(warn_only=True):
            local('git add --all')
            local('git commit -m "{}"'.format(msg))


def push(branch=None):
    if not branch:
        branchs = ['master', 'gh-pages']
    else:
        branchs = [branch, ]
    for branch in branchs:
        local('git push origin {}'.format(branch))


def deploy(type_='publish'):
    msg = ''
    if not type_ == 'publish':
        msg = input("Commit message: ")
    publish(msg)
    push()
