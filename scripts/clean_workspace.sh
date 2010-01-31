#!/bin/bash

if [ -n "${WORKSPACE:-x}" ]; then
    exit 1
fi

cd $WORKSPACE
rm -rf *
rm -rf .hg*
