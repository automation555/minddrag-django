from __future__ import with_statement
from os.path import join
from fabric.api import *

env.hosts = ['minddrag.zeropatience.net']
env.user = 'minddrag'
env.repourl = 'ssh://hg@bitbucket.org/haikoschol/minddrag-django'
env.projectdir = '/home/minddrag/minddrag-django'
env.activate = 'source /home/minddrag/minddrag-django-env/bin/activate'

def virtualenv(command):
    run(env.activate + ' && ' + command)


def setup():
    run('hg clone ' + env.repourl)
    with cd(env.projectdir):
        run('scripts/setup_prod.sh')
    with cd(join(env.projectdir, 'minddrag')):
        virtualenv('python manage.py syncdb --noinput')
        virtualenv('python manage.py createsuperuser --username hs --email hs@zeropatience.net --noinput')


def deploy():
    with cd(env.projectdir):
        run('hg pull')
        run('hg update')
        virtualenv('pip install -r requirements.txt')
        virtualenv('pip install -r prod-requirements.txt')
        # ***FIXME*** use current host for local settings file name
        # and infer file name from env.hosts variable
        run('cp settings/romulus_settings.py minddrag/local_settings.py')
        run('touch minddrag/apache/django.wsgi')


def update_docs():
    with cd(join(env.projectdir, 'docs')):
        run('make html')

