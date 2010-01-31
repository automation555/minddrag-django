#!/bin/bash

#export PIP_DOWNLOAD_CACHE=$HOME/pip_download_cache

#if [ -n "${WORKSPACE:-x}" ]; then
#    WORKSPACE="$PWD"
#fi

#cd $WORKSPACE

#python bootstrap.py --deploy minddrag-django-env

#. minddrag-django-env/bin/activate

#fab deploy > deploy_log.txt
#DEPLOY_STATUS = $?
#fab update_docs >> deploy_log.txt
#exit $DEPLOY_STATUS

# ***FIXME*** kludgey workaround! this assumes that hudson and
# the minddrag django app run on the same box! hardcoded paths!
# ugly hackery galore!

cd /tmp
sudo su minddrag
cd /home/minddrag/minddrag-django
. minddrag-django-env/bin/activate
hg pull
hg update
pip install -r requirements.txt
pip install -r prod-requirements.txt
touch minddrag/apache/django.wsgi

cd docs
make html

