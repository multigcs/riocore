
import sys
import time
import ctypes
import pathlib

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
    def __init__(self):
        libname = pathlib.Path().absolute() / "librio.so"
        self.rio = ctypes.CDLL(libname)
        self.rio.init.restype = ctypes.POINTER(RioData)
        p_args = list((arg.encode() for arg in sys.argv))
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

    def data_info(self):
        return {
            "SIGIN_BOARD0_BITIN0_BIT": {
                "direction": "input",
                "halname": "board0.bitin0.bit",
                "netname": "None",
                "type": "bool",
                "subs": {
                    "SIGIN_BOARD0_BITIN0_BIT_not": {"type": "bool"},
                },
            },
            "SIGOUT_BOARD0_BITOUT0_BIT": {
                "direction": "output",
                "halname": "board0.bitout0.bit",
                "netname": "None",
                "type": "bool",
                "subs": {
                },
            },
            "SIGOUT_BOARD0_BITOUT1_BIT": {
                "direction": "output",
                "halname": "board0.bitout1.bit",
                "netname": "None",
                "type": "bool",
                "subs": {
                },
            },
            "SIGOUT_BOARD0_PWMOUT0_DTY": {
                "direction": "output",
                "halname": "board0.pwmout0.dty",
                "netname": "None",
                "type": "float",
                "subs": {
                    "SIGOUT_BOARD0_PWMOUT0_DTY_SCALE": {"type": "float"},
                    "SIGOUT_BOARD0_PWMOUT0_DTY_OFFSET": {"type": "float"},
                },
            },
            "SIGOUT_BOARD0_PWMOUT0_ENABLE": {
                "direction": "output",
                "halname": "board0.pwmout0.enable",
                "netname": "None",
                "type": "bool",
                "subs": {
                },
            },
            "SIGOUT_BOARD0_STEPDIR0_VELOCITY": {
                "direction": "output",
                "halname": "board0.stepdir0.velocity",
                "netname": "None",
                "type": "float",
                "subs": {
                    "SIGOUT_BOARD0_STEPDIR0_VELOCITY_SCALE": {"type": "float"},
                    "SIGOUT_BOARD0_STEPDIR0_VELOCITY_OFFSET": {"type": "float"},
                },
            },
            "SIGIN_BOARD0_STEPDIR0_POSITION": {
                "direction": "input",
                "halname": "board0.stepdir0.position",
                "netname": "None",
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
                "direction": "output",
                "halname": "board0.stepdir0.enable",
                "netname": "None",
                "type": "bool",
                "subs": {
                },
            },
        }
