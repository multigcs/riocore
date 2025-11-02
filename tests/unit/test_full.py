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

        ret = os.system(f"diff -r tests/unit/data/full/{target}/ tests/unit/output/{target}/")
        assert ret == 0

