from __future__ import with_statement
from os.path import join
from fabric.api import *

env.hosts = ['minddrag.zeropatience.net']
env.user = 'minddrag'
env.hostname = 'romulus'
env.projectname = 'minddrag'
env.repourl = 'ssh://hg@bitbucket.org/haikoschol/minddrag-django'
env.repodir = '/home/minddrag/minddrag-django'
env.venvdir = '/home/minddrag/minddrag-django-env'
env.projectdir = '/home/minddrag/minddrag-django/minddrag'
env.activate = 'source /home/minddrag/minddrag-django-env/bin/activate'
env.superusername = 'hs'
env.superusermail = 'hs@zeropatience.net'


def prepare_deploy():
    with cd(env.projectname):
        local('python manage.py test core')


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

    run('hg clone %(repourl)s' % env)
    with cd(env.repodir):
        run('python bootstrap.py %(venvdir)s' % env)
        run('cp settings/%(hostname)s_settings.py %(projectdir)s/local_settings.py' % env)
    
    with cd(env.projectdir):
        virtualenv('python manage.py syncdb --noinput')
        virtualenv('python manage.py migrate')
        virtualenv('python manage.py createsuperuser --username %(superusername)s --email %(superusermail)s --noinput' % env)


def deploy():
    require('repodir')
    require('hostname')
    require('projectdir')

    prepare_deploy()
    
    with cd(env.repodir):
        run('hg pull')
        run('hg update')
        virtualenv('pip install -q -r requirements.txt')
        virtualenv('pip install -q -r prod-requirements.txt')
        run('cp %(repodir)s/settings/%(hostname)s_settings.py %(projectdir)s/local_settings.py' % env)
        run('touch %(projectdir)s/apache/django.wsgi' % env)

    with cd(env.projectdir):
        virtualenv('python manage.py migrate')


def update_docs():
    require('projectdir')
    with cd(join(env.projectdir, 'docs')):
        run('make html')

