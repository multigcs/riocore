#!/usr/bin/env python3
#
#

import glob
import os
import pytest
import riocore
import os.path
import shutil


@pytest.mark.parametrize(
    'config',
    glob.glob("tests/unit/data/full/*.json"),
)

def test_generator(config):
    target = config.split("/")[-1].replace(".json", "")
    if os.path.exists("tests/unit/output"):
        shutil.rmtree("tests/unit/output")
    os.system(f"bin/rio-generator {config} tests/unit/output")
    if not os.path.exists(f"tests/unit/output/{target}/LinuxCNC/rio.hal"):
        assert False

    if not os.path.exists(f"tests/unit/data/full/{target}"):
        shutil.copytree(f"tests/unit/output/{target}", f"tests/unit/data/full/{target}")

    # cleanup files
    for path in (
        f"{target}/Gateware/*/Makefile",
        f"{target}/Gateware/board0/pll.v",
        f"{target}/Gateware/board0/pll_bb.v",
        f"{target}/Gateware/board0/pll.qip",
        f"{target}/DOC",
        f"{target}/LinuxCNC/subroutines",
        f"{target}/LinuxCNC/mcodes",
    ):
        os.system(f'rm -rf tests/unit/data/full/{path}')
        os.system(f'rm -rf tests/unit/output/{path}')

    os.system(f'test -e tests/unit/data/full/{target}/Firmware/*/Makefile && sed -i "s|TOOLCHAIN_PATH .*| TOOLCHAIN_PATH|g" tests/unit/data/full/{target}/Firmware/*/Makefile')
    os.system(f'test -e tests/unit/output/{target}/Firmware/*/Makefile && sed -i "s|TOOLCHAIN_PATH .*| TOOLCHAIN_PATH|g" tests/unit/output/{target}/Firmware/*/Makefile')

    ret = os.system(f"diff -r tests/unit/data/full/{target}/ tests/unit/output/{target}/")
    assert ret == 0

