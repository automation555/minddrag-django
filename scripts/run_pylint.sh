#!/bin/bash

# the name of the app inside myproject to run pylint on is required
# as command line argument
[ $# -ge 1 ] || exit 1 

if [ -n "${WORKSPACE:-x}" ]; then
    WORKSPACE="$PWD"
fi

cd $WORKSPACE

# make sure $1 contains a valid app name
[ -d minddrag/$1 ] || exit 1

# activate virtualenv
. minddrag-django-env/bin/activate

# run pylint
cd minddrag
# using ubuntus pylint, therefore the virtualenv doesn't work
# hack upon hack upon hack :(
PYTHONPATH=$PYTHONPATH:$WORKSPACE/minddrag-django-env/lib/python2.6/site-packages pylint --rcfile ../scripts/pylintrc -f parseable $1 | egrep -v "__init__.py:1: \[C0111\] Missing docstring" | egrep -v "No name '(test|db)' in module 'django'" > pylint.txt
echo "done" # return success to hudson
