#!/usr/bin/env python3
#
#

import pytest
import os.path
import shutil

from riocore.generator.LinuxCNC import LinuxCNC


class fake_project:
    config = {
        "jdata": {},
        "output_path": "tests/unit/output/",
    }
    plugin_instances = []
    networks = {}


@pytest.mark.parametrize(
    "networks, setps, expected",
    (
        (
            {
                "multi-output1": {
                    "in": ["multi-output1.in"],
                    "out": ["multi-output1.out1", "multi-output1.out2"],
                },
            },
            {},
            (
                [
                    "",
                    "# multi-output1",
                    "net multi-output1 <= multi-output1.in",
                    "net multi-output1 => multi-output1.out1",
                    "net multi-output1 => multi-output1.out2",
                    "",
                    "# setp",
                ],
                [],
            ),
        ),
        (
            {
                "multi-input1": {
                    "in": ["multi-input1.in1", "multi-input1.in2"],
                    "out": ["multi-input1.out1"],
                    "options": {"multi-input1.out1": {"type": "OR"}},
                },
            },
            {},
            (
                [
                    "",
                    "# multi-input1",
                    "loadrt logic names=logic.multi-input1 personality=0x202",
                    "addf logic.multi-input1 servo-thread",
                    "net multi-input1-in-00 <= multi-input1.in1",
                    "net multi-input1-in-00 => logic.multi-input1.in-00",
                    "net multi-input1-in-01 <= multi-input1.in2",
                    "net multi-input1-in-01 => logic.multi-input1.in-01",
                    "net multi-input1_or <= logic.multi-input1.or",
                    "net multi-input1_or => multi-input1.out1",
                    "",
                    "# setp",
                ],
                [],
            ),
        ),
        (
            {
                "multi-input2": {
                    "in": ["multi-input1.in1", "multi-input1.in2"],
                    "out": ["multi-input1.out1", "multi-input1.out2"],
                    "options": {"multi-input1.out1": {"type": "OR"}, "multi-input1.out2": {"type": "AND"}},
                },
            },
            {},
            (
                [
                    "",
                    "# multi-input2",
                    "loadrt logic names=logic.multi-input2 personality=0x302",
                    "addf logic.multi-input2 servo-thread",
                    "net multi-input2-in-00 <= multi-input1.in1",
                    "net multi-input2-in-00 => logic.multi-input2.in-00",
                    "net multi-input2-in-01 <= multi-input1.in2",
                    "net multi-input2-in-01 => logic.multi-input2.in-01",
                    "net multi-input2_or <= logic.multi-input2.or",
                    "net multi-input2_and <= logic.multi-input2.and",
                    "net multi-input2_or => multi-input1.out1",
                    "net multi-input2_and => multi-input1.out2",
                    "",
                    "# setp",
                ],
                [],
            ),
        ),
    ),
)
def test_LinuxCNC_generate_networks(networks, setps, expected):
    project = fake_project
    lcnc = LinuxCNC(project)

    pre, post = lcnc.generate_networks(networks, setps)
    print(pre)
    print(post)

    assert sorted(pre) == sorted(expected[0])
    assert sorted(post) == sorted(expected[1])


def test_LinuxCNC_hal_net_add():
    project = fake_project
    lcnc = LinuxCNC(project)

    lcnc.hal_net_add("net1.in1", "net1.out1")
    lcnc.hal_net_add("net1.in1", "net1.out2")
    lcnc.hal_net_add("net0.in1", "net1.in1")

    for name, net in lcnc.networks.items():
        print(name, net["in"], net["out"])

    pre, post = lcnc.generate_networks(lcnc.networks, {})
    for line in pre:
        print(line)

    print(lcnc.networks)

    assert lcnc.networks == {
        "net1-in1": {"in": ["net0.in1"], "out": ["net1.out1", "net1.out2", "net1.in1"], "type": "OR", "options": {"net1.out1": {"type": "OR"}, "net1.out2": {"type": "OR"}, "net1.in1": {"type": "OR"}}}
    }
