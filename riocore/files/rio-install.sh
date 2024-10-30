#!/bin/bash
#
# install script for riocore
#
#  wget -q -O- https://raw.githubusercontent.com/multigcs/riocore/refs/heads/dev/riocore/files/rio-install.sh | bash
#


UNAME_M="`uname -m`"
APT_PACKAGES="wget git tar python3 python3-pip python3-yaml python3-graphviz python3-pyqtgraph python3-pyqt5 python3-pyqt5.qtsvg python3-stdeb dh-python python3-pyqt5 python3-pyqt5.qtsvg make"
DF_B=`df -m ./ | tail -n 1 | awk '{print $4}'`

# checking disk-space
if test "$DF_B" -lt "2500"
then
    echo "## you need at least 2.5GB diskspace"
    df -h .
    exit 1
fi

# checking installed tools
if ! which whiptail >/dev/null 2>&1
then
    echo "## whiptail not found, plese install with: sudo apt-get install whiptail" >&2
    exit 1
fi

# install apt packages if needed
INSTALLED=`dpkg -l | grep "^ii "`
FLAG=1
for APT_PACKAGE in $APT_PACKAGES
do
    if ! echo "$INSTALLED" | grep -s -q "\<$APT_PACKAGE\>"
    then
        echo "## missing apt package: $APT_PACKAGE"
        FLAG=0
    fi
done

if test "$FLAG" = "0"
then
    if whiptail --yesno "Should i install the needed apt packages like git, python, ... ?" 10 40
    then
        echo "## installing.."
        sudo apt-get install $APT_PACKAGES
        echo "## installing....done"
    fi
fi

# install linuxcnc packages
if echo "$INSTALLED" | grep -s -q "\<linuxcnc-uspace-dev\>"
then
    echo "## linuxcnc allready installed"
else
    if whiptail --yesno "Should i install the linuxcnc apt packages ?" 10 40
    then
        echo "## installing.."
        sudo apt-get install linuxcnc-uspace linuxcnc-uspace-dev
        echo "## installing....done"
    fi
fi

# clone riocore if not exist
if test -e riocore/.git
then
    echo "## folder riocore allready exists" >&2
    cd riocore
elif test -e ./.git && test -e ./riocore/__init__.py
then
    echo "## folder riocore allready exists" >&2
    cd .
else
    # cloning riocore git
    if ! git clone https://github.com/multigcs/riocore.git
    then
        echo "## error cloning riocore git repository" >&2
        exit 1
    fi
    cd riocore
fi

# check if we are in the riocore folder
if ! test -e ./riocore/__init__.py
then
    echo "riocore folder not found" >&2
    exit 1
fi

# installing rio halcomponent
if which halcompile >/dev/null 2>&1
then
    echo "## using halcompile to install the rio.c component.."
    sudo halcompile --install riocore/files/rio.c
    echo "## using halcompile to install the rio.c component....done"
fi

# installing toolchain: icestorm (yosys/nextpnr)
if which nextpnr-himbaechel >/dev/null 2>&1
then
    echo "## icestorm toolchain allready installed"
else
    if whiptail --yesno "Should i install the oss-cad-suite (icestorm-toolchain / ICE40/ECP5 Boards) ?" 10 40
    then
        if test "$UNAME_M" = "x86_64"
        then
            echo "## installing.."
            mkdir -p toolchains
            (
                cd toolchains
                echo "## getting oss-cad-suite.."
                wget https://github.com/YosysHQ/oss-cad-suite-build/releases/download/2024-09-03/oss-cad-suite-linux-x64-20240903.tgz
                echo "## getting oss-cad-suite....done"
                echo -n "## extracting oss-cad-suite.."
                tar xzpf oss-cad-suite-linux-x64-20240903.tgz && echo "..done"
                rm -rf oss-cad-suite-linux-x64-20240903.tgz
            )
            echo "## installing....done"
        elif test "$UNAME_M" = "aarch64"
        then
            echo "## installing.."
            mkdir -p toolchains
            (
                cd toolchains
                echo "## getting oss-cad-suite.."
                wget https://github.com/YosysHQ/oss-cad-suite-build/releases/download/2024-09-03/oss-cad-suite-linux-arm64-20240903.tgz
                echo "## getting oss-cad-suite....done"
                echo -n "## extracting oss-cad-suite.."
                tar xzpf oss-cad-suite-linux-arm64-20240903.tgz && echo "..done"
                rm -rf oss-cad-suite-linux-arm64-20240903.tgz
            )
            echo "## installing....done"
        else
            echo "## this mashine type is not supported by the installer script: $UNAME_M" >&2
        fi
    fi
    if test -e toolchains/oss-cad-suite/bin/
    then
        echo "## updating PATH in ~/.bashrc..."
        RPATH=`realpath toolchains/oss-cad-suite/bin/`
        echo "export PATH=\$PATH:$RPATH" >> ~/.bashrc
        export PATH=$PATH:$RPATH
        echo "## ...done"
    else
        echo "## no icestorm toolchain found"
    fi
fi

# installing toolchain: gowin
if which gw_ide >/dev/null 2>&1
then
    echo "## gowin toolchain allready installed"
else
    if whiptail --yesno "Should i install the gowin-eda (gowin-toolchain / Tangnano Boards) ?" 10 40
    then
        if test "$UNAME_M" = "x86_64"
        then
            echo "## installing.."
            mkdir -p toolchains/gowin
            (
                cd toolchains/gowin
                echo "## getting oss-cad-suite.."
                wget "https://cdn.gowinsemi.com.cn/Gowin_V1.9.9.03_Education_linux.tar.gz"
                echo "## getting oss-cad-suite....done"
                echo -n "## extracting oss-cad-suite.."
                tar xzpf Gowin_V1.9.9.03_Education_linux.tar.gz && echo "..done"
                rm -rf Gowin_V1.9.9.03_Education_linux.tar.gz
            )
            echo "## installing....done"
        else
            echo "## this mashine type is not supported by the installer script: $UNAME_M" >&2
        fi
    fi
    if test -e toolchains/gowin/IDE/bin/
    then
        echo "## updating PATH in ~/.bashrc..."
        RPATH=`realpath toolchains/gowin/IDE/bin/`
        echo "export PATH=\$PATH:$RPATH" >> ~/.bashrc
        export PATH=$PATH:$RPATH
        echo "## ...done"
    else
        echo "## no gowin toolchain found"
    fi
    if which openfpgaloader >/dev/null 2>&1
    then
        if whiptail --yesno "Should i install openfpgaloader via apt ?" 10 40
        then
            echo "## installing.."
            sudo apt-get install openfpgaloader
            echo "## installing....done"
        fi
    fi
fi

# done
echo "##"
echo "## to start setup tool, go into the riocore folder and type:"
echo "##   export PATH=$PATH"
echo "##   bin/rio-setup"
echo "##"

