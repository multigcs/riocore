
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
      # multiplexer
      ("MULTIPLEXER_INPUT_VALUE", ctypes.c_float),
      ("MULTIPLEXER_INPUT_ID", ctypes.c_char),
      # signals
      ("SIGIN_FPGA0_MODBUS0_TEMPERATURE", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_FPGA0_MODBUS0_TEMPERATURE_ABS", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_FPGA0_MODBUS0_TEMPERATURE_S32", ctypes.POINTER(ctypes.c_int32)),
      ("SIGIN_FPGA0_MODBUS0_TEMPERATURE_U32_ABS", ctypes.POINTER(ctypes.c_uint32)),
      ("SIGIN_FPGA0_MODBUS0_TEMPERATURE_SCALE", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_FPGA0_MODBUS0_TEMPERATURE_OFFSET", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_FPGA0_I2CBUS0_LM75_0_TEMP", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_FPGA0_I2CBUS0_LM75_0_TEMP_ABS", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_FPGA0_I2CBUS0_LM75_0_TEMP_S32", ctypes.POINTER(ctypes.c_int32)),
      ("SIGIN_FPGA0_I2CBUS0_LM75_0_TEMP_U32_ABS", ctypes.POINTER(ctypes.c_uint32)),
      ("SIGIN_FPGA0_I2CBUS0_LM75_0_TEMP_SCALE", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_FPGA0_I2CBUS0_LM75_0_TEMP_OFFSET", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_FPGA0_I2CBUS0_LM75_0_VALID", ctypes.POINTER(ctypes.c_bool)),
      ("SIGIN_FPGA0_I2CBUS0_LM75_0_VALID_not", ctypes.POINTER(ctypes.c_bool)),
      ("SIGOUT_FPGA0_STEPDIR0_VELOCITY", ctypes.POINTER(ctypes.c_float)),
      ("SIGOUT_FPGA0_STEPDIR0_VELOCITY_SCALE", ctypes.POINTER(ctypes.c_float)),
      ("SIGOUT_FPGA0_STEPDIR0_VELOCITY_OFFSET", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_FPGA0_STEPDIR0_POSITION", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_FPGA0_STEPDIR0_POSITION_ABS", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_FPGA0_STEPDIR0_POSITION_S32", ctypes.POINTER(ctypes.c_int32)),
      ("SIGIN_FPGA0_STEPDIR0_POSITION_U32_ABS", ctypes.POINTER(ctypes.c_uint32)),
      ("SIGIN_FPGA0_STEPDIR0_POSITION_SCALE", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_FPGA0_STEPDIR0_POSITION_OFFSET", ctypes.POINTER(ctypes.c_float)),
      ("SIGOUT_FPGA0_STEPDIR0_ENABLE", ctypes.POINTER(ctypes.c_bool)),
      ("SIGOUT_FPGA0_STEPDIR1_VELOCITY", ctypes.POINTER(ctypes.c_float)),
      ("SIGOUT_FPGA0_STEPDIR1_VELOCITY_SCALE", ctypes.POINTER(ctypes.c_float)),
      ("SIGOUT_FPGA0_STEPDIR1_VELOCITY_OFFSET", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_FPGA0_STEPDIR1_POSITION", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_FPGA0_STEPDIR1_POSITION_ABS", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_FPGA0_STEPDIR1_POSITION_S32", ctypes.POINTER(ctypes.c_int32)),
      ("SIGIN_FPGA0_STEPDIR1_POSITION_U32_ABS", ctypes.POINTER(ctypes.c_uint32)),
      ("SIGIN_FPGA0_STEPDIR1_POSITION_SCALE", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_FPGA0_STEPDIR1_POSITION_OFFSET", ctypes.POINTER(ctypes.c_float)),
      ("SIGOUT_FPGA0_STEPDIR1_ENABLE", ctypes.POINTER(ctypes.c_bool)),
      ("SIGOUT_FPGA0_STEPDIR2_VELOCITY", ctypes.POINTER(ctypes.c_float)),
      ("SIGOUT_FPGA0_STEPDIR2_VELOCITY_SCALE", ctypes.POINTER(ctypes.c_float)),
      ("SIGOUT_FPGA0_STEPDIR2_VELOCITY_OFFSET", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_FPGA0_STEPDIR2_POSITION", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_FPGA0_STEPDIR2_POSITION_ABS", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_FPGA0_STEPDIR2_POSITION_S32", ctypes.POINTER(ctypes.c_int32)),
      ("SIGIN_FPGA0_STEPDIR2_POSITION_U32_ABS", ctypes.POINTER(ctypes.c_uint32)),
      ("SIGIN_FPGA0_STEPDIR2_POSITION_SCALE", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_FPGA0_STEPDIR2_POSITION_OFFSET", ctypes.POINTER(ctypes.c_float)),
      ("SIGOUT_FPGA0_STEPDIR2_ENABLE", ctypes.POINTER(ctypes.c_bool)),
      ("SIGIN_FPGA0_BITIN0_BIT", ctypes.POINTER(ctypes.c_bool)),
      ("SIGIN_FPGA0_BITIN0_BIT_not", ctypes.POINTER(ctypes.c_bool)),
      ("SIGIN_FPGA0_BITIN1_BIT", ctypes.POINTER(ctypes.c_bool)),
      ("SIGIN_FPGA0_BITIN1_BIT_not", ctypes.POINTER(ctypes.c_bool)),
      ("SIGIN_FPGA0_BITIN2_BIT", ctypes.POINTER(ctypes.c_bool)),
      ("SIGIN_FPGA0_BITIN2_BIT_not", ctypes.POINTER(ctypes.c_bool)),
      ("SIGOUT_FPGA0_FPGA0_WLED_0_GREEN", ctypes.POINTER(ctypes.c_bool)),
      ("SIGOUT_FPGA0_FPGA0_WLED_0_BLUE", ctypes.POINTER(ctypes.c_bool)),
      ("SIGOUT_FPGA0_FPGA0_WLED_0_RED", ctypes.POINTER(ctypes.c_bool)),
      ("SIGOUT_FPGA0_BITOUT0_BIT", ctypes.POINTER(ctypes.c_bool)),
      # raw variables
      ("VARIN128_MODBUS0_RXDATA", ctypes.c_char * 16),
      ("VAROUT128_MODBUS0_TXDATA", ctypes.c_char * 16),
      ("VAROUT32_STEPDIR0_VELOCITY", ctypes.c_uint32),
      ("VARIN32_STEPDIR0_POSITION", ctypes.c_uint32),
      ("VAROUT32_STEPDIR1_VELOCITY", ctypes.c_uint32),
      ("VARIN32_STEPDIR1_POSITION", ctypes.c_uint32),
      ("VAROUT32_STEPDIR2_VELOCITY", ctypes.c_uint32),
      ("VARIN32_STEPDIR2_POSITION", ctypes.c_uint32),
      ("VARIN16_I2CBUS0_LM75_0_TEMP", ctypes.c_uint16),
      ("VARIN1_I2CBUS0_LM75_0_VALID", ctypes.c_bool),
      ("VAROUT1_STEPDIR0_ENABLE", ctypes.c_bool),
      ("VAROUT1_STEPDIR1_ENABLE", ctypes.c_bool),
      ("VAROUT1_STEPDIR2_ENABLE", ctypes.c_bool),
      ("VARIN1_BITIN0_BIT", ctypes.c_bool),
      ("VARIN1_BITIN1_BIT", ctypes.c_bool),
      ("VARIN1_BITIN2_BIT", ctypes.c_bool),
      ("VAROUT1_FPGA0_WLED_0_GREEN", ctypes.c_bool),
      ("VAROUT1_FPGA0_WLED_0_BLUE", ctypes.c_bool),
      ("VAROUT1_FPGA0_WLED_0_RED", ctypes.c_bool),
      ("VAROUT1_BITOUT0_BIT", ctypes.c_bool),
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
            "SIGIN_FPGA0_MODBUS0_TEMPERATURE": {
                "direction": "input",
                "halname": "fpga0.modbus0.temperature",
                "netname": "None",
                "type": "float",
                "subs": {
                    "SIGIN_FPGA0_MODBUS0_TEMPERATURE_ABS": {"type": "float"},
                    "SIGIN_FPGA0_MODBUS0_TEMPERATURE_S32": {"type": "int32"},
                    "SIGIN_FPGA0_MODBUS0_TEMPERATURE_U32_ABS": {"type": "uint32"},
                    "SIGIN_FPGA0_MODBUS0_TEMPERATURE_SCALE": {"type": "float"},
                    "SIGIN_FPGA0_MODBUS0_TEMPERATURE_OFFSET": {"type": "float"},
                },
            },
            "SIGIN_FPGA0_I2CBUS0_LM75_0_TEMP": {
                "direction": "input",
                "halname": "fpga0.i2cbus0.lm75_0_temp",
                "netname": "None",
                "type": "float",
                "subs": {
                    "SIGIN_FPGA0_I2CBUS0_LM75_0_TEMP_ABS": {"type": "float"},
                    "SIGIN_FPGA0_I2CBUS0_LM75_0_TEMP_S32": {"type": "int32"},
                    "SIGIN_FPGA0_I2CBUS0_LM75_0_TEMP_U32_ABS": {"type": "uint32"},
                    "SIGIN_FPGA0_I2CBUS0_LM75_0_TEMP_SCALE": {"type": "float"},
                    "SIGIN_FPGA0_I2CBUS0_LM75_0_TEMP_OFFSET": {"type": "float"},
                },
            },
            "SIGIN_FPGA0_I2CBUS0_LM75_0_VALID": {
                "direction": "input",
                "halname": "fpga0.i2cbus0.lm75_0_valid",
                "netname": "None",
                "type": "bool",
                "subs": {
                    "SIGIN_FPGA0_I2CBUS0_LM75_0_VALID_not": {"type": "bool"},
                },
            },
            "SIGOUT_FPGA0_STEPDIR0_VELOCITY": {
                "direction": "output",
                "halname": "fpga0.stepdir0.velocity",
                "netname": "None",
                "type": "float",
                "subs": {
                    "SIGOUT_FPGA0_STEPDIR0_VELOCITY_SCALE": {"type": "float"},
                    "SIGOUT_FPGA0_STEPDIR0_VELOCITY_OFFSET": {"type": "float"},
                },
            },
            "SIGIN_FPGA0_STEPDIR0_POSITION": {
                "direction": "input",
                "halname": "fpga0.stepdir0.position",
                "netname": "None",
                "type": "float",
                "subs": {
                    "SIGIN_FPGA0_STEPDIR0_POSITION_ABS": {"type": "float"},
                    "SIGIN_FPGA0_STEPDIR0_POSITION_S32": {"type": "int32"},
                    "SIGIN_FPGA0_STEPDIR0_POSITION_U32_ABS": {"type": "uint32"},
                    "SIGIN_FPGA0_STEPDIR0_POSITION_SCALE": {"type": "float"},
                    "SIGIN_FPGA0_STEPDIR0_POSITION_OFFSET": {"type": "float"},
                },
            },
            "SIGOUT_FPGA0_STEPDIR0_ENABLE": {
                "direction": "output",
                "halname": "fpga0.stepdir0.enable",
                "netname": "None",
                "type": "bool",
                "subs": {
                },
            },
            "SIGOUT_FPGA0_STEPDIR1_VELOCITY": {
                "direction": "output",
                "halname": "fpga0.stepdir1.velocity",
                "netname": "None",
                "type": "float",
                "subs": {
                    "SIGOUT_FPGA0_STEPDIR1_VELOCITY_SCALE": {"type": "float"},
                    "SIGOUT_FPGA0_STEPDIR1_VELOCITY_OFFSET": {"type": "float"},
                },
            },
            "SIGIN_FPGA0_STEPDIR1_POSITION": {
                "direction": "input",
                "halname": "fpga0.stepdir1.position",
                "netname": "None",
                "type": "float",
                "subs": {
                    "SIGIN_FPGA0_STEPDIR1_POSITION_ABS": {"type": "float"},
                    "SIGIN_FPGA0_STEPDIR1_POSITION_S32": {"type": "int32"},
                    "SIGIN_FPGA0_STEPDIR1_POSITION_U32_ABS": {"type": "uint32"},
                    "SIGIN_FPGA0_STEPDIR1_POSITION_SCALE": {"type": "float"},
                    "SIGIN_FPGA0_STEPDIR1_POSITION_OFFSET": {"type": "float"},
                },
            },
            "SIGOUT_FPGA0_STEPDIR1_ENABLE": {
                "direction": "output",
                "halname": "fpga0.stepdir1.enable",
                "netname": "None",
                "type": "bool",
                "subs": {
                },
            },
            "SIGOUT_FPGA0_STEPDIR2_VELOCITY": {
                "direction": "output",
                "halname": "fpga0.stepdir2.velocity",
                "netname": "None",
                "type": "float",
                "subs": {
                    "SIGOUT_FPGA0_STEPDIR2_VELOCITY_SCALE": {"type": "float"},
                    "SIGOUT_FPGA0_STEPDIR2_VELOCITY_OFFSET": {"type": "float"},
                },
            },
            "SIGIN_FPGA0_STEPDIR2_POSITION": {
                "direction": "input",
                "halname": "fpga0.stepdir2.position",
                "netname": "None",
                "type": "float",
                "subs": {
                    "SIGIN_FPGA0_STEPDIR2_POSITION_ABS": {"type": "float"},
                    "SIGIN_FPGA0_STEPDIR2_POSITION_S32": {"type": "int32"},
                    "SIGIN_FPGA0_STEPDIR2_POSITION_U32_ABS": {"type": "uint32"},
                    "SIGIN_FPGA0_STEPDIR2_POSITION_SCALE": {"type": "float"},
                    "SIGIN_FPGA0_STEPDIR2_POSITION_OFFSET": {"type": "float"},
                },
            },
            "SIGOUT_FPGA0_STEPDIR2_ENABLE": {
                "direction": "output",
                "halname": "fpga0.stepdir2.enable",
                "netname": "None",
                "type": "bool",
                "subs": {
                },
            },
            "SIGIN_FPGA0_BITIN0_BIT": {
                "direction": "input",
                "halname": "fpga0.bitin0.bit",
                "netname": "joint.0.home-sw-in",
                "type": "bool",
                "subs": {
                    "SIGIN_FPGA0_BITIN0_BIT_not": {"type": "bool"},
                },
            },
            "SIGIN_FPGA0_BITIN1_BIT": {
                "direction": "input",
                "halname": "fpga0.bitin1.bit",
                "netname": "joint.1.home-sw-in",
                "type": "bool",
                "subs": {
                    "SIGIN_FPGA0_BITIN1_BIT_not": {"type": "bool"},
                },
            },
            "SIGIN_FPGA0_BITIN2_BIT": {
                "direction": "input",
                "halname": "fpga0.bitin2.bit",
                "netname": "joint.2.home-sw-in",
                "type": "bool",
                "subs": {
                    "SIGIN_FPGA0_BITIN2_BIT_not": {"type": "bool"},
                },
            },
            "SIGOUT_FPGA0_FPGA0_WLED_0_GREEN": {
                "direction": "output",
                "halname": "fpga0.fpga0_wled.0_green",
                "netname": "None",
                "type": "bool",
                "subs": {
                },
            },
            "SIGOUT_FPGA0_FPGA0_WLED_0_BLUE": {
                "direction": "output",
                "halname": "fpga0.fpga0_wled.0_blue",
                "netname": "None",
                "type": "bool",
                "subs": {
                },
            },
            "SIGOUT_FPGA0_FPGA0_WLED_0_RED": {
                "direction": "output",
                "halname": "fpga0.fpga0_wled.0_red",
                "netname": "None",
                "type": "bool",
                "subs": {
                },
            },
            "SIGOUT_FPGA0_BITOUT0_BIT": {
                "direction": "output",
                "halname": "fpga0.bitout0.bit",
                "netname": "spindle.0.on",
                "type": "bool",
                "subs": {
                },
            },
        }
