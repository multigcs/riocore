#!/bin/sh
#
#

find riocore/plugins/ | grep "/kicad/.*/.*.kicad_pcb" | while read FILENAME
do
    BASENAME=`basename $FILENAME .kicad_pcb`
    DIRNAME=`dirname $FILENAME`
    PLUGIN=`echo "$FILENAME" | sed "s|/kicad/.*||g" | sed "s|.*/||g"`
    echo "$DIRNAME/$BASENAME.png"
    # rm -f "$DIRNAME/$BASENAME-render.png"
    # kicad-cli pcb render --output "$DIRNAME/$BASENAME-render.png" "$FILENAME"
    kicad-cli pcb export svg --fit-page-to-board --layers F.Cu,F.SilkS,Edge.Cuts --output "$DIRNAME/$BASENAME-export.svg" "$FILENAME"
    inkscape "$DIRNAME/$BASENAME-export.svg" --export-type=png --export-filename="$DIRNAME/$BASENAME-export.png" --export-dpi=110
    rm -f "$DIRNAME/$BASENAME-export.svg"
done
