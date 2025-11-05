#!/usr/bin/env python3
#
#

import glob
import os
import pytest
import riocore
import os.path
import shutil


def test_generator():

    for config in glob.glob("tests/unit/data/full/*.json"):
        target = config.split("/")[-1].replace(".json", "")

        if os.path.exists("tests/unit/output"):
            shutil.rmtree("tests/unit/output")

        os.system(f"bin/rio-generator {config} tests/unit/output")

        if not os.path.exists(f"tests/unit/output/{target}/LinuxCNC/rio.hal"):
            assert False


        if not os.path.exists(f"tests/unit/data/full/{target}"):
            shutil.copytree(f"tests/unit/output/{target}", f"tests/unit/data/full/{target}")

        # cleanup files
        os.system(f'test -e tests/unit/data/full/{target}/Firmware/*/Makefile && sed -i "s|TOOLCHAIN_PATH .*| TOOLCHAIN_PATH|g" tests/unit/data/full/{target}/Firmware/*/Makefile')
        os.system(f'test -e tests/unit/output/{target}/Firmware/*/Makefile && sed -i "s|TOOLCHAIN_PATH .*| TOOLCHAIN_PATH|g" tests/unit/output/{target}/Firmware/*/Makefile')
        os.system(f'rm -rf tests/unit/data/full/{target}/Gateware/Makefile')
        os.system(f'rm -rf tests/unit/output/{target}/Gateware/Makefile')

        ret = os.system(f"diff -r tests/unit/data/full/{target}/ tests/unit/output/{target}/")
        assert ret == 0

