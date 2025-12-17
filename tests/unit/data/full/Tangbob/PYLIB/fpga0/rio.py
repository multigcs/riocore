
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
            "modbus0": {
                "type": "modbus",
                "title": "modbus0",
                "is_joint": False,
                "variables": [
                    "SIGIN_FPGA0_MODBUS0_TEMPERATURE",
                ],
            },
            "blink0": {
                "type": "blink",
                "title": "blink0",
                "is_joint": False,
                "variables": [
                ],
            },
            "i2cbus0": {
                "type": "i2cbus",
                "title": "i2cbus0",
                "is_joint": False,
                "variables": [
                    "SIGIN_FPGA0_I2CBUS0_LM75_0_TEMP",
                    "SIGIN_FPGA0_I2CBUS0_LM75_0_VALID",
                ],
            },
            "stepdir0": {
                "type": "stepdir",
                "title": "stepdir0",
                "is_joint": True,
                "variables": [
                    "SIGOUT_FPGA0_STEPDIR0_VELOCITY",
                    "SIGIN_FPGA0_STEPDIR0_POSITION",
                    "SIGOUT_FPGA0_STEPDIR0_ENABLE",
                ],
            },
            "stepdir1": {
                "type": "stepdir",
                "title": "stepdir1",
                "is_joint": True,
                "variables": [
                    "SIGOUT_FPGA0_STEPDIR1_VELOCITY",
                    "SIGIN_FPGA0_STEPDIR1_POSITION",
                    "SIGOUT_FPGA0_STEPDIR1_ENABLE",
                ],
            },
            "stepdir2": {
                "type": "stepdir",
                "title": "stepdir2",
                "is_joint": True,
                "variables": [
                    "SIGOUT_FPGA0_STEPDIR2_VELOCITY",
                    "SIGIN_FPGA0_STEPDIR2_POSITION",
                    "SIGOUT_FPGA0_STEPDIR2_ENABLE",
                ],
            },
            "bitin0": {
                "type": "bitin",
                "title": "home-x",
                "is_joint": False,
                "variables": [
                    "SIGIN_FPGA0_BITIN0_BIT",
                ],
            },
            "bitin1": {
                "type": "bitin",
                "title": "home-y",
                "is_joint": False,
                "variables": [
                    "SIGIN_FPGA0_BITIN1_BIT",
                ],
            },
            "bitin2": {
                "type": "bitin",
                "title": "home-z",
                "is_joint": False,
                "variables": [
                    "SIGIN_FPGA0_BITIN2_BIT",
                ],
            },
            "fpga0": {
                "type": "fpga",
                "title": "fpga0",
                "is_joint": False,
                "variables": [
                ],
            },
            "fpga0_w5500": {
                "type": "w5500",
                "title": "fpga0_w5500",
                "is_joint": False,
                "variables": [
                ],
            },
            "fpga0_wled": {
                "type": "wled",
                "title": "fpga0_wled",
                "is_joint": False,
                "variables": [
                    "SIGOUT_FPGA0_FPGA0_WLED_0_GREEN",
                    "SIGOUT_FPGA0_FPGA0_WLED_0_BLUE",
                    "SIGOUT_FPGA0_FPGA0_WLED_0_RED",
                ],
            },
            "bitout0": {
                "type": "bitout",
                "title": "bitout0",
                "is_joint": False,
                "variables": [
                    "SIGOUT_FPGA0_BITOUT0_BIT",
                ],
            },
        }

    def data_info(self):
        return {
            "SIGIN_FPGA0_MODBUS0_TEMPERATURE": {
                "plugin": "modbus0",
                "direction": "input",
                "signal_name": "temperature",
                "userconfig": {},
                "halname": "fpga0.modbus0.temperature",
                "netname": "",
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
                "plugin": "i2cbus0",
                "direction": "input",
                "signal_name": "lm75_0_temp",
                "userconfig": {},
                "halname": "fpga0.i2cbus0.lm75_0_temp",
                "netname": "",
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
                "plugin": "i2cbus0",
                "direction": "input",
                "signal_name": "lm75_0_valid",
                "userconfig": {},
                "halname": "fpga0.i2cbus0.lm75_0_valid",
                "netname": "",
                "type": "bool",
                "subs": {
                    "SIGIN_FPGA0_I2CBUS0_LM75_0_VALID_not": {"type": "bool"},
                },
            },
            "SIGOUT_FPGA0_STEPDIR0_VELOCITY": {
                "plugin": "stepdir0",
                "direction": "output",
                "signal_name": "velocity",
                "userconfig": {},
                "halname": "fpga0.stepdir0.velocity",
                "netname": "",
                "type": "float",
                "subs": {
                    "SIGOUT_FPGA0_STEPDIR0_VELOCITY_SCALE": {"type": "float"},
                    "SIGOUT_FPGA0_STEPDIR0_VELOCITY_OFFSET": {"type": "float"},
                },
            },
            "SIGIN_FPGA0_STEPDIR0_POSITION": {
                "plugin": "stepdir0",
                "direction": "input",
                "signal_name": "position",
                "userconfig": {},
                "halname": "fpga0.stepdir0.position",
                "netname": "",
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
                "plugin": "stepdir0",
                "direction": "output",
                "signal_name": "enable",
                "userconfig": {},
                "halname": "fpga0.stepdir0.enable",
                "netname": "",
                "type": "bool",
                "subs": {
                },
            },
            "SIGOUT_FPGA0_STEPDIR1_VELOCITY": {
                "plugin": "stepdir1",
                "direction": "output",
                "signal_name": "velocity",
                "userconfig": {},
                "halname": "fpga0.stepdir1.velocity",
                "netname": "",
                "type": "float",
                "subs": {
                    "SIGOUT_FPGA0_STEPDIR1_VELOCITY_SCALE": {"type": "float"},
                    "SIGOUT_FPGA0_STEPDIR1_VELOCITY_OFFSET": {"type": "float"},
                },
            },
            "SIGIN_FPGA0_STEPDIR1_POSITION": {
                "plugin": "stepdir1",
                "direction": "input",
                "signal_name": "position",
                "userconfig": {},
                "halname": "fpga0.stepdir1.position",
                "netname": "",
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
                "plugin": "stepdir1",
                "direction": "output",
                "signal_name": "enable",
                "userconfig": {},
                "halname": "fpga0.stepdir1.enable",
                "netname": "",
                "type": "bool",
                "subs": {
                },
            },
            "SIGOUT_FPGA0_STEPDIR2_VELOCITY": {
                "plugin": "stepdir2",
                "direction": "output",
                "signal_name": "velocity",
                "userconfig": {},
                "halname": "fpga0.stepdir2.velocity",
                "netname": "",
                "type": "float",
                "subs": {
                    "SIGOUT_FPGA0_STEPDIR2_VELOCITY_SCALE": {"type": "float"},
                    "SIGOUT_FPGA0_STEPDIR2_VELOCITY_OFFSET": {"type": "float"},
                },
            },
            "SIGIN_FPGA0_STEPDIR2_POSITION": {
                "plugin": "stepdir2",
                "direction": "input",
                "signal_name": "position",
                "userconfig": {},
                "halname": "fpga0.stepdir2.position",
                "netname": "",
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
                "plugin": "stepdir2",
                "direction": "output",
                "signal_name": "enable",
                "userconfig": {},
                "halname": "fpga0.stepdir2.enable",
                "netname": "",
                "type": "bool",
                "subs": {
                },
            },
            "SIGIN_FPGA0_BITIN0_BIT": {
                "plugin": "bitin0",
                "direction": "input",
                "signal_name": "bit",
                "userconfig": {'net': 'joint.0.home-sw-in'},
                "halname": "fpga0.bitin0.bit",
                "netname": "joint.0.home-sw-in",
                "type": "bool",
                "subs": {
                    "SIGIN_FPGA0_BITIN0_BIT_not": {"type": "bool"},
                },
            },
            "SIGIN_FPGA0_BITIN1_BIT": {
                "plugin": "bitin1",
                "direction": "input",
                "signal_name": "bit",
                "userconfig": {'net': 'joint.1.home-sw-in'},
                "halname": "fpga0.bitin1.bit",
                "netname": "joint.1.home-sw-in",
                "type": "bool",
                "subs": {
                    "SIGIN_FPGA0_BITIN1_BIT_not": {"type": "bool"},
                },
            },
            "SIGIN_FPGA0_BITIN2_BIT": {
                "plugin": "bitin2",
                "direction": "input",
                "signal_name": "bit",
                "userconfig": {'net': 'joint.2.home-sw-in'},
                "halname": "fpga0.bitin2.bit",
                "netname": "joint.2.home-sw-in",
                "type": "bool",
                "subs": {
                    "SIGIN_FPGA0_BITIN2_BIT_not": {"type": "bool"},
                },
            },
            "SIGOUT_FPGA0_FPGA0_WLED_0_GREEN": {
                "plugin": "fpga0_wled",
                "direction": "output",
                "signal_name": "0_green",
                "userconfig": {},
                "halname": "fpga0.fpga0_wled.0_green",
                "netname": "",
                "type": "bool",
                "subs": {
                },
            },
            "SIGOUT_FPGA0_FPGA0_WLED_0_BLUE": {
                "plugin": "fpga0_wled",
                "direction": "output",
                "signal_name": "0_blue",
                "userconfig": {},
                "halname": "fpga0.fpga0_wled.0_blue",
                "netname": "",
                "type": "bool",
                "subs": {
                },
            },
            "SIGOUT_FPGA0_FPGA0_WLED_0_RED": {
                "plugin": "fpga0_wled",
                "direction": "output",
                "signal_name": "0_red",
                "userconfig": {},
                "halname": "fpga0.fpga0_wled.0_red",
                "netname": "",
                "type": "bool",
                "subs": {
                },
            },
            "SIGOUT_FPGA0_BITOUT0_BIT": {
                "plugin": "bitout0",
                "direction": "output",
                "signal_name": "bit",
                "userconfig": {'net': 'spindle.0.on'},
                "halname": "fpga0.bitout0.bit",
                "netname": "spindle.0.on",
                "type": "bool",
                "subs": {
                },
            },
        }
