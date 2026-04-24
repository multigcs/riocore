#!/usr/bin/env python3
#
#

import copy
import json
import os
import sys
import uuid

import sexp

references = []


def update_reference(reference):
    if reference not in references:
        references.append(reference)
        return reference
    prefix = reference.strip("0123456789")
    num = 0
    reference = f"{prefix}{num}"
    while reference in references:
        num += 1
        reference = f"{prefix}{num}"
    references.append(reference)
    return reference


setup = json.loads(open(sys.argv[1], "r").read())
project_name = setup["name"]

# check old files
old_sch = None
if os.path.isfile(f"{project_name}.kicad_sch"):
    old_sch = sexp.loads(open(f"{project_name}.kicad_sch", "r").read())
old_pcb = None
if os.path.isfile(f"{project_name}.kicad_pcb"):
    old_pcb = sexp.loads(open(f"{project_name}.kicad_pcb", "r").read())


# set module uuids and sheets
partnumbers = {}
for name, settings in setup["modules"].items():
    settings["spins"] = {}
    settings["sheets"] = {}
    settings["ref_mapping"] = {}
    settings["units"] = {}
    settings["iname"] = {}
    settings["pos"] = {}
    settings["rotate"] = {}

    # load files
    settings["module_sch"] = sexp.loads(open(f"{settings['path']}/{name}/{name}.kicad_sch", "r").read())
    settings["module_pcb"] = sexp.loads(open(f"{settings['path']}/{name}/{name}.kicad_pcb", "r").read())

    # check uuid
    suuid_prefix = None
    for entry in settings["module_sch"]:
        if entry[0] == "uuid":
            suuid_prefix = entry[1].strip('"')[:-3]
            break
    if suuid_prefix is None:
        print("ERROR")
        exit(1)

    num = 0
    for iname, idata in settings["instances"].items():
        suuid = f"{suuid_prefix}{num:03d}"
        settings["sheets"][num] = suuid
        settings["ref_mapping"][num] = {}
        settings["iname"][num] = iname
        settings["pos"][num] = idata.get("pos")
        settings["rotate"][num] = idata.get("rotate")
        num += 1

# SCH
uuid_exsits_sch = []
if old_sch:
    sch_new = copy.deepcopy(old_sch)
    for entry in sch_new:
        if not entry:
            continue
        if entry[0] == "uuid":
            rootid = entry[1].strip('"')
        for sentry in entry[1:]:
            if sentry[0] == "uuid":
                uuid_exsits_sch.append(sentry[1].strip('"'))
            # elif sentry[0] == "property" and sentry[1].strip('"') == "Reference":
            # reference = sentry[2].strip('"')
            # reference_new = update_reference(reference)
            # sentry[2] = f'"{reference_new}"'
else:
    rootid = str(uuid.uuid4())
    template_sch_str = f"""(kicad_sch
        (version 20250114)
        (generator "eeschema")
        (generator_version "9.0")
        (uuid "{rootid}")
        (paper "A4")
    )
    """
    sch_new = sexp.loads(template_sch_str)

lib_symbols = False
for name, settings in setup["modules"].items():
    settings["schema_data"] = []
    muuid = None
    for entry in sexp.get_types(settings["module_sch"], {"lib_symbols"}):
        lib_symbols = True
        break
    for entry in sexp.get_types(settings["module_sch"], {"uuid"}):
        muuid = entry[1].strip('"')
    for entry in sexp.get_types(settings["module_sch"], {"hierarchical_label"}):
        pin_name = entry[1].strip('"')
        settings["spins"][pin_name] = "input"

    for entry in settings["module_sch"]:
        # find symbol - modify instances / reference
        reference = None
        for sentry in sexp.get_property(entry[1:], "Reference"):
            # update reference mapping
            reference = sentry[2].strip('"')
            for num, suuid in settings["sheets"].items():
                if reference not in settings["ref_mapping"][num]:
                    reference_new = update_reference(reference)
                    settings["ref_mapping"][num][reference] = reference_new

    for entry in copy.deepcopy(settings["module_sch"]):
        # find symbol - modify instances / reference
        reference = None
        for sentry in sexp.get_property(entry[1:], "Reference"):
            reference = sentry[2].strip('"')

        puuid = None
        for sentry in entry[1:]:
            if sentry[0] == "uuid":
                puuid = sentry[1].strip('"')
            elif sentry[0] == "instances":
                unit = 1
                for ssentry in sentry[1:]:
                    for sssentry in ssentry[1:]:
                        if sssentry[0] == "path" and sssentry[1].strip('"/') == muuid:
                            for ssssentry in sssentry[1:]:
                                if ssssentry[0] == "unit":
                                    unit = ssssentry[1]
                sentry.append(["project", f'"{project_name}"'])
                for num, suuid in settings["sheets"].items():
                    reference_new = settings["ref_mapping"][num].get(reference, reference)
                    if settings.get("main"):
                        ipath = f'"/{rootid}"'
                    else:
                        ipath = f'"/{rootid}/{suuid}"'
                    sentry[-1].append(
                        [
                            "path",
                            ipath,
                            ["reference", f'"{reference_new}"'],
                            ["unit", f"{unit}"],
                        ]
                    )
        if not settings.get("main"):
            settings["schema_data"].append(entry)
        elif entry[0] in {"lib_symbols", "global_label", "symbol", "wire", "junction"}:
            suuid = None
            for sentry in entry[1:]:
                if sentry[0] == "uuid":
                    suuid = sentry[1].strip('"')
                elif sentry[0] == "instances":
                    for ssentry in sentry[1:]:
                        for sssentry in ssentry[1:]:
                            if sssentry[0] == "path" and sssentry[1].strip('"/') == muuid:
                                for ssssentry in sssentry[1:]:
                                    if ssssentry[0] == "unit":
                                        units = ssssentry[1]
                                        settings["units"][suuid] = units

            if suuid not in uuid_exsits_sch:
                sch_new.append(entry)
                uuid_exsits_sch.append(suuid)

for name, settings in setup["modules"].items():
    if not settings.get("main"):
        open(f"{name}.kicad_sch", "w").write(sexp.dumps(settings["schema_data"]))

if not lib_symbols:
    sch_new.append(["lib_symbols"])

pcb_new = [
    "kicad_pcb",
    ["version", "20241229"],
    ["generator", '"pcbnew"'],
    ["generator_version", '"9.0"'],
    ["general", ["thickness", "1.6"], ["legacy_teardrops", "no"]],
    ["paper", '"A4"'],
    [
        "layers",
        ["0", '"F.Cu"', "signal"],
        ["2", '"B.Cu"', "signal"],
        ["9", '"F.Adhes"', "user", '"F.Adhesive"'],
        ["11", '"B.Adhes"', "user", '"B.Adhesive"'],
        ["13", '"F.Paste"', "user"],
        ["15", '"B.Paste"', "user"],
        ["5", '"F.SilkS"', "user", '"F.Silkscreen"'],
        ["7", '"B.SilkS"', "user", '"B.Silkscreen"'],
        ["1", '"F.Mask"', "user"],
        ["3", '"B.Mask"', "user"],
        ["17", '"Dwgs.User"', "user", '"User.Drawings"'],
        ["19", '"Cmts.User"', "user", '"User.Comments"'],
        ["21", '"Eco1.User"', "user", '"User.Eco1"'],
        ["23", '"Eco2.User"', "user", '"User.Eco2"'],
        ["25", '"Edge.Cuts"', "user"],
        ["27", '"Margin"', "user"],
        ["31", '"F.CrtYd"', "user", '"F.Courtyard"'],
        ["29", '"B.CrtYd"', "user", '"B.Courtyard"'],
        ["35", '"F.Fab"', "user"],
        ["33", '"B.Fab"', "user"],
        ["39", '"User.1"', "user"],
        ["41", '"User.2"', "user"],
        ["43", '"User.3"', "user"],
        ["45", '"User.4"', "user"],
    ],
    [
        "setup",
        ["pad_to_mask_clearance", "0"],
        ["allow_soldermask_bridges_in_footprints", "no"],
        ["tenting", "front", "back"],
        [
            "pcbplotparams",
            ["layerselection", "0x00000000_00000000_55555555_5755f5ff"],
            ["plot_on_all_layers_selection", "0x00000000_00000000_00000000_00000000"],
            ["disableapertmacros", "no"],
            ["usegerberextensions", "no"],
            ["usegerberattributes", "yes"],
            ["usegerberadvancedattributes", "yes"],
            ["creategerberjobfile", "yes"],
            ["dashed_line_dash_ratio", "12.000000"],
            ["dashed_line_gap_ratio", "3.000000"],
            ["svgprecision", "4"],
            ["plotframeref", "no"],
            ["mode", "1"],
            ["useauxorigin", "no"],
            ["hpglpennumber", "1"],
            ["hpglpenspeed", "20"],
            ["hpglpendiameter", "15.000000"],
            ["pdf_front_fp_property_popups", "yes"],
            ["pdf_back_fp_property_popups", "yes"],
            ["pdf_metadata", "yes"],
            ["pdf_single_document", "no"],
            ["dxfpolygonmode", "yes"],
            ["dxfimperialunits", "yes"],
            ["dxfusepcbnewfont", "yes"],
            ["psnegative", "no"],
            ["psa4output", "no"],
            ["plot_black_and_white", "yes"],
            ["sketchpadsonfab", "no"],
            ["plotpadnumbers", "no"],
            ["hidednponfab", "no"],
            ["sketchdnponfab", "yes"],
            ["crossoutdnponfab", "yes"],
            ["subtractmaskfromsilk", "no"],
            ["outputformat", "1"],
            ["mirror", "no"],
            ["drillshape", "1"],
            ["scaleselection", "1"],
            ["outputdirectory", '""'],
        ],
    ],
]


# read existing net names
netnames = []
if old_pcb:
    for netname in sexp.pcb_netnames(old_pcb):
        if netname and netname not in netnames:
            netnames.append(netname)

# read all module net names and check sizes
for name, settings in setup["modules"].items():
    dimentions = sexp.pcb_dimentions(settings["module_pcb"])
    settings.update(dimentions)
    for netname in sexp.pcb_netnames(settings["module_pcb"]):
        if netname and netname not in netnames:
            netnames.append(netname)

# print(netnames)

# add all netnames to new pcb
pcb_new.append(["net", "0", '""'])
for netnum, netname in enumerate(netnames, 1):
    pcb_new.append(["net", f"{netnum}", f'"{netname}"'])


# adding parts from existing pcb
uuid_exsits_pcb = []
if old_pcb:
    for entry in sexp.get_types(old_pcb, {"footprint", "segment", "gr_rect", "via"}):
        iuuid = None
        for sentry in entry[1:]:
            if sentry[0] == "uuid":
                iuuid = sentry[1].strip('"')
        if iuuid:
            uuid_exsits_pcb.append(iuuid)
            for sentry in entry[1:]:
                for ssentry in sentry[1:]:
                    # update net numbers
                    if ssentry[0] == "net":
                        if len(ssentry) == 3:
                            netname = ssentry[2].strip('"')
                            if netname in netnames:
                                netnum = netnames.index(netname) + 1
                                # print(ssentry, netnum, netname)
                                ssentry[1] = f"{netnum}"
                            else:
                                print(ssentry)
            pcb_new.append(entry)

# PCB: place/copy parts
position_y = 14
enum = 0
ref = None
refs = {}

for name, settings in setup["modules"].items():
    position_x = 310
    for num, suuid in settings["sheets"].items():
        groupids = []
        # print(num, suuid)
        for entry in sexp.get_types(copy.deepcopy(settings["module_pcb"]), {"footprint", "segment", "gr_rect", "via"}):
            # get uuid
            uuid_prefix = None
            for sentry in entry[1:]:
                if sentry[0] == "uuid":
                    uuid_prefix = sentry[1].strip('"')[:-3]
            puuid = f"{uuid_prefix}{num:03d}"
            groupids.append(puuid)

            # add only new parts
            if puuid in uuid_exsits_pcb:
                continue

            if entry[0] == "gr_rect":
                for sentry in entry[1:]:
                    # convert Edge.Cuts to F.SilkS
                    if sentry[0] == "layer" and sentry[1].strip('"') == "Edge.Cuts":
                        sentry[1] = '"F.SilkS"'

            rotate = settings.get("rotate", {}).get(num)
            if rotate:
                for sentry in sexp.get_property(entry[1:], {"Value", "Reference"}) + sexp.get_types(entry[1:], {"fp_text"}):
                    for ssn, ssentry in enumerate(sentry[1:], 1):
                        if ssentry[0] == "at":
                            rotate_org = 0
                            if len(ssentry) == 4:
                                rotate_org = int(ssentry[3])
                            rotate_org -= rotate
                            while rotate_org < -90:
                                rotate_org += 360
                            while rotate_org > 180:
                                rotate_org -= 360
                            sentry[ssn] = [ssentry[0], ssentry[1], ssentry[2], str(rotate_org)]

            for sn, sentry in enumerate(entry[1:], 1):
                if sentry[0] == "uuid":
                    # update uuid
                    sentry[1] = f'"{puuid}"'
                elif sentry[0] == "pad":
                    # rotating pads
                    if rotate:
                        for ssn, ssentry in enumerate(sexp.get_types(sentry[4:], {"at"}), 4):
                            rotate_org = 0
                            if len(ssentry) == 4:
                                rotate_org = int(ssentry[3])
                            rotate_org -= rotate
                            while rotate_org < -90:
                                rotate_org += 360
                            while rotate_org > 180:
                                rotate_org -= 360
                            sentry[ssn] = [ssentry[0], ssentry[1], ssentry[2], str(rotate_org)]
                elif sentry[0] in {"at", "start", "end"}:
                    # update position and rotate parts
                    pos_x_org = float(sentry[1].strip('"'))
                    pos_y_org = float(sentry[2].strip('"'))
                    rotate_org = 0
                    if sentry[0] == "at" and len(sentry) == 4:
                        rotate_org = float(sentry[3].strip('"'))
                    px = position_x
                    py = position_y
                    if spos := settings.get("pos", {}).get(num):
                        px = spos[0]
                        py = spos[1]
                    if rotate := settings.get("rotate", {}).get(num):
                        if sentry[0] == "at":
                            rotate_org -= rotate
                            while rotate_org < -90:
                                rotate_org += 360
                            while rotate_org > 180:
                                rotate_org -= 360
                        pos_x_org, pos_y_org = sexp.rotate_point((settings["start_x"] + settings["center_x"], settings["start_y"] + settings["center_y"]), (pos_x_org, pos_y_org), -rotate)
                    pos_x_new = px + pos_x_org - settings["start_x"]
                    pos_y_new = py + pos_y_org - settings["start_y"]
                    sentry[1] = f"{pos_x_new:0.3f}"
                    sentry[2] = f"{pos_y_new:0.3f}"
                    if sentry[0] == "at" and entry[0] not in {"via", "pad"}:
                        entry[sn] = [sentry[0], sentry[1], sentry[2], f"{int(rotate_org)}"]
                elif sentry[0] == "sheetname":
                    # update sheetname
                    sheetname_old = sentry[1].strip('"')
                    sheetname_new = f"/{name}{num}"
                    sentry[1] = f'"{sheetname_new}"'
                elif sentry[0] == "path":
                    # update path
                    cuuid = sentry[1].strip('"').split("/")[-1]
                    if settings.get("main"):
                        sentry[1] = f'"/{cuuid}"'
                    else:
                        sentry[1] = f'"/{suuid}/{cuuid}"'
                for ssentry in sentry[1:]:
                    # update net numbers
                    if ssentry[0] == "net":
                        # TODO: uniq or rename Net-* per sheet / or by Referenz ?
                        if len(ssentry) == 3:
                            netname = ssentry[2].strip('"')
                            if netname in netnames:
                                netnum = netnames.index(netname) + 1
                                # print(ssentry, netnum, netname)
                                ssentry[1] = f"{netnum}"
                            else:
                                print(ssentry)
                    elif ssentry[0] == "uuid":
                        # update sub uuid
                        sub_uuid_prefix = ssentry[1].strip('"')[:-3]
                        sub_uuid = f"{sub_uuid_prefix}{num:03d}"
                        # print(sub_uuid_prefix, sub_uuid)
                        groupids.append(sub_uuid)
                        ssentry[1] = f'"{sub_uuid}"'
            pcb_new.append(entry)
        position_x += settings["width"]

        # print(name, groupids)
        if groupids:
            suuid_prefix = suuid[:-3]
            guuid = f"{suuid}{num + 900:03d}"
            group = ["group", '""', ["uuid", f'"{guuid}"'], ["members"]]
            for groupid in groupids:
                group[-1].append(f'"{groupid}"')
            pcb_new.append(group)
    position_y += settings["height"] + 5
pcb_new.append(["embedded_fonts", "no"])

open(f"{project_name}.kicad_pcb", "w").write(sexp.dumps(pcb_new))

pos_x = 310
pos_y = 15
width = 20
pin_conn = []

for name, settings in setup["modules"].items():
    if settings.get("main"):
        continue
    num = 0
    for iname, idata in settings["instances"].items():
        sheetname = f"{name}{num}"
        suuid = settings["sheets"][num]
        height = (len(settings["spins"]) + 2) * 2.54
        if suuid in uuid_exsits_sch:
            pos_y += height + 2.54 + 2.54
            num += 1
            continue
        sch_new.append(
            [
                "sheet",
                ["at", f"{pos_x}", f"{pos_y}"],
                ["size", f"{width}", f"{height}"],
                ["exclude_from_sim", "no"],
                ["in_bom", "yes"],
                ["on_board", "yes"],
                ["dnp", "no"],
                ["fields_autoplaced", "yes"],
                [
                    "stroke",
                    ["width", "0.1524"],
                    ["type", "solid"],
                ],
                [
                    "fill",
                    ["color", "0", "0", "0", "0.0000"],
                ],
                ["uuid", f'"{suuid}"'],
                [
                    "property",
                    '"Sheetname"',
                    f'"{sheetname}"',
                    ["at", f"{pos_x}", f"{pos_y}", "0"],
                    [
                        "effects",
                        [
                            "font",
                            ["size", "1.27", "1.27"],
                        ],
                        ["justify", "left bottom"],
                    ],
                ],
                [
                    "property",
                    '"Sheetfile"',
                    f'"{name}.kicad_sch"',
                    ["at", f"{pos_x}", f"{pos_y + height}", "0"],
                    [
                        "effects",
                        [
                            "font",
                            ["size", "1.27", "1.27"],
                        ],
                        ["justify", "left", "top"],
                    ],
                ],
            ]
        )
        pin_x = pos_x
        pin_y = pos_y
        for pin_name, direction in settings["spins"].items():
            pin_y += 2.54
            puuid = str(uuid.uuid4())
            conpuuid = str(uuid.uuid4())
            connected_pin = idata.get("pins", {}).get(pin_name)
            sch_new[-1].append(
                [
                    "pin",
                    f'"{pin_name}"',
                    f"{direction}",
                    ["at", f"{pin_x}", f"{pin_y}", "180"],
                    ["uuid", f'"{puuid}"'],
                    [
                        "effects",
                        [
                            "font",
                            ["size", "1.27", "1.27"],
                        ],
                        ["justify", "left"],
                    ],
                ]
            )
            if connected_pin:
                pin_conn.append(
                    [
                        "global_label",
                        f'"{connected_pin}"',
                        ["shape", "input"],
                        ["at", f"{pin_x}", f"{pin_y}", "180"],
                        ["fields_autoplaced", "yes"],
                        [
                            "effects",
                            [
                                "font",
                                ["size", "1.27", "1.27"],
                            ],
                            ["justify", "right"],
                        ],
                        ["uuid", f'"{conpuuid}"'],
                        [
                            "property",
                            '"Intersheetrefs"',
                            '"${INTERSHEET_REFS}"',
                            ["at", f"{pin_x - 4.75}", f"{pin_y}", "0"],
                            [
                                "effects",
                                [
                                    "font",
                                    ["size", "1.27", "1.27"],
                                ],
                                ["justify", "right"],
                                ["hide", "yes"],
                            ],
                        ],
                    ]
                )

        sch_new[-1].append(
            [
                "instances",
                [
                    "project",
                    f'"{project_name}"',
                    [
                        "path",
                        f'"/{rootid}"',
                        ["page", '"2"'],
                    ],
                ],
            ]
        )
        pos_y += height + 2.54 + 2.54
        num += 1

sch_new += pin_conn
sch_new.append(["sheet_instances", ["path", '"/"', ["page", '"1"']]])
sch_new.append(["embedded_fonts", "no"])
# print(json.dumps(sch_new, indent=4))
open(f"{project_name}.kicad_sch", "w").write(sexp.dumps(sch_new))


sheets = [[f"{rootid}", "Root"]]
for name, settings in setup["modules"].items():
    for num, suuid in settings["sheets"].items():
        sheets.append([f"{suuid}", f"{name}"])

data_pro = {
    "board": {
        "3dviewports": [],
        "design_settings": {
            "defaults": {
                "apply_defaults_to_fp_fields": False,
                "apply_defaults_to_fp_shapes": False,
                "apply_defaults_to_fp_text": False,
                "board_outline_line_width": 0.05,
                "copper_line_width": 0.2,
                "copper_text_italic": False,
                "copper_text_size_h": 1.5,
                "copper_text_size_v": 1.5,
                "copper_text_thickness": 0.3,
                "copper_text_upright": False,
                "courtyard_line_width": 0.05,
                "dimension_precision": 4,
                "dimension_units": 3,
                "dimensions": {"arrow_length": 1270000, "extension_offset": 500000, "keep_text_aligned": True, "suppress_zeroes": True, "text_position": 0, "units_format": 0},
                "fab_line_width": 0.1,
                "fab_text_italic": False,
                "fab_text_size_h": 1.0,
                "fab_text_size_v": 1.0,
                "fab_text_thickness": 0.15,
                "fab_text_upright": False,
                "other_line_width": 0.1,
                "other_text_italic": False,
                "other_text_size_h": 1.0,
                "other_text_size_v": 1.0,
                "other_text_thickness": 0.15,
                "other_text_upright": False,
                "pads": {"drill": 0.8, "height": 1.27, "width": 2.54},
                "silk_line_width": 0.1,
                "silk_text_italic": False,
                "silk_text_size_h": 1.0,
                "silk_text_size_v": 1.0,
                "silk_text_thickness": 0.1,
                "silk_text_upright": False,
                "zones": {"min_clearance": 0.5},
            },
            "diff_pair_dimensions": [],
            "drc_exclusions": [],
            "meta": {"version": 2},
            "rule_severities": {
                "annular_width": "error",
                "clearance": "error",
                "connection_width": "warning",
                "copper_edge_clearance": "error",
                "copper_sliver": "warning",
                "courtyards_overlap": "error",
                "creepage": "error",
                "diff_pair_gap_out_of_range": "error",
                "diff_pair_uncoupled_length_too_long": "error",
                "drill_out_of_range": "error",
                "duplicate_footprints": "warning",
                "extra_footprint": "warning",
                "footprint": "error",
                "footprint_filters_mismatch": "ignore",
                "footprint_symbol_mismatch": "warning",
                "footprint_type_mismatch": "ignore",
                "hole_clearance": "error",
                "hole_to_hole": "warning",
                "holes_co_located": "warning",
                "invalid_outline": "error",
                "isolated_copper": "warning",
                "item_on_disabled_layer": "error",
                "items_not_allowed": "error",
                "length_out_of_range": "error",
                "lib_footprint_issues": "warning",
                "lib_footprint_mismatch": "warning",
                "malformed_courtyard": "error",
                "microvia_drill_out_of_range": "error",
                "mirrored_text_on_front_layer": "warning",
                "missing_courtyard": "ignore",
                "missing_footprint": "warning",
                "net_conflict": "warning",
                "nonmirrored_text_on_back_layer": "warning",
                "npth_inside_courtyard": "ignore",
                "padstack": "warning",
                "pth_inside_courtyard": "ignore",
                "shorting_items": "error",
                "silk_edge_clearance": "warning",
                "silk_over_copper": "warning",
                "silk_overlap": "warning",
                "skew_out_of_range": "error",
                "solder_mask_bridge": "error",
                "starved_thermal": "error",
                "text_height": "warning",
                "text_on_edge_cuts": "error",
                "text_thickness": "warning",
                "through_hole_pad_without_hole": "error",
                "too_many_vias": "error",
                "track_angle": "error",
                "track_dangling": "warning",
                "track_segment_length": "error",
                "track_width": "error",
                "tracks_crossing": "error",
                "unconnected_items": "error",
                "unresolved_variable": "error",
                "via_dangling": "warning",
                "zones_intersect": "error",
            },
            "rules": {
                "max_error": 0.005,
                "min_clearance": 0.0,
                "min_connection": 0.0,
                "min_copper_edge_clearance": 0.5,
                "min_groove_width": 0.0,
                "min_hole_clearance": 0.25,
                "min_hole_to_hole": 0.25,
                "min_microvia_diameter": 0.2,
                "min_microvia_drill": 0.1,
                "min_resolved_spokes": 2,
                "min_silk_clearance": 0.0,
                "min_text_height": 0.8,
                "min_text_thickness": 0.08,
                "min_through_hole_diameter": 0.3,
                "min_track_width": 0.0,
                "min_via_annular_width": 0.1,
                "min_via_diameter": 0.5,
                "solder_mask_to_copper_clearance": 0.0,
                "use_height_for_length_calcs": True,
            },
            "teardrop_options": [{"td_onpthpad": True, "td_onroundshapesonly": False, "td_onsmdpad": True, "td_ontrackend": False, "td_onvia": True}],
            "teardrop_parameters": [
                {"td_allow_use_two_tracks": True, "td_curve_segcount": 0, "td_height_ratio": 1.0, "td_length_ratio": 0.5, "td_maxheight": 2.0, "td_maxlen": 1.0, "td_on_pad_in_zone": False, "td_target_name": "td_round_shape", "td_width_to_size_filter_ratio": 0.9},
                {"td_allow_use_two_tracks": True, "td_curve_segcount": 0, "td_height_ratio": 1.0, "td_length_ratio": 0.5, "td_maxheight": 2.0, "td_maxlen": 1.0, "td_on_pad_in_zone": False, "td_target_name": "td_rect_shape", "td_width_to_size_filter_ratio": 0.9},
                {"td_allow_use_two_tracks": True, "td_curve_segcount": 0, "td_height_ratio": 1.0, "td_length_ratio": 0.5, "td_maxheight": 2.0, "td_maxlen": 1.0, "td_on_pad_in_zone": False, "td_target_name": "td_track_end", "td_width_to_size_filter_ratio": 0.9},
            ],
            "track_widths": [],
            "tuning_pattern_settings": {
                "diff_pair_defaults": {"corner_radius_percentage": 80, "corner_style": 1, "max_amplitude": 1.0, "min_amplitude": 0.2, "single_sided": False, "spacing": 1.0},
                "diff_pair_skew_defaults": {"corner_radius_percentage": 80, "corner_style": 1, "max_amplitude": 1.0, "min_amplitude": 0.2, "single_sided": False, "spacing": 0.6},
                "single_track_defaults": {"corner_radius_percentage": 80, "corner_style": 1, "max_amplitude": 1.0, "min_amplitude": 0.2, "single_sided": False, "spacing": 0.6},
            },
            "via_dimensions": [],
            "zones_allow_external_fillets": False,
        },
        "ipc2581": {"dist": "", "distpn": "", "internal_id": "", "mfg": "", "mpn": ""},
        "layer_pairs": [],
        "layer_presets": [],
        "viewports": [],
    },
    "boards": [],
    "cvpcb": {"equivalence_files": []},
    "erc": {
        "erc_exclusions": [],
        "meta": {"version": 0},
        "pin_map": [
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2],
            [0, 2, 0, 1, 0, 0, 1, 0, 2, 2, 2, 2],
            [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 2],
            [0, 1, 0, 0, 0, 0, 1, 1, 2, 1, 1, 2],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
            [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 2],
            [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 2],
            [0, 2, 1, 2, 0, 0, 1, 0, 2, 2, 2, 2],
            [0, 2, 0, 1, 0, 0, 1, 0, 2, 0, 0, 2],
            [0, 2, 1, 1, 0, 0, 1, 0, 2, 0, 0, 2],
            [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
        ],
        "rule_severities": {
            "bus_definition_conflict": "error",
            "bus_entry_needed": "error",
            "bus_to_bus_conflict": "error",
            "bus_to_net_conflict": "error",
            "different_unit_footprint": "error",
            "different_unit_net": "error",
            "duplicate_reference": "error",
            "duplicate_sheet_names": "error",
            "endpoint_off_grid": "warning",
            "extra_units": "error",
            "footprint_filter": "ignore",
            "footprint_link_issues": "warning",
            "four_way_junction": "ignore",
            "global_label_dangling": "warning",
            "hier_label_mismatch": "error",
            "label_dangling": "error",
            "label_multiple_wires": "warning",
            "lib_symbol_issues": "warning",
            "lib_symbol_mismatch": "warning",
            "missing_bidi_pin": "warning",
            "missing_input_pin": "warning",
            "missing_power_pin": "error",
            "missing_unit": "warning",
            "multiple_net_names": "warning",
            "net_not_bus_member": "warning",
            "no_connect_connected": "warning",
            "no_connect_dangling": "warning",
            "pin_not_connected": "error",
            "pin_not_driven": "error",
            "pin_to_pin": "warning",
            "power_pin_not_driven": "error",
            "same_local_global_label": "warning",
            "similar_label_and_power": "warning",
            "similar_labels": "warning",
            "similar_power": "warning",
            "simulation_model_issue": "ignore",
            "single_global_label": "ignore",
            "unannotated": "error",
            "unconnected_wire_endpoint": "warning",
            "unit_value_mismatch": "error",
            "unresolved_variable": "error",
            "wire_dangling": "error",
        },
    },
    "libraries": {"pinned_footprint_libs": [], "pinned_symbol_libs": []},
    "meta": {"filename": f"{project_name}.kicad_pro", "version": 3},
    "net_settings": {
        "classes": [
            {
                "bus_width": 12,
                "clearance": 0.2,
                "diff_pair_gap": 0.25,
                "diff_pair_via_gap": 0.25,
                "diff_pair_width": 0.2,
                "line_style": 0,
                "microvia_diameter": 0.3,
                "microvia_drill": 0.1,
                "name": "Default",
                "pcb_color": "rgba(0, 0, 0, 0.000)",
                "priority": 2147483647,
                "schematic_color": "rgba(0, 0, 0, 0.000)",
                "track_width": 0.2,
                "via_diameter": 0.6,
                "via_drill": 0.3,
                "wire_width": 6,
            }
        ],
        "meta": {"version": 4},
        "net_colors": None,
        "netclass_assignments": None,
        "netclass_patterns": [],
    },
    "pcbnew": {"last_paths": {"gencad": "", "idf": "", "netlist": "", "plot": "", "pos_files": "", "specctra_dsn": "", "step": "", "svg": "", "vrml": ""}, "page_layout_descr_file": ""},
    "schematic": {
        "annotate_start_num": 0,
        "bom_export_filename": "${PROJECTNAME}.csv",
        "bom_fmt_presets": [],
        "bom_fmt_settings": {"field_delimiter": ",", "keep_line_breaks": False, "keep_tabs": False, "name": "CSV", "ref_delimiter": ",", "ref_range_delimiter": "", "string_delimiter": '"'},
        "bom_presets": [],
        "bom_settings": {
            "exclude_dnp": False,
            "fields_ordered": [
                {"group_by": False, "label": "Reference", "name": "Reference", "show": True},
                {"group_by": False, "label": "Qty", "name": "${QUANTITY}", "show": True},
                {"group_by": True, "label": "Value", "name": "Value", "show": True},
                {"group_by": True, "label": "DNP", "name": "${DNP}", "show": True},
                {"group_by": True, "label": "Exclude from BOM", "name": "${EXCLUDE_FROM_BOM}", "show": True},
                {"group_by": True, "label": "Exclude from Board", "name": "${EXCLUDE_FROM_BOARD}", "show": True},
                {"group_by": True, "label": "Footprint", "name": "Footprint", "show": True},
                {"group_by": False, "label": "Datasheet", "name": "Datasheet", "show": True},
            ],
            "filter_string": "",
            "group_symbols": True,
            "include_excluded_from_bom": True,
            "name": "Default Editing",
            "sort_asc": True,
            "sort_field": "Reference",
        },
        "connection_grid_size": 50.0,
        "drawing": {
            "dashed_lines_dash_length_ratio": 12.0,
            "dashed_lines_gap_length_ratio": 3.0,
            "default_line_thickness": 6.0,
            "default_text_size": 50.0,
            "field_names": [],
            "intersheets_ref_own_page": False,
            "intersheets_ref_prefix": "",
            "intersheets_ref_short": False,
            "intersheets_ref_show": False,
            "intersheets_ref_suffix": "",
            "junction_size_choice": 3,
            "label_size_ratio": 0.375,
            "operating_point_overlay_i_precision": 3,
            "operating_point_overlay_i_range": "~A",
            "operating_point_overlay_v_precision": 3,
            "operating_point_overlay_v_range": "~V",
            "overbar_offset_ratio": 1.23,
            "pin_symbol_size": 25.0,
            "text_offset_ratio": 0.15,
        },
        "legacy_lib_dir": "",
        "legacy_lib_list": [],
        "meta": {"version": 1},
        "net_format_name": "",
        "page_layout_descr_file": "",
        "plot_directory": "",
        "space_save_all_events": True,
        "spice_current_sheet_as_root": False,
        "spice_external_command": 'spice "%I"',
        "spice_model_current_sheet_as_root": True,
        "spice_save_all_currents": False,
        "spice_save_all_dissipations": False,
        "spice_save_all_voltages": False,
        "subpart_first_id": 65,
        "subpart_id_separator": 0,
    },
    "sheets": sheets,
    "text_variables": {},
}
open(f"{project_name}.kicad_pro", "w").write(json.dumps(data_pro, indent=4))

data_prl = {
    "board": {
        "active_layer": 0,
        "active_layer_preset": "All Layers",
        "auto_track_width": False,
        "hidden_netclasses": [],
        "hidden_nets": [],
        "high_contrast_mode": 0,
        "net_color_mode": 1,
        "opacity": {"images": 1.0, "pads": 1.0, "shapes": 1.0, "tracks": 1.0, "vias": 1.0, "zones": 1.0},
        "selection_filter": {"dimensions": True, "footprints": True, "graphics": True, "keepouts": True, "lockedItems": False, "otherItems": True, "pads": True, "text": True, "tracks": True, "vias": True, "zones": True},
        "visible_items": ["vias", "footprint_text", "footprint_anchors", "ratsnest", "grid", "footprints_front", "footprints_back", "footprint_values", "footprint_references", "tracks", "drc_errors", "drawing_sheet", "bitmaps", "pads", "zones", "drc_warnings", "locked_item_shadows", "conflict_shadows", "shapes"],
        "visible_layers": "ffffffff_ffffffff_ffffffff_ffffffff",
        "zone_display_mode": 0,
    },
    "git": {"repo_type": "", "repo_username": "", "ssh_key": ""},
    "meta": {"filename": f"{project_name}.kicad_prl", "version": 5},
    "net_inspector_panel": {
        "col_hidden": [False, False, False, False, False, False, False, False, False, False],
        "col_order": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        "col_widths": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "custom_group_rules": [],
        "expanded_rows": [],
        "filter_by_net_name": True,
        "filter_by_netclass": True,
        "filter_text": "",
        "group_by_constraint": False,
        "group_by_netclass": False,
        "show_unconnected_nets": False,
        "show_zero_pad_nets": False,
        "sort_ascending": True,
        "sorting_column": 0,
    },
    "open_jobsets": [],
    "project": {"files": []},
    "schematic": {"selection_filter": {"graphics": True, "images": True, "labels": True, "lockedItems": False, "otherItems": True, "pins": True, "symbols": True, "text": True, "wires": True}},
}
open(f"{project_name}.kicad_prl", "w").write(json.dumps(data_prl, indent=4))
