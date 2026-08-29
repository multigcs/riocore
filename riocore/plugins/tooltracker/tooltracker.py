#!/usr/bin/env python3
#
#

import argparse
import os
import sys
import time

import hal

from python.tooltable import tools_load, tools_save


def main(args):
    tools = tools_load(args.tooltable)
    tools_lastmod = os.path.getmtime(args.tooltable)

    if args.debug:
        print("tools:")
        for tool_id, tool_data in tools.items():
            print("   ", tool_id, tool_data)
        print()

    h = hal.component("tooltracker")
    h.newpin("tool", hal.HAL_U32, hal.HAL_IN)
    h.newpin("running", hal.HAL_BIT, hal.HAL_IN)
    h.newpin("timer", hal.HAL_FLOAT, hal.HAL_OUT)
    h.newpin("warning_level", hal.HAL_FLOAT, hal.HAL_OUT)
    h.newpin("critical_level", hal.HAL_FLOAT, hal.HAL_OUT)
    h.newpin("warning_flag", hal.HAL_BIT, hal.HAL_OUT)
    h.newpin("critical_flag", hal.HAL_BIT, hal.HAL_OUT)
    h.newpin("percent", hal.HAL_FLOAT, hal.HAL_OUT)

    h["timer"] = 0.0
    h["warning_level"] = 0.0
    h["critical_level"] = 0.0
    h["warning_flag"] = False
    h["critical_flag"] = False
    h["percent"] = 0.0
    h.ready()

    save_timer = 0
    changed = False
    while True:
        if tools_lastmod < os.path.getmtime(args.tooltable):
            tools = tools_load(args.tooltable)
            tools_lastmod = os.path.getmtime(args.tooltable)
            print("reload...")

        tool_num = h["tool"]
        if tool_num not in tools:
            if args.debug:
                print("unknown tool:", tool_num)
            h["timer"] = 0.0
            h["percent"] = 0.0
            h["warning_level"] = 0.0
            h["critical_level"] = 0.0
            h["warning_flag"] = False
            h["critical_flag"] = False
        else:
            h["warning_level"] = tools[tool_num]["warning"]
            h["critical_level"] = tools[tool_num]["critical"]
            if h["running"]:
                tools[tool_num]["timer"] += 1
                if args.debug:
                    print(tool_num, tools[tool_num])
                changed = True
            elif args.debug:
                print("not running")
            h["timer"] = tools[tool_num]["timer"]
            h["percent"] = h["timer"] * 100.0 / tools[tool_num]["critical"]
            if h["timer"] >= tools[tool_num]["critical"]:
                h["critical_flag"] = True
                print(f"tooltracker: CRITICAL: T{tool_num}: {h['percent']}%")
            else:
                h["critical_flag"] = False

            if h["timer"] >= tools[tool_num]["warning"]:
                h["warning_flag"] = True
                print(f"tooltracker: WARNING: T{tool_num}: {h['percent']}%")
            else:
                h["warning_flag"] = False

        if save_timer >= 10 and changed:
            if args.debug:
                print("save")
            changed = False
            tools_save(args.tooltable, tools)
            tools_lastmod = os.path.getmtime(args.tooltable)
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
