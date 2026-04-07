#!/bin/bash
#
#

mkdir -p riocore/files/images/guis
for GUI in `bin/rio-generator -G list riocore/configs/Tangoboard/config-w5500.json | cut -d" " -f1`
do
    if ! test -e riocore/files/images/guis/$GUI.png
    then
        rm -rf Output/
        bin/rio-generator -s -G $GUI riocore/configs/Tangoboard/config-w5500.json &
        sleep 10
        WID=`xdotool getactivewindow`
        import -window $WID /tmp/gui-$GUI.png
        convert -scale 400x /tmp/gui-$GUI.png riocore/files/images/guis/$GUI.png
        xkill -id $WID
        sleep 3
        killall -9 linuxcncsvr milltask /usr/bin/rtapi_app halui /usr/bin/qtvcp /usr/bin/wish8.6
   fi
done

geeqie riocore/files/images/guis/





