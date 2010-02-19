from __future__ import with_statement
from os.path import join
from fabric.api import *

env.hosts = ['minddrag.zeropatience.net']
env.hostname = 'romulus'
env.repourl = 'ssh://hg@bitbucket.org/haikoschol/minddrag-django'
env.repodir = '/home/minddrag/minddrag-django'
env.venvdir = '/home/minddrag/minddrag-django-env'
env.projectdir = '/home/minddrag/minddrag-django/minddrag'
env.activate = 'source /home/minddrag/minddrag-django-env/bin/activate'
env.superusername = 'hs'
env.superusermail = 'hs@zeropatience.net'

def virtualenv(command):
    require('activate')
    run(env.activate + ' && ' + command)


def setup():
    require('repourl')
    require('venvdir')
    require('hostname')
    require('projectdir')
    require('superusername')
    require('superusermail')

    run('hg clone $(repourl)')
    with cd(env.repodir):
        run('python bootstrap.py $(venvdir)')
        run('cp settings/$(hostname)_settings.py $(projectdir)/local_settings.py')
    
    with cd(env.projectdir):
        virtualenv('python manage.py syncdb --noinput')
        virtualenv('python manage.py migrate')
        virtualenv('python manage.py createsuperuser --username $(superusername) --email $(superusermail) --noinput')


def deploy():
    require('repodir')
    require('hostname')
    require('projectdir')

    with cd(env.repodir):
        run('hg pull')
        run('hg update')
        virtualenv('pip install -r requirements.txt')
        virtualenv('pip install -r prod-requirements.txt')
        run('cp $(repodir)/settings/$(hostname)_settings.py $(projectdir)/local_settings.py')
        run('touch $(projectdir)/apache/django.wsgi')

    with cd(env.projectdir):
        virtualenv('python manage.py migrate')


def update_docs():
    require('projectdir')
    with cd(join(env.projectdir, 'docs')):
        run('make html')

