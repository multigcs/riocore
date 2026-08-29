import re


def tools_load(filename):
    tools = {}
    updated = False
    with open(filename, "r") as tooltable:
        for line in tooltable.read().split("\n"):
            parts = line.strip().split(";", 1)
            if parts[0]:
                comment = ""
                timer = 0
                warning = 3600
                critical = 4800
                sister = 0
                if len(parts) > 1:
                    comment = parts[1].strip()
                    res = re.findall("TT:[0-9]+/[0-9]+/[0-9]+/[0-9]+", comment, re.IGNORECASE)
                    if res:
                        timer, warning, critical, sister = res[0][3:].split("/")
                        comment = comment.replace(res[0], "").strip()
                    else:
                        updated = True
                else:
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
                    "timer": int(timer),
                    "warning": int(warning),
                    "critical": int(critical),
                    "sister": int(sister),
                }
                for col in cols:
                    vtype = col[0]
                    value = col[1:]
                    tool_data[vtype] = value
                if tool_data["T"] != "0":
                    tools[int(tool_data["T"])] = tool_data
    if updated:
        tools_save(filename, tools)
    return tools


def tools_save(filename, tools):
    with open(filename, "w") as tooltable:
        for tool_num, tool_data in tools.items():
            line = []
            for key, value in tool_data.items():
                if key in {"comment", "timer", "warning", "critical", "sister"}:
                    continue
                line.append(f"{key}{value}")
            line.append(f"; {tool_data['comment']} TT:{tool_data['timer']}/{tool_data['warning']}/{tool_data['critical']}/{tool_data['sister']}")
            tooltable.write(" ".join(line))
            tooltable.write("\n")
