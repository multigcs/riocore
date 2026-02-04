#!/bin/bash
#
#

FOLDER="$1"

echo "supported = {" > riocore/plugins/ethercat/lcec_devices.py
grep "{\"E[A-Z][0-9][0-9][0-9][0-9]\", LCEC_\|BECKHOFF_[A-Z]*_DEVICE(\"" $FOLDER/lcec_*.c  | sed "s/.*{\"\|.*BECKHOFF_[A-Z]*_DEVICE(\"//g" | cut -d'"' -f1 | sort -u | awk '{print "    \""$1"\","}' >> riocore/plugins/ethercat/lcec_devices.py
echo "}" >> riocore/plugins/ethercat/lcec_devices.py
