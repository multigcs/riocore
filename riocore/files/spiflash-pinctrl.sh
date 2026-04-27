#!/bin/bash
#
# write Flash from raspberry over SPI
# please use the latest flashrom from: https://github.com/flashrom/flashrom.git
#
#

# if ! test -e /usr/src/flashrom
# then
#    (cd /usr/src && git clone https://github.com/flashrom/flashrom.git && cd flashrom && make)
# fi


SPIDEV="/dev/spidev0.1"
SPISPEED="20000"
SPISELPIN_FLASH="7"
RESETPIN="25"

BITFILE=$1
if test "$BITFILE" = ""
then
    echo "$0 BITFILE [SIZE]"
    exit 1
fi
if ! test -e "$BITFILE"
then
	echo "ERROR: bitfile not found: $BITFILE"
	exit 1
fi

FLASHSIZE="$2"

echo "bitfile: $BITFILE ..."
echo "  reload drivers / set FPGA into reset mode"

# set all spi selects to SPI0_CE...
pinctrl set 7 a0
pinctrl set 8 a0

sudo rmmod spidev 2>/dev/null
sudo rmmod spi_bcm2835 2>/dev/null
sudo modprobe spi_bcm2835 2>/dev/null
sudo modprobe spidev 2>/dev/null

# set reset pin to output low
pinctrl set $RESETPIN op dl
sleep .2

if test "$FLASHSIZE" = ""
then
	BITSIZE=`du -b $BITFILE| awk '{print $1}'`
	FLASHSIZE=`flashrom -p linux_spi:dev=$SPIDEV,spispeed=$SPISPEED --flash-size | tail -n1 | grep "^[1-9]"`
	if test "$FLASHSIZE" -lt "$BITSIZE"
	then
		echo "   ERROR: bitfile is to big for the flash: $FLASHSIZE > $BITSIZE"
		exit 1
	fi 
fi

echo "  fill bitfile with zeros to reach flashsize: $FLASHSIZE"
if ! dd if=/dev/zero of=/tmp/_flash.bin  bs=$FLASHSIZE count=1 2> /dev/null
then
	echo "   ERROR: dd can not read/write: dd if=/dev/zero of=/tmp/_flash.bin  bs=$FLASHSIZE count=1"
	exit 1
fi
if ! dd if=$BITFILE conv=notrunc of=/tmp/_flash.bin 2> /dev/null
then
	echo "   ERROR: dd can not read/write: dd if=$BITFILE conv=notrunc of=/tmp/_flash.bin"
	exit 1
fi

echo "  write to flash"
rm -rf /tmp/_flash.log
if ! flashrom -p linux_spi:dev=$SPIDEV,spispeed=$SPISPEED -w /tmp/_flash.bin > /tmp/_flash.log
then
	echo "   ERROR: flashrom: `cat /tmp/_flash.log`"
	echo "   retry.."
	rm -rf /tmp/_flash.log
	if ! flashrom -p linux_spi:dev=$SPIDEV,spispeed=$SPISPEED -w /tmp/_flash.bin > /tmp/_flash.log
	then
		echo "   ERROR: flashrom: `cat /tmp/_flash.log`"
	fi
fi

echo "  unload drivers / reset FPGA"
sudo rmmod spidev 2>/dev/null
sudo rmmod spi_bcm2835 2>/dev/null

# release spi pins
pinctrl set 7 ip pu
pinctrl set 8 ip pu
pinctrl set 9 ip
pinctrl set 10 ip
pinctrl set 11 ip

# set reset pin to input pullup -> hi
pinctrl set $RESETPIN op dl
sleep .2
pinctrl set $RESETPIN op dh
sleep 2

# set all spi selects to SPI0_CE...
pinctrl set 7 a0
pinctrl set 8 a0

echo "...done"
