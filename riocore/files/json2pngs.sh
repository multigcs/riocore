#!/bin/bash
#
#

mkdir -p pngs
find riocore/configs/ | grep  "\.json" | while read JSON
do
    PNG=`basename "$JSON" .json`.png
    DIRNAME=`dirname "$JSON"`
    PREFIX=`basename "$DIRNAME"`
    echo "$PREFIX-$PNG"
    bin/rio-flow "$JSON" -p "pngs/$PREFIX-$PNG"
done

