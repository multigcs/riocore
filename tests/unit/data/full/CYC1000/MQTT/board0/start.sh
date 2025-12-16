#!/bin/sh

set -e
set -x

DIRNAME=`dirname "$0"`

echo "compile package:"
(cd "$DIRNAME" && make clean all)

echo "running mqttbridge:"
$DIRNAME/mqttbridge $@

