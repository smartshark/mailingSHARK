#!/bin/bash

current=`pwd`
mkdir -p /tmp/mailingSHARK/
cp -R ../mailingshark /tmp/mailingSHARK/
cp ../setup.py /tmp/mailingSHARK/
cp ../main.py /tmp/mailingSHARK
cp ../loggerConfiguration.json /tmp/mailingSHARK
cp * /tmp/mailingSHARK/
cd /tmp/mailingSHARK/

tar -cvf "$current/mailingSHARK_plugin.tar" --exclude=*.tar --exclude=build_plugin.sh --exclude=*/tests --exclude=*/__pycache__ --exclude=*.pyc *
