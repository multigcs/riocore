import os

from .cbase import cbase

riocore_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class component(cbase):
    filename_functions = "hal_functions.c"
    rtapi_mode = True
    typemap = {
        "float": "hal_float_t",
        "bool": "hal_bit_t",
        "s32": "hal_s32_t",
        "u32": "hal_u32_t",
    }
    printf = "rtapi_print"
    header_list = [
        "rtapi.h",
        "rtapi_app.h",
        "hal.h",
        "unistd.h",
        "stdlib.h",
        "stdbool.h",
        "stdio.h",
        "string.h",
        "math.h",
        "sys/mman.h",
        "errno.h",
    ]
    module_info = {
        "AUTHOR": "Oliver Dippel",
        "DESCRIPTION": "Driver for RIO FPGA boards",
        "LICENSE": "GPL v2",
    }

    def __init__(self, project, instance):
        self.project = project
        self.instance = instance
        self.prefix = instance.hal_prefix
        self.base_path = os.path.join(self.project.config["output_path"], "LinuxCNC")
        self.component_path = f"{self.base_path}"
        os.makedirs(self.component_path, exist_ok=True)
        output = self.mainc()
        open(os.path.join(self.component_path, f"riocomp-{instance.instances_name}.c"), "w").write("\n".join(output))

    def vinit(self, vname, vtype, halstr=None, vdir="input"):
        vtype = {"bool": "bit"}.get(vtype, vtype)
        direction = {"output": "IN", "input": "OUT", "inout": "IO"}.get(vdir, vdir)
        return f'    if (retval = hal_pin_{vtype}_newf(HAL_{direction}, &(data->{vname}), comp_id, "{halstr}") != 0) error_handler(retval);'
