#!/bin/bash
#
#

PWD="`pwd`"
SYSTEM="arm64"
if test "`uname -m`" = "x86_64"
then
	SYSTEM="x64"
fi

TEMPFILE="`mktemp /tmp/rioXXXXXX.tmp`"
TC_ICESTORM=""
TC_GOWIN=""

doexit() {
	rm -rf $TEMPFILE
	exit $1
}

cd ~ || doexit 1


if test "$SYSTEM" = "x64"
then
	if ! whiptail --checklist "what do you want to install ?" 20 60 12 \
	apt "install dependencies" ON \
	rio "git clone riocore" ON \
	icestorm "install OSS-Cad-Suite" ON \
	gowin "install Gowin Toolchain" ON \
	2> $TEMPFILE
	then
		rm -rf $TEMPFILE
		doexit 0
	fi
else
	if ! whiptail --checklist "what do you want to install ?" 20 60 12 \
	apt "install dependencies" ON \
	rio "git clone riocore" ON \
	icestorm "install OSS-Cad-Suite" ON \
	2> $TEMPFILE
	then
		rm -rf $TEMPFILE
		doexit 0
	fi
fi



if grep -s -q '"apt"' in $TEMPFILE
then
	echo "installing dependencies"
	sudo apt-get update || doexit 1
	sudo apt-get -y install git python3 python3-pip python3-yaml python3-graphviz python3-pyqtgraph python3-pyqt5 python3-pyqt5.qtsvg python3-lxml || doexit 1
fi

if grep -s -q '"rio"' in $TEMPFILE
then
	if ! test -d riocore
	then
		echo "installing riocore"
		git clone https://github.com/multigcs/riocore.git || doexit 1
	else
		echo "riocore already installed"
	fi
fi

if grep -s -q '"icestorm"' in $TEMPFILE
then
	if ! test -d riocore/toolchains/oss-cad-suite
	then
		echo "installing icestorm"
		(
			mkdir -p riocore/toolchains/
			cd riocore/toolchains || doexit 1
			wget "https://github.com/YosysHQ/oss-cad-suite-build/releases/download/2024-09-10/oss-cad-suite-linux-$SYSTEM-20240910.tgz" || doexit 1
			tar xzvpf oss-cad-suite-linux-$SYSTEM-20240910.tgz || doexit 1
			rm -rf oss-cad-suite-linux-$SYSTEM-20240910.tgz
		)
	else
		echo "icestorm already installed"
	fi
	TC_ICESTORM="$PWD/riocore/toolchains/oss-cad-suite"
fi

if grep -s -q '"gowin"' in $TEMPFILE
then
	if ! test -d riocore/toolchains/gowin/IDE
	then
		echo "installing gowin"
		(
			mkdir -p riocore/toolchains/gowin
			cd riocore/toolchains/gowin || doexit 1
			wget "https://cdn.gowinsemi.com.cn/Gowin_V1.9.10.03_Education_linux.tar.gz" || doexit 1
			tar xzvpf Gowin_V1.9.10.03_Education_linux.tar.gz || doexit 1
			rm -rf Gowin_V1.9.10.03_Education_linux.tar.gz
		)
	else
		echo "gowin already installed"
	fi
	TC_GOWIN="$PWD/riocore/toolchains/gowin/IDE"
fi

if test -e riocore/riocore && test "$TC_ICESTORM$TC_GOWIN" != ""
then
	echo "adding toolchains to riocore/riocore/toolchains.json"
	for TC in $TC_ICESTORM $TC_GOWIN
	do
		echo "    $TC"
	done
	cat <<EOF > riocore/riocore/toolchains.json 
{
    "icestorm": "$TC_ICESTORM",
    "gowin": "$TC_GOWIN",
    "diamond": "",
    "vivado": "",
    "quartus": "",
    "ise": ""
}
EOF
fi

echo ""
echo "####################################################################"
echo ""
echo "# command examples:"
echo ""
echo "    cd ~/riocore/"
echo ""
echo "  # create new setup:"
echo "    bin/rio-setup"
echo ""
echo "  # generate, build and flash the Tangbob config"
echo "    bin/rio-generator -b -f riocore/configs/Tangbob/config.json"
echo ""
echo "  # generate and start linuxcnc for the Tangbob config"
echo "    bin/rio-generator -s riocore/configs/Tangbob/config.json"
echo ""
echo "####################################################################"
echo ""

