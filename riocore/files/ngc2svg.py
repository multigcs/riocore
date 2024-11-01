#!/usr/bin/python3
#
#

import argparse
import math
import os
import re

COMMAND = re.compile("(?P<line>\d+) N\.* (?P<type>[A-Z_]+)\((?P<coords>.*)\)")


parser = argparse.ArgumentParser()
parser.add_argument("ngc", help="ngc file", nargs="?", type=str, default=None)
parser.add_argument("--no-g0", help="do not fdraw G0 moves", action="store_true")
args = parser.parse_args()

filename = args.ngc

if filename:
    content = open(filename, "r").read()
else:
    exit(1)

# force adding file end to nc files to prevent rs274 loop
content += "\n\n\nM02\n"
open("/tmp/.tmp.ngc", "w").write(content)


svg_out = []
p = os.popen("rs274 -n 0 -g '/tmp/.tmp.ngc' 2>&1")
output = p.readlines()
r = p.close()
last_pos = ()
pos_min_x = 9999999999
pos_min_y = 9999999999
pos_max_x = 0
pos_max_y = 0
for line in output:
    if "File ended with no" in line:
        print("no file end")
        exit(1)

    result = COMMAND.match(line.strip())
    if result:
        if result["type"] in {"ARC_FEED", "STRAIGHT_FEED", "STRAIGHT_TRAVERSE"}:
            coords = result["coords"].split(",")
            new_x = float(coords[0].strip())
            new_y = float(coords[1].strip())
            new_z = float(coords[2].strip())
            pos_min_x = min(new_x, pos_min_x)
            pos_min_y = min(new_y, pos_min_y)
            pos_max_x = max(new_x, pos_max_x)
            pos_max_y = max(new_y, pos_max_y)

# print(pos_min_x, pos_min_y, pos_max_x, pos_max_y)

width = pos_max_x - pos_min_x
height = pos_max_y - pos_min_y

border = max(height / 4, 2.0)

width += border * 2
height += border * 2


def draw_line(x1, y1, z1, x2, y2, z2, color):
    """
    i_x1 = (x1 - z1) / math.sqrt(2)
    i_y1 = (x1 + 2 * y1 + z1) / math.sqrt(6)

    i_x2 = (x2 - z2) / math.sqrt(2)
    i_y2 = (x2 + 2 * y2 + z2) / math.sqrt(6)

    x1 = i_x1
    y1 = i_y1
    x2 = i_x2
    y2 = i_y2
    """

    svg_out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" style="stroke:{color};stroke-width:0.5" />')


color = "black"
for line in output:
    result = COMMAND.match(line.strip())
    if result:
        if result["type"] in {"ARC_FEED"}:
            coords = result["coords"].split(",")
            new_x = float(coords[0].strip()) - pos_min_x + border
            new_y = height - (float(coords[1].strip()) - pos_min_y) - border
            new_z = float(coords[2].strip())
            if coords[4].strip()[0] == "-":
                direction = "cw"
            else:
                direction = "ccw"
            radius = round(
                math.dist(
                    (float(coords[0].strip()), float(coords[1].strip())),
                    (float(coords[2].strip()), float(coords[3].strip())),
                ),
                4,
            )
            if last_pos:
                last_x, last_y, last_z = last_pos
                if direction == "cw":
                    svg_out.append(f'<g stroke="red" fill="none" style="stroke:{color};stroke-width:0.5"><path d="M {last_x} {last_y} A {radius} {radius} 0 0 1 {new_x} {new_y}" /></g>')
                else:
                    svg_out.append(f'<g stroke="red" fill="none" style="stroke:{color};stroke-width:0.5"><path d="M {new_x} {new_y} A {radius} {radius} 0 0 1 {last_x} {last_y}" /></g>')
            last_pos = (new_x, new_y, new_z)
        elif result["type"] in {"STRAIGHT_FEED", "STRAIGHT_TRAVERSE", "ARC_FEED"}:
            coords = result["coords"].split(",")
            new_x = float(coords[0].strip()) - pos_min_x + border
            new_y = height - (float(coords[1].strip()) - pos_min_y) - border
            new_z = float(coords[2].strip())
            if result["type"] == "ARC_FEED":
                new_z = float(coords[4].strip())

            color = "black"
            if result["type"] == "STRAIGHT_TRAVERSE":
                color = "green"
            if last_pos:
                last_x, last_y, last_z = last_pos
                if result["type"] not in {"STRAIGHT_TRAVERSE"} or not args.no_g0:
                    draw_line(last_x, last_y, last_z, new_x, new_y, new_z, color)

            last_pos = (new_x, new_y, new_z)

lines = "".join(svg_out)
svg_str = f'<svg viewBox="0 0 {width} {height}" style="background-color:white" xmlns="http://www.w3.org/2000/svg">{lines}</svg>'

print(svg_str)
