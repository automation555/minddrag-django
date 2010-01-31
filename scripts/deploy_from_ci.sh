#!/bin/bash

cd $WORKSPACE

. minddrag-django-env/bin/activate

DEPLOY_STATUS = fab deploy > deploy_log.txt
fab update_docs >> deploy_log.txt
return $DEPLOY_STATUS

