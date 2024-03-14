#!/usr/bin/env python3
#
# wget https://raw.githubusercontent.com/LinuxCNC/linuxcnc/v2.9.2/docs/src/config/ini-config.adoc
#

data = open("ini-config.adoc", "r").read()


help_text = {
    "INI": {},
}


ini_section = None

for line in data.split("\n"):
    if line.startswith("[[sub:ini:sec:"):
        ini_section = line.split(":")[-1].strip("]").upper().replace("-", "_")
        help_text["INI"][ini_section] = {}

    elif line.startswith("[["):
        ini_section = None

    elif ini_section:
        if line.startswith("* `"):
            var_name = line.split()[1].strip("`")
            text_start = line.find("- ")
            if text_start > 0:
                text = line[text_start + 2 :]
                if var_name not in help_text["INI"][ini_section]:
                    help_text["INI"][ini_section][var_name] = text
                    print(ini_section, var_name, " ---- ", text)


print(help_text)
