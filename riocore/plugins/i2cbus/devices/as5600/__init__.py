class i2c_device:
    options = {
        "info": "magnetic rotary position sensor",
        "description": "",
        "addresses": ["0x36"],
    }

    def __init__(self, setup, system_setup={}):
        self.last = 0
        self.revs = 0
        self.system_setup = system_setup
        self.name = setup["name"]
        self.addr = setup["address"]
        self.INTERFACE = {
            f"{self.name}_angle": {
                "size": 16,
                "direction": "input",
            },
            f"{self.name}_valid": {
                "size": 1,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            f"{self.name}_position": {
                "direction": "input",
                "format": "0.1f",
            },
            f"{self.name}_angle": {
                "direction": "input",
                "format": "0.1f",
            },
            f"{self.name}_valid": {
                "direction": "input",
                "bool": True,
            },
        }
        self.PARAMS = {}
        self.INITS = []
        self.STEPS = [
            {
                "mode": "write",
                "value": "8'd14",
                "bytes": 1,
            },
            {
                "mode": "read",
                "var": f"{self.name}_angle",
                "var_set": "{3'd0, data_in[11:0]}",
                "bytes": 2,
            },
        ]

    def convert(self, signal_name, signal_setup, value):
        if signal_name.endswith("_angle"):
            new = value
            diff = new - self.last
            if diff < -2048:
                self.revs += 1
            elif diff > 2048:
                self.revs -= 1
            self.SIGNALS[f"{self.name}_position"]["value"] = (self.revs * 4096) + new
            self.last = new

            return value * 360 / 4096
        return value

    def convert_c(self, signal_name, signal_setup):
        if signal_name.endswith("_angle"):
            varname = self.SIGNALS[f"{self.name}_position"]["varname"]
            return f"""

    static float revs = 0;
    float diff = 0;

    diff = raw_value - last_raw_value;

    if (diff < -2048) {{
        revs++;
    }} else if (diff > 2048) {{
        revs--;
    }}

    float position_value = (revs * 4096) + raw_value;
    position_value = position_value + *data->{varname}_OFFSET;
    position_value = position_value / *data->{varname}_SCALE;
    *data->{varname} = position_value;

    value = value * 360 / 4096;
            """
        return ""
