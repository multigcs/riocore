from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "tmc5160"
        self.TYPE = "joint"
        self.INFO = "TMC5160 SPI joint"
        self.DESCRIPTION = """Joint controlled through the TMC5160 internal ramp generator.
Velocity is written through SPI and XACTUAL is used as position feedback.

WARNING: if you use a board like the TMC5160T Pro V1.0,
you need to modify it to disable SD-Mode
This drivers have enabled SPI, but only for configuration.
"""
        self.KEYWORDS = "joint stepper tmc5160 spi trinamic"
        self.ORIGIN = "https://www.analog.com/en/products/tmc5160.html"
        self.VERILOGS = ["tmc5160.v"]
        self.IMAGES = ["image.png"]
        self.EXPERIMENTAL = True

        self.PINDEFAULTS = {
            "sck": {
                "direction": "output",
                "description": "TMC5160 SPI clock, mode 3",
                "pos": (6, 28),
            },
            "mosi": {
                "direction": "output",
                "description": "TMC5160 SPI data input",
                "pos": (6, 17),
            },
            "miso": {
                "direction": "input",
                "description": "TMC5160 SPI data output",
                "pos": (6, 50),
            },
            "cs_n": {
                "direction": "output",
                "description": "TMC5160 active-low chip select",
                "pos": (6, 39),
            },
            "enable_n": {
                "direction": "output",
                "description": "TMC5160 active-low driver enable",
                "pos": (6, 6),
            },
        }

        self.INTERFACE = {
            "velocity": {
                "size": 32,
                "direction": "output",
            },
            "enable": {
                "size": 1,
                "direction": "output",
                "on_error": False,
            },
            "position": {
                "size": 32,
                "direction": "input",
            },
            "drv_status": {
                "size": 32,
                "direction": "input",
            },
            "tmc_status": {
                "size": 8,
                "direction": "input",
            },
            "fault": {
                "size": 1,
                "direction": "input",
            },
        }

        self.SIGNALS = {
            "velocity": {
                "direction": "output",
                "min": -100000,
                "max": 100000,
                "unit": "Hz",
                "absolute": False,
                "description": "speed in steps per second",
            },
            "enable": {
                "direction": "output",
                "bool": True,
                "description": "Joint amplifier enable",
            },
            "position": {
                "direction": "input",
                "unit": "unit",
                "description": "XACTUAL position / Feedback",
            },
            "drv_status": {
                "direction": "input",
                "description": "Raw TMC5160 DRV_STATUS register",
                "format": "032b",
            },
            "tmc_status": {
                "direction": "input",
                "description": "TMC5160 SPI status byte",
                "format": "032b",
            },
            "fault": {
                "direction": "input",
                "bool": True,
                "description": "TMC5160 driver error or short/overtemperature",
            },
        }

        self.OPTIONS = {
            "microsteps": {
                "default": "256",
                "type": "select",
                "options": ["256", "128", "64", "32", "16", "8", "4", "2", "FULL"],
                "description": "MRES",
            },
            "global_scaler": {
                "default": 0,
                "min": 0,
                "max": 256,
                "type": int,
                "description": "TMC5160 GLOBAL_SCALER",
            },
            "irun": {
                "default": 15,
                "type": int,
                "min": 0,
                "max": 31,
                "description": "",
            },
            "ihold": {
                "default": 5,
                "type": int,
                "min": 0,
                "max": 31,
                "description": "",
            },
            "ihold_delay": {
                "default": 5,
                "type": int,
                "min": 0,
                "max": 15,
                "description": "",
            },
        }

    def _option_int(self, name, default):
        value = self.plugin_setup.get(name, default)
        if isinstance(value, str):
            return int(value, 0)
        return int(value)

    def _u32_parameter(self, name, default):
        value = self._option_int(name, default) & 0xFFFFFFFF
        return f"32'h{value:08X}"

    def gateware_instances(self, gateware=None):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        parameters = instance.setdefault("parameter", {})

        system_clock = int(self.system_setup["speed"])
        spi_hz = self._option_int("spi_hz", 1_000_000)
        startup_ms = self._option_int("startup_ms", 50)

        # SPI_DIVIDER is the number of FPGA clocks per half SPI period.
        spi_divider = max(
            1,
            (system_clock + 2 * spi_hz - 1) // (2 * spi_hz),
        )

        startup_cycles = max(
            0,
            int(system_clock * startup_ms / 1000),
        )

        parameters["SPI_DIVIDER"] = spi_divider
        parameters["STARTUP_CYCLES"] = startup_cycles

        register_parameters = {
            "GCONF": ("gconf", 0b00000000000000000000000000001100),
            "TPOWERDOWN": ("tpowerdown", 10),
            "TPWMTHRS": ("tpwmthrs", 0x000001F4),
            "TCOOLTHRS": ("tcoolthrs", 0),
            "THIGH": ("thigh", 0),
            "COOLCONF": ("coolconf", 0),
            "PWMCONF": ("pwmconf", 0xC40C001E),
            "VSTART": ("vstart", 4),
            "A1": ("a1", 5000),
            "V1": ("v1", 1000),
            "AMAX": ("amax", 5000),
            "DMAX": ("dmax", 5000),
            "D1": ("d1", 1000),
            "VSTOP": ("vstop", 100),
            "TZEROWAIT": ("tzerowait", 0),
            "SW_MODE": ("sw_mode", 0),
            "XACTUAL_INIT": ("xactual_init", 0),
        }

        for parameter, (option, default) in register_parameters.items():
            parameters[parameter] = self._u32_parameter(option, default)

        microsteps = self.plugin_setup.get("microsteps", "256")
        microsteps_mapping = {
            "256": "0000",
            "128": "0001",
            "64": "0010",
            "32": "0011",
            "16": "0100",
            "8": "0101",
            "4": "0010",
            "2": "0111",
            "FULL": "1000",
        }
        parameters["CHOPCONF"] = f"32'b0000_{microsteps_mapping[microsteps]}_000000010000000011000011"

        ihold_delay = self.plugin_setup.get("ihold_delay", 5)
        irun = self.plugin_setup.get("irun", 20)
        ihold = self.plugin_setup.get("ihold", 10)
        parameters["IHOLD_IRUN"] = f"32'b{ihold_delay:04b}_{irun:05b}_{ihold:05b}"
        global_scaler = self.plugin_setup.get("global_scaler", 200)
        if global_scaler == 256:
            global_scaler = 0
        parameters["GLOBAL_SCALER"] = f"32'b00000000_00000000_00000000_{global_scaler:08b}"

        return instances

    def convert_c(self, signal_name, signal_setup):
        return ""
        """
        scale = float(self.plugin_setup.get("scale", 1.0))
        tmc_clock = float(
            self.plugin_setup.get("tmc_clock_hz", 12_000_000)
        )

        if signal_name == "velocity":
            factor = scale * (2**24) / tmc_clock
            return f"((int32_t)(({value}) * {factor:.12g}))"

        if signal_name == "position":
            return f"((float)({value}) / {scale:.12g})"

        return value
        """
