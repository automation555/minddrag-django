#!/bin/sh

# called from scripts directory?
if [[ $PWD =~ "/scripts" ]]; then
    cd ..
fi

cd docs
make html

