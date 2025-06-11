class Modifiers:
    def info(self):
        return {
            "onerror": {
                "title": "OnError",
                "info": "holds the pin at 0 when an error has occurred",
                "options": {
                    "invert": {"title": "Invert", "type": bool, "default": False, "help_text": "Inverts the Logic"},
                },
            },
            "debounce": {
                "title": "Debounce",
                "info": "to filter noisy signals",
                "options": {
                    "delay": {"title": "Delay", "type": float, "default": 2.5, "help_text": "Delay in ms"},
                },
            },
            "pwm": {
                "title": "PWM",
                "info": "pwm generator",
                "options": {
                    "frequency": {"title": "Frequency", "type": int, "default": 1, "help_text": "PWM Frequency"},
                    "dty": {"title": "DTY", "type": int, "default": 50, "help_text": "PWM Duty Cycle"},
                },
            },
            "oneshot": {
                "title": "Oneshot",
                "info": "creates a variable-length output pulse when the input changes state",
                "options": {
                    "pulselen": {"title": "PulseLen", "type": float, "default": 1.0, "help_text": "pulse len in ms"},
                    "retrigger": {"title": "Retrigger", "type": bool, "default": False, "help_text": "retrigger the time pulse"},
                    "hold": {"title": "Hold", "type": bool, "default": False, "help_text": "hold the puls while input is set"},
                    "edge": {"title": "Edge", "type": "select", "options": ["RISING", "FALLING", "BOTH"], "default": "RISING", "help_text": "edge to trigger"},
                },
            },
            "toggle": {
                "title": "Toggle",
                "info": "toggle pin on rising edge",
            },
            "invert": {
                "title": "Invert",
                "info": "inverting the pin",
            },
        }

    def pin_modifier_debounce(self, instances, modifier_num, pin_name, pin_varname, modifier, system_setup):
        delay = modifier.get("delay", 2.5)
        delay_divider = int(system_setup["speed"] * delay / 1000)
        instances[f"debouncer{modifier_num}_{self.instances_name}_{pin_name}"] = {
            "module": "debouncer",
            "parameter": {"DELAY": delay_divider},
            "arguments": {
                "clk": "sysclk",
                "din": pin_varname,
                "dout": f"{pin_varname}_DEBOUNCED",
            },
            "predefines": [f"wire {pin_varname}_DEBOUNCED;"],
        }
        pin_varname = f"{pin_varname}_DEBOUNCED"
        return pin_varname

    def pin_modifier_toggle(self, instances, modifier_num, pin_name, pin_varname, modifier, system_setup):
        instances[f"toggle{modifier_num}_{self.instances_name}_{pin_name}"] = {
            "module": "toggle",
            "arguments": {
                "clk": "sysclk",
                "din": pin_varname,
                "dout": f"{pin_varname}_TOGGLED",
            },
            "predefines": [f"wire {pin_varname}_TOGGLED;"],
        }
        pin_varname = f"{pin_varname}_TOGGLED"
        return pin_varname

    def pin_modifier_invert(self, instances, modifier_num, pin_name, pin_varname, modifier, system_setup):
        instances[f"invert{modifier_num}_{self.instances_name}_{pin_name}"] = {
            "predefines": [
                f"wire {pin_varname}_INVERTED;",
                f"assign {pin_varname}_INVERTED = ~{pin_varname};",
            ],
        }
        pin_varname = f"{pin_varname}_INVERTED"
        return pin_varname

    def pin_modifier_onerror(self, instances, modifier_num, pin_name, pin_varname, modifier, system_setup):
        invert = modifier.get("invert", False)
        invert_char = "~"
        if invert:
            invert_char = ""
        instances[f"onerror{modifier_num}_{self.instances_name}_{pin_name}"] = {
            "predefines": [
                f"wire {pin_varname}_ONERROR;",
                f"assign {pin_varname}_ONERROR = {pin_varname} & {invert_char}ERROR;",
            ],
        }
        pin_varname = f"{pin_varname}_ONERROR"
        return pin_varname

    def pin_modifier_oneshot(self, instances, modifier_num, pin_name, pin_varname, modifier, system_setup):
        edges = ["RISING", "FALLING", "BOTH"]
        pulselen = modifier.get("pulselen", 1.0)
        retrigger = int(modifier.get("retrigger", False))
        hold = int(modifier.get("hold", False))
        edge = edges.index(modifier.get("edge", "RISING"))
        pulselen_divider = int(system_setup["speed"] * pulselen / 1000)
        instances[f"oneshot{modifier_num}_{self.instances_name}_{pin_name}"] = {
            "module": "oneshot",
            "parameter": {"PULSE_LEN": pulselen_divider, "RETRIGGER": retrigger, "HOLD": hold, "EDGE": edge},
            "arguments": {
                "clk": "sysclk",
                "din": pin_varname,
                "dout": f"{pin_varname}_ONESHOT",
            },
        }
        pin_varname = f"{pin_varname}_ONESHOT"
        return pin_varname

    def pin_modifier_pwm(self, instances, modifier_num, pin_name, pin_varname, modifier, system_setup):
        frequency = modifier.get("frequency", 1)
        dty = modifier.get("dty", 50)
        frequency_divider = system_setup["speed"] // frequency
        dty_divider = frequency_divider * dty // 100
        instances[f"pwm{modifier_num}_{self.instances_name}_{pin_name}"] = {
            "module": "pwmmod",
            "parameter": {"DIVIDER_FREQ": frequency_divider, "DIVIDER_DTY": dty_divider},
            "arguments": {
                "clk": "sysclk",
                "din": pin_varname,
                "dout": f"{pin_varname}_PWM",
            },
        }
        pin_varname = f"{pin_varname}_PWM"
        return pin_varname

    def pin_modifier_list(self, direction=None):
        modifiers = []
        for part in dir(self):
            if part.startswith("pin_modifier_") and part != "pin_modifier_list":
                modifiers.append(part.split("_")[2])
        return modifiers
