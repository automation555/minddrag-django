#!/bin/bash

export PIP_DOWNLOAD_CACHE=$HOME/pip_download_cache

if [ -n "${WORKSPACE:-x}" ]; then
    WORKSPACE="$PWD"
fi

cd $WORKSPACE

python bootstrap.py --deploy minddrag-django-env

. minddrag-django-env/bin/activate

fab deploy > deploy_log.txt
DEPLOY_STATUS = $?
fab update_docs >> deploy_log.txt
exit $DEPLOY_STATUS

