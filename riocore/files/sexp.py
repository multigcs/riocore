import ast
import math


def loads(sdata):
    ref = []
    inside_q = 0
    inside_key = 0
    skey = {"str": ""}
    keys = []

    def add_ch(ch):
        ch = ch.replace('\\"', '\\\\"')
        if inside_key:
            if not inside_q and ch == " ":
                keys.append(skey["str"] + "'")
                skey["str"] = "'"
            else:
                skey["str"] += ch
        else:
            ref.append(ch)

    for ch in sdata:
        if ch in {"\n", "\t"}:
            continue
        if ch == '"':
            add_ch(ch)
            inside_q = 1 - inside_q
        elif inside_q:
            if ch == "'":
                add_ch("\\")
            add_ch(ch)
        elif ch == "(" and not inside_q:
            if inside_key:
                inside_key = 0
                if skey["str"].strip("'"):
                    keys.append(skey["str"] + "'")
                add_ch(",".join(keys))
                add_ch(",")

            add_ch("[")
            inside_key = 1
            skey["str"] = "'"
            keys = []
        elif ch == ")" and not inside_q:
            if inside_key:
                inside_key = 0
                if skey["str"].strip("'"):
                    keys.append(skey["str"] + "'")
                add_ch(",".join(keys))
            add_ch("],")
        elif ch == " " and not inside_key and not inside_q:
            inside_key = 1
            skey["str"] = "'"
            keys = []
            add_ch(ch)
        else:
            add_ch(ch)
    # print("".join(ref))
    # exit(0)
    lists = ast.literal_eval("".join(ref))
    if lists:
        # import json
        # print(json.dumps(lists[0], indent=4))
        return lists[0]


def dumps(lists):
    def lp(entry, result, prefix=""):
        if isinstance(entry, list):
            # bad hack for better debug-diffs
            if len(result) > 3 and "xy" in result[-4]:
                result.append(f" ({entry[0]}")
            else:
                result.append(f"\n{prefix}({entry[0]}")
            for part in entry[1:]:
                lp(part, result, prefix=f"{prefix}\t")
            if result[-1][-1] == ")":
                result.append(f"\n{prefix})")
            else:
                result.append(")")
        else:
            result.append(f" {entry.strip()}")

    result = []
    lp(lists, result)
    return "".join(result).strip()


def minmax_polygons(dimentions, entry):
    for sn, sentry in enumerate(entry[1:], 1):
        if sentry[0] in {"filled_polygon", "polygon"}:
            for ptsn, pts in enumerate(get_types(sentry[1:], {"pts"}), 1):
                for pn, part in enumerate(pts[1:], 1):
                    if part and part[0] == "xy":
                        px = float(part[1])
                        py = float(part[2])
                        dimentions["start_x"] = min(dimentions["start_x"], px)
                        dimentions["start_y"] = min(dimentions["start_y"], py)
                        dimentions["end_x"] = max(dimentions["end_x"], px)
                        dimentions["end_y"] = max(dimentions["end_y"], py)
    return dimentions


def pcb_dimentions(pcb_data):
    dimentions = {}
    dimentions["start_x"] = 100000
    dimentions["start_y"] = 100000
    dimentions["end_x"] = 0
    dimentions["end_y"] = 0
    dimentions["width"] = 0
    dimentions["height"] = 0
    for entry in pcb_data:
        if entry[0] in {"footprint", "segment", "gr_rect", "via", "zone"}:
            minmax_polygons(dimentions, entry)
            for sentry in entry[1:]:
                if sentry[0] in {"zone"}:
                    minmax_polygons(dimentions, sentry)
                elif sentry[0] in {"at", "start", "end"}:
                    px = float(sentry[1])
                    py = float(sentry[2])
                    dimentions["start_x"] = min(dimentions["start_x"], px)
                    dimentions["start_y"] = min(dimentions["start_y"], py)
                    dimentions["end_x"] = max(dimentions["end_x"], px)
                    dimentions["end_y"] = max(dimentions["end_y"], py)

    dimentions["width"] = dimentions["end_x"] - dimentions["start_x"]
    dimentions["height"] = dimentions["end_y"] - dimentions["start_y"]
    dimentions["center_x"] = dimentions["width"] / 2
    dimentions["center_y"] = dimentions["height"] / 2
    return dimentions


def pcb_netnames(pcb_data):
    netnames = []
    for entry in pcb_data:
        if entry[0] == "footprint":
            for sentry in entry[1:]:
                for ssentry in sentry[1:]:
                    if ssentry[0] == "net" and len(ssentry) == 3:
                        netname = ssentry[2].strip('"')
                        if netname and netname not in netnames:
                            netnames.append(netname)
    return netnames


def rotate_point(origin, point, angle):
    origin_x, origin_y = origin
    point_x, point_y = point
    radians = math.radians(-angle)
    new_x = origin_x + math.cos(radians) * (point_x - origin_x) - math.sin(radians) * (point_y - origin_y)
    new_y = origin_y + math.sin(radians) * (point_x - origin_x) + math.cos(radians) * (point_y - origin_y)
    return (new_x, new_y)


def get_types(data, types):
    entrys = []
    for entry in data:
        if entry and entry[0] in types:
            entrys.append(entry)
    return entrys


def get_property(data, ptype):
    entrys = []
    if isinstance(ptype, str):
        ptype = {ptype}
    for entry in data:
        if entry[0] == "property" and entry[1].strip('"') in ptype:
            entrys.append(entry)
    return entrys
