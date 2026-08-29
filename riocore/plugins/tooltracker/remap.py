import emccanon
import linuxcnc

from interpreter import INTERP_OK
from tttable import tools_load

throw_exceptions = 1


def prepare(self, **words):
    cblock = self.blocks[self.remap_level]
    if not cblock.t_flag:
        return "T requires a tool number"
    tool = cblock.t_number
    if tool == 0:
        return INTERP_OK

    (status, pocket) = self.find_tool_pocket(tool)
    if status != INTERP_OK:
        return "T%d: pocket not found" % (tool)

    # load tooltable
    stat = linuxcnc.stat()
    stat.poll()
    inifile = linuxcnc.ini(stat.ini_filename)
    tool_table = inifile.find("EMCIO", "TOOL_TABLE")
    tools = tools_load(tool_table)

    # select usable tool or sister
    load = tool
    if load in tools:
        found = False
        for level in ("warning", "critical"):
            select = tools[load]
            while select:
                if select["timer"] < select[level]:
                    # found usable tool
                    pocket = int(select["P"])
                    tool = int(select["T"])
                    print(f"tooltracker-remap: using tool {tool} in pocket {pocket}")
                    found = True
                    select = None
                else:
                    print(f"tooltracker-remap: tool {select['T']} in pocket {select['P']} is in {level} state")
                    if int(select["sister"]):
                        select = tools[int(select["sister"])]
                        print(f"tooltracker-remap: found sister {select['T']} in pocket {select['P']}")
                    else:
                        select = None
            if found:
                if level == "critical":
                    print("tooltracker-remap: used tool is in critical state !!!")
                break

        if not found:
            print("tooltracker-remap: no usable tool found")

    self.selected_tool = tool
    self.selected_pocket = pocket
    emccanon.SELECT_TOOL(tool)
    return INTERP_OK
