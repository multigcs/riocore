import math


class i2c_device:
    sensor_options = ["volt", "ntc", "pressure"]
    options = {
        "info": "16bit / 4channel adc",
        "description": "",
        "addresses": ["0x48", "0x49"],
        "config": {
            "channels": {
                "type": int,
                "min": 1,
                "max": 4,
                "description": "number of channels",
                "default": 4,
            },
            "sensor0": {
                "type": "combo",
                "options": sensor_options,
                "max": 4,
                "description": "sensor type on channel 1",
                "default": sensor_options[0],
            },
            "sensor1": {
                "type": "combo",
                "options": sensor_options,
                "max": 4,
                "description": "sensor type on channel 1",
                "default": sensor_options[0],
            },
            "sensor2": {
                "type": "combo",
                "options": sensor_options,
                "max": 4,
                "description": "sensor type on channel 1",
                "default": sensor_options[0],
            },
            "sensor3": {
                "type": "combo",
                "options": sensor_options,
                "max": 4,
                "description": "sensor type on channel 1",
                "default": sensor_options[0],
            },
        },
    }

    def __init__(self, setup, system_setup={}):
        self.system_setup = system_setup
        self.name = setup["name"]
        self.addr = setup["address"]
        self.setup = setup
        self.channels = setup.get("channels", self.options["config"]["channels"]["default"])

        self.INTERFACE = {}
        self.SIGNALS = {}
        for channel in range(self.channels):
            sensor_setups = {
                "volt": ("V", "0.3f"),
                "ntc": ("°C", "0.1f"),
                "pressure": ("bar", "0.1f"),
            }
            sensor = self.setup.get(f"sensor{channel}", self.options["config"][f"sensor{channel}"]["default"])
            self.INTERFACE[f"{self.name}_adc{channel}"] = {
                "size": 16,
                "direction": "input",
            }
            self.SIGNALS[f"{self.name}_adc{channel}"] = {
                "direction": "input",
                "format": sensor_setups.get(sensor, ["", "0.3f"])[1],
                "unit": sensor_setups.get(sensor, ["", ""])[0],
            }
        self.INTERFACE[f"{self.name}_valid"] = {
            "size": 1,
            "direction": "input",
        }
        self.SIGNALS[f"{self.name}_valid"] = {
            "direction": "input",
            "bool": True,
        }

        self.PARAMS = {}
        self.INITS = {}
        setupRegister = [
            "8'd1",  # Register-Address
            "1'b1",  # Start Conversion
            "3'b100",  # Channel 0 Single ended
            "3'b001",  # FSR +- 4.096v
            "1'b1",  # Single shot mode
            "3'b100",  # 128 SPS
            "1'b0",  # Traditional Comparator
            "1'b0",  # Active low alert
            "1'b0",  # Non latching
            "2'b11",  # Disable comparator
        ]

        self.INITS = []
        self.STEPS = []

        for channel in range(self.channels):
            setupRegister[2] = f"3'd{4 + channel}"
            self.STEPS += [
                {
                    "comment": "start conversion",
                    "mode": "write",
                    "value": f"{{{', '.join(setupRegister)}}}",
                    "bytes": 3,
                },
                {
                    "comment": "set status register",
                    "mode": "write",
                    "value": "8'd1",
                    "bytes": 1,
                },
                {
                    "comment": "check status",
                    "mode": "read",
                    "until": "data_in[7] == 1",
                    "timeout": 130,
                    "bytes": 1,
                },
                {
                    "comment": "set adc register",
                    "mode": "write",
                    "value": "8'd0",
                    "bytes": 1,
                },
                {
                    "comment": "read 16bit adc value",
                    "mode": "read",
                    "var": f"{self.name}_adc{channel}",
                    "bytes": 2,
                },
            ]

    def convert(self, signal_name, signal_setup, value):
        if signal_name.endswith("_valid"):
            return value

        channel = signal_name[-1]
        sensor = self.setup.get(f"sensor{channel}", self.options["config"][f"sensor{channel}"]["default"])
        value = value >> 3
        value /= 1000.0

        if sensor == "ntc":
            Rt = 10.0 * value / (3.3 - value)
            if Rt == 0.0:
                value = -999.0
            else:
                tempK = 1.0 / (math.log(Rt / 10.0) / 3950.0 + 1.0 / (273.15 + 25.0))
                tempC = tempK - 273.15
                value = tempC
        elif sensor == "pressure":
            value *= 2.57
            value -= 0.56

        return value

    def convert_c(self, signal_name, signal_setup):
        if signal_name.endswith("_valid"):
            return ""

        channel = signal_name[-1]
        sensor = self.setup.get(f"sensor{channel}", self.options["config"][f"sensor{channel}"]["default"])

        if sensor == "ntc":
            return """
                value = (int16_t)value>>3;
                value /= 1000.0;
                float Rt = 10.0 * value / (3.3 - value);
                float tempK = 1.0 / (log(Rt / 10.0) / 3950.0 + 1.0 / (273.15 + 25.0));
                float tempC = tempK - 273.15;
                value = tempC;
            """
        elif sensor == "pressure":
            return """
            value = (int16_t)value>>3;
            value /= 1000.0;
            value *= 2.57;
            value -= 0.56;
            """
        else:
            return """
            value = (int16_t)value>>3;
            value /= 1000.0;
            """
