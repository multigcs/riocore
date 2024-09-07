#!/bin/sh
#
#

BASEDIR=`dirname "$0"`
DIR="$1"

mkdir -p ~/.cache/thumbnails/normal
mkdir -p ~/.cache/thumbnails/large

ls $DIR/*.ngc $DIR/*.nc  $DIR/*.gcode 2>/dev/null | while read FILE
do

    if test -f $FILE
    then
        rm -rf /tmp/thumbnail.svg
        REALPATH=`realpath "$FILE"`
        MD5SUM=`echo -n file://$REALPATH | md5sum - | cut -d" " -f1`
        if ! test -e  ~/.cache/thumbnails/normal/$MD5SUM.png
        then
            echo $FILE
            python3 $BASEDIR/ngc2svg.py --no-g0 $FILE > /tmp/thumbnail.svg
            convert -scale 128x128 /tmp/thumbnail.svg ~/.cache/thumbnails/normal/$MD5SUM.png
            convert -scale 256x256 /tmp/thumbnail.svg ~/.cache/thumbnails/large/$MD5SUM.png
        fi
    fi

done


