#!/bin/sh

set -e
set -x

DIRNAME=`dirname "$0"`

(
    cd "$DIRNAME/"
    make simulator_run
)

