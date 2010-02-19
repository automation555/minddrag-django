#!/bin/bash

# called from scripts directory?
if [[ "$PWD" =~ "/scripts" ]]; then
    cd ..
fi

ABOVE_REPO=`dirname $PWD`

# if no argument was given, use a default value for the virtualenv path
if [ $# -ge 1 ]; then
    VENV="$1"
else
    VENV="${ABOVE_REPO}/minddrag-django-env"
fi

python bootstrap.py $VENV

# copy server specific settings file in place
cp settings/romulus_settings.py minddrag/local_settings.py
