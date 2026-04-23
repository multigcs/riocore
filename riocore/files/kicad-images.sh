#!/bin/sh
#
#

find riocore/plugins/ | grep "/kicad/.*/.*.kicad_pcb" | while read FILENAME
do
    BASENAME=`basename $FILENAME .kicad_pcb`
    DIRNAME=`dirname $FILENAME`
    echo "$DIRNAME/$BASENAME.png"
    
    kicad-cli pcb render --output "$DIRNAME/$BASENAME-render.png" "$FILENAME"
    kicad-cli pcb export svg --fit-page-to-board --layers F.Cu,F.SilkS,Edge.Cuts --output "$DIRNAME/$BASENAME-export.svg" "$FILENAME"
    convert "$DIRNAME/$BASENAME-export.svg" "$DIRNAME/$BASENAME-export.png"
done
