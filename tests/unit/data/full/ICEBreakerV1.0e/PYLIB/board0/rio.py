
import os
import ctypes

class RioData(ctypes.Structure):
    _fields_ = [
      ("sys_enable", ctypes.POINTER(ctypes.c_bool)),
      ("sys_enable_request", ctypes.POINTER(ctypes.c_bool)),
      ("sys_status", ctypes.POINTER(ctypes.c_bool)),
      ("machine_on", ctypes.POINTER(ctypes.c_bool)),
      ("sys_simulation", ctypes.POINTER(ctypes.c_bool)),
      ("fpga_timestamp", ctypes.POINTER(ctypes.c_int)),
      ("duration", ctypes.POINTER(ctypes.c_float)),
      # signals
      ("SIGOUT_BOARD0_STEPDIR0_VELOCITY", ctypes.POINTER(ctypes.c_float)),
      ("SIGOUT_BOARD0_STEPDIR0_VELOCITY_SCALE", ctypes.POINTER(ctypes.c_float)),
      ("SIGOUT_BOARD0_STEPDIR0_VELOCITY_OFFSET", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_BOARD0_STEPDIR0_POSITION", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_BOARD0_STEPDIR0_POSITION_ABS", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_BOARD0_STEPDIR0_POSITION_S32", ctypes.POINTER(ctypes.c_int32)),
      ("SIGIN_BOARD0_STEPDIR0_POSITION_U32_ABS", ctypes.POINTER(ctypes.c_uint32)),
      ("SIGIN_BOARD0_STEPDIR0_POSITION_SCALE", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_BOARD0_STEPDIR0_POSITION_OFFSET", ctypes.POINTER(ctypes.c_float)),
      ("SIGOUT_BOARD0_STEPDIR0_ENABLE", ctypes.POINTER(ctypes.c_bool)),
      ("SIGOUT_BOARD0_STEPDIR1_VELOCITY", ctypes.POINTER(ctypes.c_float)),
      ("SIGOUT_BOARD0_STEPDIR1_VELOCITY_SCALE", ctypes.POINTER(ctypes.c_float)),
      ("SIGOUT_BOARD0_STEPDIR1_VELOCITY_OFFSET", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_BOARD0_STEPDIR1_POSITION", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_BOARD0_STEPDIR1_POSITION_ABS", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_BOARD0_STEPDIR1_POSITION_S32", ctypes.POINTER(ctypes.c_int32)),
      ("SIGIN_BOARD0_STEPDIR1_POSITION_U32_ABS", ctypes.POINTER(ctypes.c_uint32)),
      ("SIGIN_BOARD0_STEPDIR1_POSITION_SCALE", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_BOARD0_STEPDIR1_POSITION_OFFSET", ctypes.POINTER(ctypes.c_float)),
      ("SIGOUT_BOARD0_STEPDIR1_ENABLE", ctypes.POINTER(ctypes.c_bool)),
      ("SIGIN_BOARD0_BITIN0_BIT", ctypes.POINTER(ctypes.c_bool)),
      ("SIGIN_BOARD0_BITIN0_BIT_not", ctypes.POINTER(ctypes.c_bool)),
      ("SIGOUT_BOARD0_STEPDIR2_VELOCITY", ctypes.POINTER(ctypes.c_float)),
      ("SIGOUT_BOARD0_STEPDIR2_VELOCITY_SCALE", ctypes.POINTER(ctypes.c_float)),
      ("SIGOUT_BOARD0_STEPDIR2_VELOCITY_OFFSET", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_BOARD0_STEPDIR2_POSITION", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_BOARD0_STEPDIR2_POSITION_ABS", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_BOARD0_STEPDIR2_POSITION_S32", ctypes.POINTER(ctypes.c_int32)),
      ("SIGIN_BOARD0_STEPDIR2_POSITION_U32_ABS", ctypes.POINTER(ctypes.c_uint32)),
      ("SIGIN_BOARD0_STEPDIR2_POSITION_SCALE", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_BOARD0_STEPDIR2_POSITION_OFFSET", ctypes.POINTER(ctypes.c_float)),
      ("SIGOUT_BOARD0_STEPDIR2_ENABLE", ctypes.POINTER(ctypes.c_bool)),
      ("SIGOUT_BOARD0_BITOUT0_BIT", ctypes.POINTER(ctypes.c_bool)),
      ("SIGOUT_BOARD0_BITOUT1_BIT", ctypes.POINTER(ctypes.c_bool)),
      ("SIGIN_BOARD0_BITIN1_BIT", ctypes.POINTER(ctypes.c_bool)),
      ("SIGIN_BOARD0_BITIN1_BIT_not", ctypes.POINTER(ctypes.c_bool)),
      ("SIGIN_BOARD0_BITIN2_BIT", ctypes.POINTER(ctypes.c_bool)),
      ("SIGIN_BOARD0_BITIN2_BIT_not", ctypes.POINTER(ctypes.c_bool)),
      ("SIGIN_BOARD0_BITIN3_BIT", ctypes.POINTER(ctypes.c_bool)),
      ("SIGIN_BOARD0_BITIN3_BIT_not", ctypes.POINTER(ctypes.c_bool)),
      ("SIGIN_BOARD0_BITIN4_BIT", ctypes.POINTER(ctypes.c_bool)),
      ("SIGIN_BOARD0_BITIN4_BIT_not", ctypes.POINTER(ctypes.c_bool)),
      ("SIGIN_BOARD0_BITIN5_BIT", ctypes.POINTER(ctypes.c_bool)),
      ("SIGIN_BOARD0_BITIN5_BIT_not", ctypes.POINTER(ctypes.c_bool)),
      # raw variables
      ("VAROUT32_STEPDIR0_VELOCITY", ctypes.c_uint32),
      ("VARIN32_STEPDIR0_POSITION", ctypes.c_uint32),
      ("VAROUT32_STEPDIR1_VELOCITY", ctypes.c_uint32),
      ("VARIN32_STEPDIR1_POSITION", ctypes.c_uint32),
      ("VAROUT32_STEPDIR2_VELOCITY", ctypes.c_uint32),
      ("VARIN32_STEPDIR2_POSITION", ctypes.c_uint32),
      ("VAROUT1_STEPDIR0_ENABLE", ctypes.c_bool),
      ("VAROUT1_STEPDIR1_ENABLE", ctypes.c_bool),
      ("VARIN1_BITIN0_BIT", ctypes.c_bool),
      ("VAROUT1_STEPDIR2_ENABLE", ctypes.c_bool),
      ("VAROUT1_BITOUT0_BIT", ctypes.c_bool),
      ("VAROUT1_BITOUT1_BIT", ctypes.c_bool),
      ("VARIN1_BITIN1_BIT", ctypes.c_bool),
      ("VARIN1_BITIN2_BIT", ctypes.c_bool),
      ("VARIN1_BITIN3_BIT", ctypes.c_bool),
      ("VARIN1_BITIN4_BIT", ctypes.c_bool),
      ("VARIN1_BITIN5_BIT", ctypes.c_bool),
    ]

class RioWrapper():
    def __init__(self, argv=[]):
        libname = os.path.join(os.path.dirname(__file__), "librio.so")
        self.rio = ctypes.CDLL(libname)
        self.rio.init.restype = ctypes.POINTER(RioData)
        p_args = list((arg.encode() for arg in argv))
        args = (ctypes.c_char_p * len(p_args))(*p_args)
        self.rio_data = self.rio.init(len(args), args)

    def rio_readwrite(self):
     self.rio.rio_readwrite(None, 0)

    def data_get(self, name):
        var = getattr(self.rio_data.contents, name)
        if hasattr(var, "contents"):
            return var.contents.value
        return var

    def data_set(self, name, value):
        var = getattr(self.rio_data.contents, name)
        if hasattr(var, "contents"):
            var.contents.value = value
        var = value

    def plugin_info(self):
        return {
            "board0": {
                "type": "fpga",
                "title": "board0",
                "is_joint": False,
                "variables": [
                ],
            },
            "w55000": {
                "type": "w5500",
                "title": "w55000",
                "is_joint": False,
                "variables": [
                ],
            },
            "stepdir0": {
                "type": "stepdir",
                "title": "stepdir0",
                "is_joint": True,
                "variables": [
                    "SIGOUT_BOARD0_STEPDIR0_VELOCITY",
                    "SIGIN_BOARD0_STEPDIR0_POSITION",
                    "SIGOUT_BOARD0_STEPDIR0_ENABLE",
                ],
            },
            "stepdir1": {
                "type": "stepdir",
                "title": "stepdir1",
                "is_joint": True,
                "variables": [
                    "SIGOUT_BOARD0_STEPDIR1_VELOCITY",
                    "SIGIN_BOARD0_STEPDIR1_POSITION",
                    "SIGOUT_BOARD0_STEPDIR1_ENABLE",
                ],
            },
            "blink0": {
                "type": "blink",
                "title": "blink0",
                "is_joint": False,
                "variables": [
                ],
            },
            "bitin0": {
                "type": "bitin",
                "title": "bitin0",
                "is_joint": False,
                "variables": [
                    "SIGIN_BOARD0_BITIN0_BIT",
                ],
            },
            "stepdir2": {
                "type": "stepdir",
                "title": "stepdir2",
                "is_joint": True,
                "variables": [
                    "SIGOUT_BOARD0_STEPDIR2_VELOCITY",
                    "SIGIN_BOARD0_STEPDIR2_POSITION",
                    "SIGOUT_BOARD0_STEPDIR2_ENABLE",
                ],
            },
            "bitout0": {
                "type": "bitout",
                "title": "bitout0",
                "is_joint": False,
                "variables": [
                    "SIGOUT_BOARD0_BITOUT0_BIT",
                ],
            },
            "bitout1": {
                "type": "bitout",
                "title": "bitout1",
                "is_joint": False,
                "variables": [
                    "SIGOUT_BOARD0_BITOUT1_BIT",
                ],
            },
            "bitin1": {
                "type": "bitin",
                "title": "bitin1",
                "is_joint": False,
                "variables": [
                    "SIGIN_BOARD0_BITIN1_BIT",
                ],
            },
            "bitin2": {
                "type": "bitin",
                "title": "bitin2",
                "is_joint": False,
                "variables": [
                    "SIGIN_BOARD0_BITIN2_BIT",
                ],
            },
            "bitin3": {
                "type": "bitin",
                "title": "bitin3",
                "is_joint": False,
                "variables": [
                    "SIGIN_BOARD0_BITIN3_BIT",
                ],
            },
            "bitin4": {
                "type": "bitin",
                "title": "bitin4",
                "is_joint": False,
                "variables": [
                    "SIGIN_BOARD0_BITIN4_BIT",
                ],
            },
            "bitin5": {
                "type": "bitin",
                "title": "bitin5",
                "is_joint": False,
                "variables": [
                    "SIGIN_BOARD0_BITIN5_BIT",
                ],
            },
        }

    def data_info(self):
        return {
            "SIGOUT_BOARD0_STEPDIR0_VELOCITY": {
                "plugin": "stepdir0",
                "direction": "output",
                "signal_name": "velocity",
                "userconfig": {},
                "halname": "board0.stepdir0.velocity",
                "netname": "",
                "type": "float",
                "subs": {
                    "SIGOUT_BOARD0_STEPDIR0_VELOCITY_SCALE": {"type": "float"},
                    "SIGOUT_BOARD0_STEPDIR0_VELOCITY_OFFSET": {"type": "float"},
                },
            },
            "SIGIN_BOARD0_STEPDIR0_POSITION": {
                "plugin": "stepdir0",
                "direction": "input",
                "signal_name": "position",
                "userconfig": {},
                "halname": "board0.stepdir0.position",
                "netname": "",
                "type": "float",
                "subs": {
                    "SIGIN_BOARD0_STEPDIR0_POSITION_ABS": {"type": "float"},
                    "SIGIN_BOARD0_STEPDIR0_POSITION_S32": {"type": "int32"},
                    "SIGIN_BOARD0_STEPDIR0_POSITION_U32_ABS": {"type": "uint32"},
                    "SIGIN_BOARD0_STEPDIR0_POSITION_SCALE": {"type": "float"},
                    "SIGIN_BOARD0_STEPDIR0_POSITION_OFFSET": {"type": "float"},
                },
            },
            "SIGOUT_BOARD0_STEPDIR0_ENABLE": {
                "plugin": "stepdir0",
                "direction": "output",
                "signal_name": "enable",
                "userconfig": {},
                "halname": "board0.stepdir0.enable",
                "netname": "",
                "type": "bool",
                "subs": {
                },
            },
            "SIGOUT_BOARD0_STEPDIR1_VELOCITY": {
                "plugin": "stepdir1",
                "direction": "output",
                "signal_name": "velocity",
                "userconfig": {},
                "halname": "board0.stepdir1.velocity",
                "netname": "",
                "type": "float",
                "subs": {
                    "SIGOUT_BOARD0_STEPDIR1_VELOCITY_SCALE": {"type": "float"},
                    "SIGOUT_BOARD0_STEPDIR1_VELOCITY_OFFSET": {"type": "float"},
                },
            },
            "SIGIN_BOARD0_STEPDIR1_POSITION": {
                "plugin": "stepdir1",
                "direction": "input",
                "signal_name": "position",
                "userconfig": {},
                "halname": "board0.stepdir1.position",
                "netname": "",
                "type": "float",
                "subs": {
                    "SIGIN_BOARD0_STEPDIR1_POSITION_ABS": {"type": "float"},
                    "SIGIN_BOARD0_STEPDIR1_POSITION_S32": {"type": "int32"},
                    "SIGIN_BOARD0_STEPDIR1_POSITION_U32_ABS": {"type": "uint32"},
                    "SIGIN_BOARD0_STEPDIR1_POSITION_SCALE": {"type": "float"},
                    "SIGIN_BOARD0_STEPDIR1_POSITION_OFFSET": {"type": "float"},
                },
            },
            "SIGOUT_BOARD0_STEPDIR1_ENABLE": {
                "plugin": "stepdir1",
                "direction": "output",
                "signal_name": "enable",
                "userconfig": {},
                "halname": "board0.stepdir1.enable",
                "netname": "",
                "type": "bool",
                "subs": {
                },
            },
            "SIGIN_BOARD0_BITIN0_BIT": {
                "plugin": "bitin0",
                "direction": "input",
                "signal_name": "bit",
                "userconfig": {},
                "halname": "board0.bitin0.bit",
                "netname": "",
                "type": "bool",
                "subs": {
                    "SIGIN_BOARD0_BITIN0_BIT_not": {"type": "bool"},
                },
            },
            "SIGOUT_BOARD0_STEPDIR2_VELOCITY": {
                "plugin": "stepdir2",
                "direction": "output",
                "signal_name": "velocity",
                "userconfig": {},
                "halname": "board0.stepdir2.velocity",
                "netname": "",
                "type": "float",
                "subs": {
                    "SIGOUT_BOARD0_STEPDIR2_VELOCITY_SCALE": {"type": "float"},
                    "SIGOUT_BOARD0_STEPDIR2_VELOCITY_OFFSET": {"type": "float"},
                },
            },
            "SIGIN_BOARD0_STEPDIR2_POSITION": {
                "plugin": "stepdir2",
                "direction": "input",
                "signal_name": "position",
                "userconfig": {},
                "halname": "board0.stepdir2.position",
                "netname": "",
                "type": "float",
                "subs": {
                    "SIGIN_BOARD0_STEPDIR2_POSITION_ABS": {"type": "float"},
                    "SIGIN_BOARD0_STEPDIR2_POSITION_S32": {"type": "int32"},
                    "SIGIN_BOARD0_STEPDIR2_POSITION_U32_ABS": {"type": "uint32"},
                    "SIGIN_BOARD0_STEPDIR2_POSITION_SCALE": {"type": "float"},
                    "SIGIN_BOARD0_STEPDIR2_POSITION_OFFSET": {"type": "float"},
                },
            },
            "SIGOUT_BOARD0_STEPDIR2_ENABLE": {
                "plugin": "stepdir2",
                "direction": "output",
                "signal_name": "enable",
                "userconfig": {},
                "halname": "board0.stepdir2.enable",
                "netname": "",
                "type": "bool",
                "subs": {
                },
            },
            "SIGOUT_BOARD0_BITOUT0_BIT": {
                "plugin": "bitout0",
                "direction": "output",
                "signal_name": "bit",
                "userconfig": {},
                "halname": "board0.bitout0.bit",
                "netname": "",
                "type": "bool",
                "subs": {
                },
            },
            "SIGOUT_BOARD0_BITOUT1_BIT": {
                "plugin": "bitout1",
                "direction": "output",
                "signal_name": "bit",
                "userconfig": {},
                "halname": "board0.bitout1.bit",
                "netname": "",
                "type": "bool",
                "subs": {
                },
            },
            "SIGIN_BOARD0_BITIN1_BIT": {
                "plugin": "bitin1",
                "direction": "input",
                "signal_name": "bit",
                "userconfig": {},
                "halname": "board0.bitin1.bit",
                "netname": "",
                "type": "bool",
                "subs": {
                    "SIGIN_BOARD0_BITIN1_BIT_not": {"type": "bool"},
                },
            },
            "SIGIN_BOARD0_BITIN2_BIT": {
                "plugin": "bitin2",
                "direction": "input",
                "signal_name": "bit",
                "userconfig": {},
                "halname": "board0.bitin2.bit",
                "netname": "",
                "type": "bool",
                "subs": {
                    "SIGIN_BOARD0_BITIN2_BIT_not": {"type": "bool"},
                },
            },
            "SIGIN_BOARD0_BITIN3_BIT": {
                "plugin": "bitin3",
                "direction": "input",
                "signal_name": "bit",
                "userconfig": {},
                "halname": "board0.bitin3.bit",
                "netname": "",
                "type": "bool",
                "subs": {
                    "SIGIN_BOARD0_BITIN3_BIT_not": {"type": "bool"},
                },
            },
            "SIGIN_BOARD0_BITIN4_BIT": {
                "plugin": "bitin4",
                "direction": "input",
                "signal_name": "bit",
                "userconfig": {},
                "halname": "board0.bitin4.bit",
                "netname": "",
                "type": "bool",
                "subs": {
                    "SIGIN_BOARD0_BITIN4_BIT_not": {"type": "bool"},
                },
            },
            "SIGIN_BOARD0_BITIN5_BIT": {
                "plugin": "bitin5",
                "direction": "input",
                "signal_name": "bit",
                "userconfig": {},
                "halname": "board0.bitin5.bit",
                "netname": "",
                "type": "bool",
                "subs": {
                    "SIGIN_BOARD0_BITIN5_BIT_not": {"type": "bool"},
                },
            },
        }
