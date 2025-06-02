import time


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
            f"{self.name}_rps": {
                "direction": "input",
                "format": "0.2f",
            },
            f"{self.name}_rpm": {
                "direction": "input",
                "format": "0.2f",
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
        self.INITS = [
            {
                "mode": "write",
                "value": "8'd14",
                "bytes": 1,
            },
        ]
        """
        self.INITS = [
            {
                "mode": "writereg",
                "values": [
                    (0x01, 0),
                    (0x02, 0),

                    (0x08, 0b11100000), # PWM out 920Hz
                    (0xff, 0x40), # save permanent

                    #(0x03, 0b00000000),
                    #(0x04, 0b00001111),
                    #(0xff, 0x80),
                ],
            },
        ]
        """
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
        self.timer_last = time.time()

    def convert(self, signal_name, signal_setup, value):
        if signal_name.endswith("_angle"):
            new = value
            diff = new - self.last
            if diff < -2048:
                self.revs += 1
                diff += 4096
            elif diff > 2048:
                self.revs -= 1
                diff -= 4096
            self.SIGNALS[f"{self.name}_position"]["value"] = (self.revs * 4096) + new
            self.last = new

            # calc rps/rpm
            timer_new = time.time()
            timer_diff = timer_new - self.timer_last
            rps = diff / timer_diff / 4096
            self.timer_last = timer_new
            self.SIGNALS[f"{self.name}_rps"]["value"] = rps
            self.SIGNALS[f"{self.name}_rpm"]["value"] = rps * 60

            # calc angle
            return value * 360 / 4096
        return value

    def convert_c(self, signal_name, signal_setup):
        if signal_name.endswith("_angle"):
            varname = self.SIGNALS[f"{self.name}_position"]["varname"]
            varname_rps = self.SIGNALS[f"{self.name}_rps"]["varname"]
            varname_rpm = self.SIGNALS[f"{self.name}_rpm"]["varname"]
            return f"""

    static float revs = 0;
    float diff = 0;

    diff = raw_value - last_raw_value;

    if (diff < -2048) {{
        revs++;
        diff += 4096;
    }} else if (diff > 2048) {{
        revs--;
        diff -= 4096;
    }}

    // calc rps/rpm
    static uint8_t pcnt = 0;
    static float last_rpssum = 0;
    static float diff_sum = 0;
    static float duration_sum = 0.0;
    diff_sum += diff;
    duration_sum += *data->duration;
    pcnt++;
    if (pcnt == 100) {{
        last_rpssum = diff_sum / duration_sum / 4096;
        pcnt = 0;
        duration_sum = 0;
        diff_sum = 0;
    }}
    *data->{varname_rps} = last_rpssum;
    *data->{varname_rpm} = last_rpssum * 60;


    // calc position
    float position_value = (revs * 4096) + raw_value;
    position_value = position_value + *data->{varname}_OFFSET;
    position_value = position_value / *data->{varname}_SCALE;
    *data->{varname} = position_value;

    // calc angle
    value = value * 360 / 4096;
            """
        return ""
