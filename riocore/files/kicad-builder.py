import json
import os
import sys
import uuid

setup = json.loads(open(sys.argv[1], "r").read())

rootid = str(uuid.uuid4())


positions = {}

kicad_sch_prev = ""
kicad_pcb_prev = ""
if os.path.isfile("rioboard.kicad_sch"):
    kicad_sch_prev = open("rioboard.kicad_sch", "r").read()
if os.path.isfile("rioboard.kicad_pcb"):
    kicad_pcb_prev = open("rioboard.kicad_pcb", "r").read()
    # kicad_pcb_prev = open("rioboard.kicad_pcb_bak", "r").read()

    data = {}
    for line in kicad_pcb_prev.split("\n"):
        # positions
        if line.startswith("		(uuid "):
            data["uuid"] = line.split('"')[1]
        elif line.startswith(("		(at ", "		(start ", "		(end ")):
            ptype = line.split()[0].strip("(")
            data[ptype] = line.strip()
        elif line.startswith("	)"):
            if "uuid" in data:
                positions[data["uuid"]] = data
            data = {}


pcb_data_new = []
pcb_data_new.append("""(kicad_pcb
	(version 20241229)
	(generator "pcbnew")
	(generator_version "9.0")
	(general
		(thickness 1.6)
		(legacy_teardrops no)
	)
	(paper "A4")
	(layers
		(0 "F.Cu" signal)
		(2 "B.Cu" signal)
		(9 "F.Adhes" user "F.Adhesive")
		(11 "B.Adhes" user "B.Adhesive")
		(13 "F.Paste" user)
		(15 "B.Paste" user)
		(5 "F.SilkS" user "F.Silkscreen")
		(7 "B.SilkS" user "B.Silkscreen")
		(1 "F.Mask" user)
		(3 "B.Mask" user)
		(17 "Dwgs.User" user "User.Drawings")
		(19 "Cmts.User" user "User.Comments")
		(21 "Eco1.User" user "User.Eco1")
		(23 "Eco2.User" user "User.Eco2")
		(25 "Edge.Cuts" user)
		(27 "Margin" user)
		(31 "F.CrtYd" user "F.Courtyard")
		(29 "B.CrtYd" user "B.Courtyard")
		(35 "F.Fab" user)
		(33 "B.Fab" user)
		(39 "User.1" user)
		(41 "User.2" user)
		(43 "User.3" user)
		(45 "User.4" user)
	)
	(setup
		(pad_to_mask_clearance 0)
		(allow_soldermask_bridges_in_footprints no)
		(tenting front back)
		(pcbplotparams
			(layerselection 0x00000000_00000000_55555555_5755f5ff)
			(plot_on_all_layers_selection 0x00000000_00000000_00000000_00000000)
			(disableapertmacros no)
			(usegerberextensions no)
			(usegerberattributes yes)
			(usegerberadvancedattributes yes)
			(creategerberjobfile yes)
			(dashed_line_dash_ratio 12.000000)
			(dashed_line_gap_ratio 3.000000)
			(svgprecision 4)
			(plotframeref no)
			(mode 1)
			(useauxorigin no)
			(hpglpennumber 1)
			(hpglpenspeed 20)
			(hpglpendiameter 15.000000)
			(pdf_front_fp_property_popups yes)
			(pdf_back_fp_property_popups yes)
			(pdf_metadata yes)
			(pdf_single_document no)
			(dxfpolygonmode yes)
			(dxfimperialunits yes)
			(dxfusepcbnewfont yes)
			(psnegative no)
			(psa4output no)
			(plot_black_and_white yes)
			(sketchpadsonfab no)
			(plotpadnumbers no)
			(hidednponfab no)
			(sketchdnponfab yes)
			(crossoutdnponfab yes)
			(subtractmaskfromsilk no)
			(outputformat 1)
			(mirror no)
			(drillshape 1)
			(scaleselection 1)
			(outputdirectory "")
		)
	)""")


# predefine
for name, settings in setup.items():
    settings["spins"] = {}
    settings["sheets"] = {}
    settings["old_sch"] = open(f"{settings['path']}/{name}/{name}.kicad_sch", "r").read()
    settings["old_pcb"] = open(f"{settings['path']}/{name}/{name}.kicad_pcb", "r").read()

    suuid_prefix = None
    for line in settings["old_sch"].split("\n"):
        if "uuid" in line:
            suuid_prefix = line.split('"')[1][:-3]
            break
    if suuid_prefix is None:
        print("ERROR")
        exit(1)

    for num in range(len(settings["instances"])):
        suuid = f"{suuid_prefix}{num:03d}"
        settings["sheets"][num] = suuid

# check dimensions and netnames
netnames = []
for name, settings in setup.items():
    kicad_pcb = f"{settings['path']}/{name}/{name}.kicad_pcb"

    sub_board_data_old = open(kicad_pcb, "r").read()

    settings["start_x"] = 100000
    settings["start_y"] = 100000
    settings["end_x"] = 0
    settings["end_y"] = 0
    settings["width"] = 0
    settings["height"] = 0

    for num, suuid in settings["sheets"].items():
        section = ""
        indent = ""
        reference = ""

        for line in sub_board_data_old.split("\n"):
            sline = line.strip()
            if not sline:
                continue

            fline = sline.split()[0].strip("(")
            if fline in {"footprint", "segment", "gr_rect", "via"}:
                section = fline
                indent = line.split("(")[0]
                reference = ""

            elif line == f"{indent})" and section:
                section = ""
                indent = ""
                reference = ""

            elif section:
                if sline.startswith("(net"):
                    if '"' in line:
                        netname = line.split('"')[1]
                        if netname not in netnames:
                            netnames.append(netname)

                elif line.startswith(("		(start ", "		(end ")):
                    if line.startswith("		(start "):
                        settings["start_x"] = min(settings["start_x"], float(line.split()[1]))
                        settings["start_y"] = min(settings["start_y"], float(line.split()[2].strip(")")))
                    else:
                        settings["end_x"] = max(settings["end_x"], float(line.split()[1]))
                        settings["end_y"] = max(settings["end_y"], float(line.split()[2].strip(")")))

    settings["width"] = settings["end_x"] - settings["start_x"]
    settings["height"] = settings["end_y"] - settings["start_y"]


# list netnames
pcb_data_new.append("""	(net 0 "")""")
for netnum, netname in enumerate(netnames, 1):
    pcb_data_new.append(f"""	(net {netnum} "{netname}")""")


# place/copy parts
pcb_data_new2 = []
position_x = 300
position_y = 14
enum = 0
ref = None

refs = {}
partnumbers = {}

for name, settings in setup.items():
    kicad_pcb = f"{settings['path']}/{name}/{name}.kicad_pcb"
    sub_board_data_old = open(kicad_pcb, "r").read()

    position_x = 300

    num = 0
    for iname, idata in settings["instances"].items():
        num += 1

    for num, suuid in settings["sheets"].items():
        section = ""
        section_lines = []
        indent = ""
        reference = ""
        groupids = []
        enum += 1
        uuid_prefix = None
        # print("-- sheet --")
        for line in sub_board_data_old.split("\n"):
            sline = line.strip()

            if not sline:
                continue

            fline = sline.split()[0].strip("(")
            if fline in {"sheetname"}:
                splitted = line.split('"')
                sheet_name = f"/{name}{num}"
                splitted[1] = sheet_name
                pcb_data_new2.append('"'.join(splitted))
                continue

            if fline in {"footprint", "segment", "gr_rect", "via"}:
                pcb_data_new2.append(line)
                section = fline
                section_lines = []
                indent = line.split("(")[0]
                reference = ""

            elif line == f"{indent})" and section:
                uuid_prefix = None

                for section_line in section_lines:
                    sline = section_line.strip()
                    if sline.startswith("(uuid "):
                        uuid_prefix = sline.split('"')[1][:-3]

                for section_line in section_lines:
                    sline = section_line.strip()
                    if section_line.startswith(("		(at ", "		(start ", "		(end ")):
                        uline = section_line.split(" ")
                        puuid = f"{uuid_prefix}{num:03d}"
                        ptype = section_line.split()[0].strip("(")
                        if uuid_prefix and puuid in positions and ptype in positions[puuid]:
                            # recover position
                            pcb_data_new2.append(f"		{positions[puuid][ptype]}")
                        else:
                            pos_x = position_x + float(uline[1]) - settings["start_x"]
                            pos_y = position_y + float(uline[2].strip(")")) - settings["start_y"]
                            uline[1] = str(pos_x)
                            if uline[2][-1] == ")":
                                uline[2] = str(pos_y) + ")"
                            else:
                                uline[2] = str(pos_y)
                            pcb_data_new2.append(" ".join(uline))

                    elif sline.startswith("(uuid "):
                        uuid_prefix = sline.split('"')[1][:-3]
                        puuid = f"{uuid_prefix}{num:03d}"
                        groupids.append(puuid)
                        uline = section_line.split('"')
                        uline[1] = puuid
                        pcb_data_new2.append('"'.join(uline))

                    elif sline.startswith('(property "Reference" '):
                        uline = section_line.split('"')
                        reference = uline[3]
                        fc = reference.strip("0123456789")
                        if fc not in partnumbers:
                            partnumbers[fc] = 0
                        partnumbers[fc] += 1
                        reference_new = f"{fc}{partnumbers[fc]}"
                        # print(reference_new)
                        uline[3] = reference_new

                        pcb_data_new2.append('"'.join(uline))

                    elif sline.startswith("(path"):
                        sheet_uuid = sline.split('"')[1].split("/")[1]
                        cspit = sline.split('"')[1].split("/")
                        if len(cspit) == 2:
                            cuuid = cspit[1]
                        else:
                            cuuid = cspit[2]
                        refs[cuuid] = reference_new
                        refs[cuuid + suuid] = reference_new

                        if settings.get("main"):
                            pcb_data_new2.append(f'		(path "/{cuuid}")')
                        else:
                            pcb_data_new2.append(f'		(path "/{suuid}/{cuuid}")')

                    elif sline.startswith("(net"):
                        if '"' in section_line:
                            netname = section_line.split('"')[1]
                            netnum = netnames.index(netname) + 1
                            pcb_data_new2.append(f'			(net {netnum} "{netname}")')
                        else:
                            pcb_data_new2.append(section_line)
                    else:
                        pcb_data_new2.append(section_line)

                pcb_data_new2.append(line)
                section = ""
                section_lines = []
                indent = ""
                reference = ""

            elif section:
                section_lines.append(line)

        position_x += settings["width"]

        # print(name, groupids)
        if groupids:
            suuid_prefix = suuid[:-3]
            # guuid = str(uuid.uuid4())
            guuid = f"{suuid}{num + 900:03d}"
            # print(guuid)
            pcb_data_new2.append(f"""	(group ""
		(uuid "{guuid}")
		(members "{'" "'.join(groupids)}"
		)
	)""")

    position_y += settings["height"]

pcb_data_new += pcb_data_new2


sch_data_new = []
sch_data_new.append(f"""(kicad_sch
	(version 20250114)
	(generator "eeschema")
	(generator_version "9.0")
	(uuid "{rootid}")
	(paper "A4")""")


lib_symbols = False
enum = 1
for name, settings in setup.items():
    kicad_sch = f"{settings['path']}/{name}/{name}.kicad_sch"
    section = ""
    indent = ""
    reference = ""
    last_uuid = ""
    enum += 1
    sub_schema_data_old = open(kicad_sch, "r").read()
    settings["schema_data"] = []
    for line in sub_schema_data_old.split("\n"):
        sline = line.strip()

        if sline == "(symbol":
            last_uuid = ""
        elif sline.startswith("(uuid ") and not last_uuid:
            last_uuid = sline.split('"')[1]

        elif sline.startswith("(hierarchical_label "):
            pin_name = sline.split('"')[1]
            settings["spins"][pin_name] = "input"

        if line == "	(instances":
            section = "instances"
            indent = line.split("(")[0]
            reference = ""

        elif line == "	(lib_symbols" and settings.get("main"):
            section = "lib_symbols"
            indent = line.split("(")[0]
            reference = ""
            sch_data_new.append(line)
            lib_symbols = True

        elif sline == "(symbol" and settings.get("main"):
            section = "symbol"
            indent = line.split("(")[0]
            reference = ""
            sch_data_new.append(line)

        elif sline.startswith("(global_label") and settings.get("main"):
            section = "global_label"
            indent = line.split("(")[0]
            reference = ""
            sch_data_new.append(line)

        elif sline.startswith("(reference ") and section and not reference and not settings.get("main"):
            reference = sline.split('"')[1]
            enum += 1

        elif sline.startswith('(property "Reference" ') and last_uuid in refs:
            reference_new = refs[last_uuid]
            settings["schema_data"].append(line)
            if settings.get("main"):
                sch_data_new.append(line)

        elif line == f"{indent})" and section:
            if section in {"lib_symbols", "symbol", "global_label"}:
                sch_data_new.append(line)
            else:
                settings["schema_data"].append("""		(instances
                (project \"bitin\"""")

                for num, suuid in settings["sheets"].items():
                    key = last_uuid + suuid
                    if key in refs:
                        reference_new = refs[key]
                        settings["schema_data"].append(f"""				(path "/{rootid}/{suuid}"
                                (reference "{reference_new}")
                                (unit 1)
                            )""")

                settings["schema_data"].append("""			)
                )""")

            section = ""
            indent = ""
            reference = ""

        elif section in {"lib_symbols", "symbol", "global_label"}:
            sch_data_new.append(line)

        elif section == "instances":
            pass
        else:
            settings["schema_data"].append(line)

    if not settings.get("main"):
        # print(f"{name}.kicad_sch")
        open(f"{name}.kicad_sch", "w").write("\n".join(settings["schema_data"]))


if not lib_symbols:
    sch_data_new.append("""(lib_symbols)""")


pos_x = 261.38
pos_y = 15
width = 20

pin_conn = []

for name, settings in setup.items():
    if settings.get("main"):
        continue

    num = 0
    for iname, idata in settings["instances"].items():
        sheetname = f"{name}{num}"
        suuid = settings["sheets"][num]
        height = (len(settings["spins"]) + 2) * 1.27

        sch_data_new.append(f"""	(sheet
		(at {pos_x} {pos_y})
		(size {width} {height})
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(dnp no)
		(fields_autoplaced yes)
		(stroke
			(width 0.1524)
			(type solid)
		)
		(fill
			(color 0 0 0 0.0000)
		)
		(uuid "{suuid}")
		(property "Sheetname" "{sheetname}"
			(at {pos_x} {pos_y} 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify left bottom)
			)
		)
		(property "Sheetfile" "{name}.kicad_sch"
			(at {pos_x} {pos_y + height} 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify left top)
			)
		)""")

        pin_x = pos_x
        pin_y = pos_y
        for pin_name, direction in settings["spins"].items():
            pin_y += 1.27
            puuid = str(uuid.uuid4())
            conpuuid = str(uuid.uuid4())
            connected_pin = idata.get("pins", {}).get(pin_name)
            # print("##", iname, pin_name, connected_pin, puuid)
            pin_conn.append(f"""	(global_label "{connected_pin}"
		(shape input)
		(at {pin_x} {pin_y} 180)
		(fields_autoplaced yes)
		(effects
			(font
				(size 1.27 1.27)
			)
			(justify right)
		)
		(uuid "{conpuuid}")
		(property "Intersheetrefs" "${{INTERSHEET_REFS}}"
			(at {pin_x - 4.75} {pin_y} 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify right)
				(hide yes)
			)
		)
	)""")

            sch_data_new.append(f"""		(pin "{pin_name}" {direction}
			(at {pin_x} {pin_y} 180)
			(uuid "{puuid}")
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify left)
			)
		)""")

        sch_data_new.append(f"""		(instances
			(project "rioboard"
				(path "/{rootid}"
					(page "2")
				)
			)
		)
	)""")
        pos_y += height + 2.54 + 1.27
        num += 1


sch_data_new += pin_conn

sch_data_new.append("""	(sheet_instances
		(path "/"
			(page "1")
		)
	)
	(embedded_fonts no)
)""")

pcb_data_new.append("""	(embedded_fonts no)
)""")


open("rioboard.kicad_sch", "w").write("\n".join(sch_data_new))
open("rioboard.kicad_pcb", "w").write("\n".join(pcb_data_new))

# print( "\n".join(pcb_data_new) )

data_pro = [
    """{
  "board": {
    "3dviewports": [],
    "design_settings": {
      "defaults": {
        "apply_defaults_to_fp_fields": false,
        "apply_defaults_to_fp_shapes": false,
        "apply_defaults_to_fp_text": false,
        "board_outline_line_width": 0.05,
        "copper_line_width": 0.2,
        "copper_text_italic": false,
        "copper_text_size_h": 1.5,
        "copper_text_size_v": 1.5,
        "copper_text_thickness": 0.3,
        "copper_text_upright": false,
        "courtyard_line_width": 0.05,
        "dimension_precision": 4,
        "dimension_units": 3,
        "dimensions": {
          "arrow_length": 1270000,
          "extension_offset": 500000,
          "keep_text_aligned": true,
          "suppress_zeroes": true,
          "text_position": 0,
          "units_format": 0
        },
        "fab_line_width": 0.1,
        "fab_text_italic": false,
        "fab_text_size_h": 1.0,
        "fab_text_size_v": 1.0,
        "fab_text_thickness": 0.15,
        "fab_text_upright": false,
        "other_line_width": 0.1,
        "other_text_italic": false,
        "other_text_size_h": 1.0,
        "other_text_size_v": 1.0,
        "other_text_thickness": 0.15,
        "other_text_upright": false,
        "pads": {
          "drill": 0.8,
          "height": 1.27,
          "width": 2.54
        },
        "silk_line_width": 0.1,
        "silk_text_italic": false,
        "silk_text_size_h": 1.0,
        "silk_text_size_v": 1.0,
        "silk_text_thickness": 0.1,
        "silk_text_upright": false,
        "zones": {
          "min_clearance": 0.5
        }
      },
      "diff_pair_dimensions": [],
      "drc_exclusions": [],
      "meta": {
        "version": 2
      },
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
        "zones_intersect": "error"
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
        "use_height_for_length_calcs": true
      },
      "teardrop_options": [
        {
          "td_onpthpad": true,
          "td_onroundshapesonly": false,
          "td_onsmdpad": true,
          "td_ontrackend": false,
          "td_onvia": true
        }
      ],
      "teardrop_parameters": [
        {
          "td_allow_use_two_tracks": true,
          "td_curve_segcount": 0,
          "td_height_ratio": 1.0,
          "td_length_ratio": 0.5,
          "td_maxheight": 2.0,
          "td_maxlen": 1.0,
          "td_on_pad_in_zone": false,
          "td_target_name": "td_round_shape",
          "td_width_to_size_filter_ratio": 0.9
        },
        {
          "td_allow_use_two_tracks": true,
          "td_curve_segcount": 0,
          "td_height_ratio": 1.0,
          "td_length_ratio": 0.5,
          "td_maxheight": 2.0,
          "td_maxlen": 1.0,
          "td_on_pad_in_zone": false,
          "td_target_name": "td_rect_shape",
          "td_width_to_size_filter_ratio": 0.9
        },
        {
          "td_allow_use_two_tracks": true,
          "td_curve_segcount": 0,
          "td_height_ratio": 1.0,
          "td_length_ratio": 0.5,
          "td_maxheight": 2.0,
          "td_maxlen": 1.0,
          "td_on_pad_in_zone": false,
          "td_target_name": "td_track_end",
          "td_width_to_size_filter_ratio": 0.9
        }
      ],
      "track_widths": [],
      "tuning_pattern_settings": {
        "diff_pair_defaults": {
          "corner_radius_percentage": 80,
          "corner_style": 1,
          "max_amplitude": 1.0,
          "min_amplitude": 0.2,
          "single_sided": false,
          "spacing": 1.0
        },
        "diff_pair_skew_defaults": {
          "corner_radius_percentage": 80,
          "corner_style": 1,
          "max_amplitude": 1.0,
          "min_amplitude": 0.2,
          "single_sided": false,
          "spacing": 0.6
        },
        "single_track_defaults": {
          "corner_radius_percentage": 80,
          "corner_style": 1,
          "max_amplitude": 1.0,
          "min_amplitude": 0.2,
          "single_sided": false,
          "spacing": 0.6
        }
      },
      "via_dimensions": [],
      "zones_allow_external_fillets": false
    },
    "ipc2581": {
      "dist": "",
      "distpn": "",
      "internal_id": "",
      "mfg": "",
      "mpn": ""
    },
    "layer_pairs": [],
    "layer_presets": [],
    "viewports": []
  },
  "boards": [],
  "cvpcb": {
    "equivalence_files": []
  },
  "erc": {
    "erc_exclusions": [],
    "meta": {
      "version": 0
    },
    "pin_map": [
      [
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        0,
        0,
        0,
        0,
        2
      ],
      [
        0,
        2,
        0,
        1,
        0,
        0,
        1,
        0,
        2,
        2,
        2,
        2
      ],
      [
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        0,
        1,
        0,
        1,
        2
      ],
      [
        0,
        1,
        0,
        0,
        0,
        0,
        1,
        1,
        2,
        1,
        1,
        2
      ],
      [
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        0,
        0,
        0,
        0,
        2
      ],
      [
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        2
      ],
      [
        1,
        1,
        1,
        1,
        1,
        0,
        1,
        1,
        1,
        1,
        1,
        2
      ],
      [
        0,
        0,
        0,
        1,
        0,
        0,
        1,
        0,
        0,
        0,
        0,
        2
      ],
      [
        0,
        2,
        1,
        2,
        0,
        0,
        1,
        0,
        2,
        2,
        2,
        2
      ],
      [
        0,
        2,
        0,
        1,
        0,
        0,
        1,
        0,
        2,
        0,
        0,
        2
      ],
      [
        0,
        2,
        1,
        1,
        0,
        0,
        1,
        0,
        2,
        0,
        0,
        2
      ],
      [
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2
      ]
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
      "wire_dangling": "error"
    }
  },
  "libraries": {
    "pinned_footprint_libs": [],
    "pinned_symbol_libs": []
  },
  "meta": {
    "filename": "rioboard.kicad_pro",
    "version": 3
  },
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
        "wire_width": 6
      }
    ],
    "meta": {
      "version": 4
    },
    "net_colors": null,
    "netclass_assignments": null,
    "netclass_patterns": []
  },
  "pcbnew": {
    "last_paths": {
      "gencad": "",
      "idf": "",
      "netlist": "",
      "plot": "",
      "pos_files": "",
      "specctra_dsn": "",
      "step": "",
      "svg": "",
      "vrml": ""
    },
    "page_layout_descr_file": ""
  },
  "schematic": {
    "annotate_start_num": 0,
    "bom_export_filename": "${PROJECTNAME}.csv",
    "bom_fmt_presets": [],
    "bom_fmt_settings": {
      "field_delimiter": ",",
      "keep_line_breaks": false,
      "keep_tabs": false,
      "name": "CSV",
      "ref_delimiter": ",",
      "ref_range_delimiter": "",
      "string_delimiter": "\""
    },
    "bom_presets": [],
    "bom_settings": {
      "exclude_dnp": false,
      "fields_ordered": [
        {
          "group_by": false,
          "label": "Reference",
          "name": "Reference",
          "show": true
        },
        {
          "group_by": false,
          "label": "Qty",
          "name": "${QUANTITY}",
          "show": true
        },
        {
          "group_by": true,
          "label": "Value",
          "name": "Value",
          "show": true
        },
        {
          "group_by": true,
          "label": "DNP",
          "name": "${DNP}",
          "show": true
        },
        {
          "group_by": true,
          "label": "Exclude from BOM",
          "name": "${EXCLUDE_FROM_BOM}",
          "show": true
        },
        {
          "group_by": true,
          "label": "Exclude from Board",
          "name": "${EXCLUDE_FROM_BOARD}",
          "show": true
        },
        {
          "group_by": true,
          "label": "Footprint",
          "name": "Footprint",
          "show": true
        },
        {
          "group_by": false,
          "label": "Datasheet",
          "name": "Datasheet",
          "show": true
        }
      ],
      "filter_string": "",
      "group_symbols": true,
      "include_excluded_from_bom": true,
      "name": "Default Editing",
      "sort_asc": true,
      "sort_field": "Reference"
    },
    "connection_grid_size": 50.0,
    "drawing": {
      "dashed_lines_dash_length_ratio": 12.0,
      "dashed_lines_gap_length_ratio": 3.0,
      "default_line_thickness": 6.0,
      "default_text_size": 50.0,
      "field_names": [],
      "intersheets_ref_own_page": false,
      "intersheets_ref_prefix": "",
      "intersheets_ref_short": false,
      "intersheets_ref_show": false,
      "intersheets_ref_suffix": "",
      "junction_size_choice": 3,
      "label_size_ratio": 0.375,
      "operating_point_overlay_i_precision": 3,
      "operating_point_overlay_i_range": "~A",
      "operating_point_overlay_v_precision": 3,
      "operating_point_overlay_v_range": "~V",
      "overbar_offset_ratio": 1.23,
      "pin_symbol_size": 25.0,
      "text_offset_ratio": 0.15
    },
    "legacy_lib_dir": "",
    "legacy_lib_list": [],
    "meta": {
      "version": 1
    },
    "net_format_name": "",
    "page_layout_descr_file": "",
    "plot_directory": "",
    "space_save_all_events": true,
    "spice_current_sheet_as_root": false,
    "spice_external_command": "spice \"%I\"",
    "spice_model_current_sheet_as_root": true,
    "spice_save_all_currents": false,
    "spice_save_all_dissipations": false,
    "spice_save_all_voltages": false,
    "subpart_first_id": 65,
    "subpart_id_separator": 0
  },
  "sheets": ["""
]
data_pro.append(f"""    [
      "{rootid}",
      "Root"
    ],""")

sheets = []
for name, settings in setup.items():
    sub_board_data_old = open(f"{settings['path']}/{name}/{name}.kicad_pcb", "r").read()
    for num, suuid in settings["sheets"].items():
        sheets.append(f"""    [
      "{suuid}",
      "{name}"
    ]""")

    data_pro.append(",\n".join(sheets))

data_pro.append("""  ],
  "text_variables": {}
}""")

open("rioboard.kicad_pro", "w").write("\n".join(data_pro))


data_prl = """{
  "board": {
    "active_layer": 0,
    "active_layer_preset": "All Layers",
    "auto_track_width": false,
    "hidden_netclasses": [],
    "hidden_nets": [],
    "high_contrast_mode": 0,
    "net_color_mode": 1,
    "opacity": {
      "images": 1.0,
      "pads": 1.0,
      "shapes": 1.0,
      "tracks": 1.0,
      "vias": 1.0,
      "zones": 1.0
    },
    "selection_filter": {
      "dimensions": true,
      "footprints": true,
      "graphics": true,
      "keepouts": true,
      "lockedItems": false,
      "otherItems": true,
      "pads": true,
      "text": true,
      "tracks": true,
      "vias": true,
      "zones": true
    },
    "visible_items": [
      "vias",
      "footprint_text",
      "footprint_anchors",
      "ratsnest",
      "grid",
      "footprints_front",
      "footprints_back",
      "footprint_values",
      "footprint_references",
      "tracks",
      "drc_errors",
      "drawing_sheet",
      "bitmaps",
      "pads",
      "zones",
      "drc_warnings",
      "locked_item_shadows",
      "conflict_shadows",
      "shapes"
    ],
    "visible_layers": "ffffffff_ffffffff_ffffffff_ffffffff",
    "zone_display_mode": 0
  },
  "git": {
    "repo_type": "",
    "repo_username": "",
    "ssh_key": ""
  },
  "meta": {
    "filename": "rioboard.kicad_prl",
    "version": 5
  },
  "net_inspector_panel": {
    "col_hidden": [
      false,
      false,
      false,
      false,
      false,
      false,
      false,
      false,
      false,
      false
    ],
    "col_order": [
      0,
      1,
      2,
      3,
      4,
      5,
      6,
      7,
      8,
      9
    ],
    "col_widths": [
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0
    ],
    "custom_group_rules": [],
    "expanded_rows": [],
    "filter_by_net_name": true,
    "filter_by_netclass": true,
    "filter_text": "",
    "group_by_constraint": false,
    "group_by_netclass": false,
    "show_unconnected_nets": false,
    "show_zero_pad_nets": false,
    "sort_ascending": true,
    "sorting_column": 0
  },
  "open_jobsets": [],
  "project": {
    "files": []
  },
  "schematic": {
    "selection_filter": {
      "graphics": true,
      "images": true,
      "labels": true,
      "lockedItems": false,
      "otherItems": true,
      "pins": true,
      "symbols": true,
      "text": true,
      "wires": true
    }
  }
}"""
open("rioboard.kicad_prl", "w").write("\n".join(data_prl))
