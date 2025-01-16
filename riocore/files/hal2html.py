import sys
import re

# https://forum.linuxcnc.org/24-hal-components/49344-syntax-highlighting-for-hal-in-nano
style = """
## Syntax highlighting for HAL files.
# Note if editing: Precedence of regex impacts how highlighting is displayed.

syntax hal "\.[hH]{1}[aA]{1}[lL]{1}$"
comment "#"

# Formatting for precedence.
color italic,normal "^(un)?load.*"

# Read/write names.
color lightmagenta "\b(read|write)\b"

# Thread names.
color lightblue "(servo|base)\-thread"

# Commands.
color italic,lightblue "^(unalias|unlinkp|unload|unloadrt|unloadusr|unlock|addf|alias|delf|delsig|getp|gets|ptype|stype|help|linkpp|linkps|inksp|list|loadrt|loadusr|lock|net|newsig|save|setp|sets|show|source|start|status|stop|waitusr)"

# Components.
color lightred "(motion|iocontrol|classicladder|halui|stepgen|encoder|parport|pid|siggen|spindle|stepgen|supply|func|riov|rio)\."
# add hal_.+[\w] ?


# Axis labels and numaric IDs.
#color lightblue "((\.|-|[\w])(x|y|z|a|b|c|u|v|w|s|[\d]{1,2}))+(\.|\,|-|[\w]|$)"

# Formatting for precedence/correction.
color normal "(\.|-|_|,|=)"

# INI references.
color italic,lightyellow "\[\S+]\(\S+\)"
color italic,lightgreen "\[\S+\]"
color lightyellow "\][A-Z0-9\_]+"
color cyan "(\[|\]|\(|\))"

# Thread names.
color lightblue "(servo|base)\-thread"

# Strings.
#color lightcyan start="\"" end="\""

# Numbers and booleans.
color lightmagenta "\s\-?[\d]+(\.[\d]+)?"
color lightmagenta "(true|false)"

# Comments.
color gray "#.*"

# Reminders.
color bold,brightblack,yellow "\<;(FIXME|TODO|XXX)\>"

"""

haldata = open(sys.argv[1]).read()
hallines = haldata.split("\n")
for line in style.split("\n"):
    if line.startswith("color "):
        parts = line.split(" ", 2)
        style = parts[1]
        regex = parts[2].split('"')[1]
        color = None
        for part in style.split(","):
            if part not in {"normal", "italic"}:
                color = part
        if color:
            for ln, halline in enumerate(hallines):
                if halline.startswith("#"):
                    continue
                replaces = {}
                for match in re.finditer(regex, hallines[ln]):
                    string = match.group()
                    replaces[string] = f'<i style="color:{color}">{string}</i>'
                for old, new in replaces.items():
                    hallines[ln] = hallines[ln].replace(old, new)

print("""<html>
<style>
 body {
  color: white;
  background-color: #333333;
} 
</style>
""")
for line in hallines:
    if line.startswith("#"):
        print(f'<i style="color:lightgray">{line}</i><br/>')
    else:
        print(f"{line}<br/>")
print("</html>")
