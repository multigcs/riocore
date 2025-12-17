
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
      ("SIGIN_BOARD0_BITIN0_BIT", ctypes.POINTER(ctypes.c_bool)),
      ("SIGIN_BOARD0_BITIN0_BIT_not", ctypes.POINTER(ctypes.c_bool)),
      ("SIGOUT_BOARD0_BITOUT0_BIT", ctypes.POINTER(ctypes.c_bool)),
      ("SIGOUT_BOARD0_BITOUT1_BIT", ctypes.POINTER(ctypes.c_bool)),
      ("SIGOUT_BOARD0_PWMOUT0_DTY", ctypes.POINTER(ctypes.c_float)),
      ("SIGOUT_BOARD0_PWMOUT0_DTY_SCALE", ctypes.POINTER(ctypes.c_float)),
      ("SIGOUT_BOARD0_PWMOUT0_DTY_OFFSET", ctypes.POINTER(ctypes.c_float)),
      ("SIGOUT_BOARD0_PWMOUT0_ENABLE", ctypes.POINTER(ctypes.c_bool)),
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
      # raw variables
      ("VAROUT32_PWMOUT0_DTY", ctypes.c_uint32),
      ("VAROUT32_STEPDIR0_VELOCITY", ctypes.c_uint32),
      ("VARIN32_STEPDIR0_POSITION", ctypes.c_uint32),
      ("VARIN1_BITIN0_BIT", ctypes.c_bool),
      ("VAROUT1_BITOUT0_BIT", ctypes.c_bool),
      ("VAROUT1_BITOUT1_BIT", ctypes.c_bool),
      ("VAROUT1_PWMOUT0_ENABLE", ctypes.c_bool),
      ("VAROUT1_STEPDIR0_ENABLE", ctypes.c_bool),
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
            "pwmout0": {
                "type": "pwmout",
                "title": "pwmout0",
                "is_joint": False,
                "variables": [
                    "SIGOUT_BOARD0_PWMOUT0_DTY",
                    "SIGOUT_BOARD0_PWMOUT0_ENABLE",
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
        }

    def data_info(self):
        return {
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
            "SIGOUT_BOARD0_PWMOUT0_DTY": {
                "plugin": "pwmout0",
                "direction": "output",
                "signal_name": "dty",
                "userconfig": {},
                "halname": "board0.pwmout0.dty",
                "netname": "",
                "type": "float",
                "subs": {
                    "SIGOUT_BOARD0_PWMOUT0_DTY_SCALE": {"type": "float"},
                    "SIGOUT_BOARD0_PWMOUT0_DTY_OFFSET": {"type": "float"},
                },
            },
            "SIGOUT_BOARD0_PWMOUT0_ENABLE": {
                "plugin": "pwmout0",
                "direction": "output",
                "signal_name": "enable",
                "userconfig": {},
                "halname": "board0.pwmout0.enable",
                "netname": "",
                "type": "bool",
                "subs": {
                },
            },
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
        }
