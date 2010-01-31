#!/bin/bash

export PIP_DOWNLOAD_CACHE=$HOME/pip_download_cache

# the name of the app inside myproject to test is required
# as command line argument
[ $# -ge 1 ] || exit 1 

cd $WORKSPACE

# install requirements
python bootstrap.py --ci minddrag-django-env
. minddrag-django-env/bin/activate

# make sure $1 contains a valid app name
[ -d minddrag/$1 ] || exit 1

# run tests
cd minddrag
python manage.py test --settings=test_settings --with-xunit --with-coverage --cover-package=$1 --with-xcoverage $1

