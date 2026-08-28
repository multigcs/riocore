#!/usr/bin/env python3
#
#

import argparse
import json
import os
import re
import sys
import time
import uuid

import hal

DEFAULT_LIMIT = 3600
DEFAULT_WARNING = 75.0
DEFAULT_CRITICAL = 90.0


def times_load(filename):
    tooltimes = {}
    if os.path.isfile(filename):
        with open(filename, "r") as timetable:
            tooltimes = json.loads(timetable.read())
    return tooltimes


def times_save(filename, tooltimes):
    with open(filename, "w") as timetable:
        timetable.write(json.dumps(tooltimes, indent=2))


def tools_load(filename):
    tools = {}
    updated = False
    with open(filename, "r") as tooltable:
        for line in tooltable.read().split("\n"):
            parts = line.strip().split(";", 1)
            if parts[0]:
                comment = ""
                tool_id = ""
                if len(parts) > 1:
                    comment = parts[1]
                    res = re.findall("ID:[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}", comment)
                    if res:
                        tool_id = res[0][3:]
                        comment = comment.replace(res[0], "").strip()
                if not tool_id:
                    tool_id = str(uuid.uuid4()).split("-", 1)[0]
                    updated = True

                cols = parts[0].split()
                tool_data = {
                    "T": 0,  # T: Tool number (unique integer, 0 to 99999)
                    "P": 0,  # P: Pocket number (integer, 1 to 99999; pocket 0 is the spindle)
                    "X": 0.0,  # X: Axis tool offsets (floating-point numbers for length/radius compensation on specific axes)
                    "Y": 0.0,  # Y: Axis tool offsets (floating-point numbers for length/radius compensation on specific axes)
                    "Z": 0.0,  # Z: Axis tool offsets (floating-point numbers for length/radius compensation on specific axes)
                    "A": 0.0,  # A: Axis tool offsets (floating-point numbers for length/radius compensation on specific axes)
                    "B": 0.0,  # B: Axis tool offsets (floating-point numbers for length/radius compensation on specific axes)
                    "C": 0.0,  # C: Axis tool offsets (floating-point numbers for length/radius compensation on specific axes)
                    "U": 0.0,  # U: Axis tool offsets (floating-point numbers for length/radius compensation on specific axes)
                    "V": 0.0,  # V: Axis tool offsets (floating-point numbers for length/radius compensation on specific axes)
                    "W": 0.0,  # W: Axis tool offsets (floating-point numbers for length/radius compensation on specific axes)
                    "D": 0.0,  # D: Tool diameter (absolute floating-point value)
                    "I": 0.0,  # I: Front angle (lathe tools only, floating-point)
                    "J": 0.0,  # J: Back angle (lathe tools only, floating-point)
                    "Q": 0,  # Q: Tool orientation (lathe tools only, integer 0–9).
                    "comment": comment,
                }
                for col in cols:
                    vtype = col[0]
                    value = col[1:]
                    tool_data[vtype] = value
                if tool_data["T"] != 0:
                    tools[tool_id] = tool_data
    if updated:
        tools_save(filename, tools)
    return tools


def tools_save(filename, tools):
    with open(filename, "w") as tooltable:
        for tool_id, tool_data in tools.items():
            line = []
            for key, value in tool_data.items():
                if key == "comment":
                    continue
                line.append(f"{key}{value}")
            line.append(f"; {tool_data['comment']} ID:{tool_id}")
            tooltable.write(" ".join(line))
            tooltable.write("\n")


def main(args):
    tooltimes = times_load(args.timetable)
    tools = tools_load(args.tooltable)
    tool_map = {}

    defaults = {
        "time": 0,
        "limit": DEFAULT_LIMIT,
        "warning": DEFAULT_WARNING,
        "critical": DEFAULT_CRITICAL,
    }

    changed = False
    for tool_id, tool_data in tools.items():
        if tool_id not in tooltimes:
            tooltimes[tool_id] = defaults
            changed = True
        for key, value in defaults.items():
            if key not in tooltimes[tool_id]:
                tooltimes[tool_id][key] = value
                changed = True
        tool_map[int(tool_data["T"])] = tool_id
    if changed:
        times_save(args.timetable, tooltimes)

    if args.debug:
        print("tools:")
        for tool_id, tool_data in tools.items():
            print("   ", tool_id, tool_data)
        print()
        print("tooltimes:")
        for tool_id, tooltime in tooltimes.items():
            print("   ", tool_id, tooltime)
        print()

    h = hal.component("tooltracker")
    h.newpin("time", hal.HAL_FLOAT, hal.HAL_OUT)
    h.newpin("percent", hal.HAL_FLOAT, hal.HAL_OUT)
    h.newpin("limit", hal.HAL_FLOAT, hal.HAL_OUT)
    h.newpin("num", hal.HAL_U32, hal.HAL_OUT)
    h.newpin("warning", hal.HAL_BOOL, hal.HAL_OUT)
    h.newpin("critical", hal.HAL_BOOL, hal.HAL_OUT)

    h["time"] = 0.0
    h["percent"] = 0.0
    h["limit"] = DEFAULT_LIMIT
    h["warning"] = False
    h["critical"] = False
    h["num"] = 0
    h.ready()

    save_timer = 0
    changed = False
    while True:
        ison = hal.get_value("halui.spindle.0.is-on")
        tool_num = hal.get_value("halui.tool.number")
        isrunning = hal.get_value("halui.program.is-running")

        h["num"] = tool_num

        if tool_num not in tool_map:
            if args.debug:
                print("unknown tool:", tool_num)
            h["time"] = 0.0
            h["percent"] = 0.0
            h["warning"] = False
            h["critical"] = False
        else:
            tool_id = tool_map[tool_num]
            if isrunning and ison:
                tooltimes[tool_id]["time"] += 1
                if args.debug:
                    print(ison, tool_num, isrunning, tooltimes[tool_id])
                changed = True
            elif args.debug:
                print("not running")
            h["time"] = tooltimes[tool_id]["time"]
            h["limit"] = tooltimes[tool_id]["limit"]
            h["percent"] = h["time"] * 100.0 / h["limit"]
            if h["percent"] >= tooltimes[tool_id]["critical"]:
                h["critical"] = True
                print(f"tooltracker: CRITICAL: T{tool_num}: {h['percent']}%")
            else:
                h["critical"] = False
            if h["percent"] >= tooltimes[tool_id]["warning"]:
                h["warning"] = True
                print(f"tooltracker: WARNING: T{tool_num}: {h['percent']}%")
            else:
                h["warning"] = False

        if save_timer >= 10 and changed:
            if args.debug:
                print("save")
            changed = False
            times_save(args.timetable, tooltimes)
            save_timer = 0
        else:
            save_timer += 1
        time.sleep(1)


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("-t", "--tooltable", help="tooltable filename", type=str, default="tool.tbl")
        parser.add_argument("-i", "--timetable", help="tooltime filename", type=str, default="tooltime.json")
        parser.add_argument("-d", "--debug", help="print debug output", default=False, action="store_true")
        args = parser.parse_args()
        main(args)
    except KeyboardInterrupt:
        print("exiting tooltracker.py")
        sys.exit(130)
