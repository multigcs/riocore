import os


class Pins:
    def __init__(self, config):
        self.config = config

    def generate(self, path):
        data = []

        family = self.config["family"]
        ftype = self.config["type"]

        CLK_IN = int(self.config["jdata"]["clock"]["osc"])
        CLK_OUT = int(self.config["jdata"]["clock"]["speed"])

        interface = []
        interface.append("import os")
        interface.append("import sys")
        interface.append("pt_home = os.environ['EFXPT_HOME']")
        interface.append("sys.path.append(pt_home + '/bin')")
        interface.append("from api_service.design import DesignAPI")
        interface.append("from api_service.device import DeviceAPI")
        interface.append("import api_service.excp.design_excp as APIExcp")
        interface.append("")
        interface.append("is_verbose = True")
        interface.append("design = DesignAPI(is_verbose)")
        interface.append("device = DeviceAPI(is_verbose)")
        interface.append(f"device_name = '{ftype}'")
        interface.append("project_name = 'rio'")
        interface.append("design.create(project_name, device_name, './')")
        interface.append("design.create_block('PLL', block_type='PLL')")
        interface.append(f"pll_config = {{'REFCLK_FREQ': '{CLK_IN / 1000000}', 'CLKOUT0_PIN': 'sysclk_in'}}")
        interface.append("design.set_property('PLL', pll_config, block_type='PLL')")
        interface.append("target_freq = {")
        interface.append(f"    'CLKOUT0_FREQ': '{CLK_OUT / 1000000}',")
        interface.append("    'CLKOUT0_PHASE': '0',")
        interface.append("}")
        interface.append("calc_result = design.auto_calc_pll_clock('PLL', target_freq)")
        interface.append("clock_prop = ['M', 'N', 'O', 'CLKOUT0_DIV', 'CLKOUT2_DIV', 'VCO_FREQ', 'PLL_FREQ']")
        interface.append("prop_map = design.get_property('PLL', clock_prop, block_type='PLL')")
        interface.append("")
        interface.append("#print(device.get_gpio_resource_name())")
        for pname, pins in self.config["pinlists"].items():
            for pin, pin_config in pins.items():
                if pin_config["varname"] == "sysclk_in":
                    interface.append('design.create_pll_input_clock_gpio("PLLIN")')
                    interface.append('design.set_property("PLLIN", "PULL_OPTION", "WEAK_PULLUP")')
                    interface.append(f'design.assign_pkg_pin("PLLIN", "{pin_config["pin"]}")')
                else:
                    interface.append(f'design.create_{pin_config["direction"]}_gpio("{pin_config["varname"]}")')
                    if pin_config["direction"] == "output":
                        drive = int(pin_config.get("drive", "4"))
                        # slew = pin_config.get("slew", "SLOW").upper()
                        if family == "Trion":
                            if drive > 5:
                                drive = 4
                        else:
                            set_drive = 2
                            for dv in (2, 4, 6, 8, 10, 12, 16):
                                if dv > drive:
                                    break
                                set_drive = dv
                            drive = set_drive
                        interface.append(f'design.set_property("{pin_config["varname"]}", "DRIVE_STRENGTH", "{drive}")')
                        # if slew == FAST:
                        #    interface.append(f'design.set_property("{pin_config["varname"]}", "SLEW_RATE", "1")')
                    else:
                        if pin_config.get("pullup", False) or pin_config.get("pull") == "up":
                            interface.append(f'design.set_property("{pin_config["varname"]}", "PULL_OPTION", "WEAK_PULLUP")')
                        elif pin_config.get("pulldown", False) or pin_config.get("pull") == "down":
                            interface.append(f'design.set_property("{pin_config["varname"]}", "PULL_OPTION", "WEAK_PULLDOWN")')

                    interface.append(f'design.assign_pkg_pin("{pin_config["varname"]}", "{pin_config["pin"]}")')
                data.append("        </efxpt:gpio>")

        interface.append("")
        interface.append("design.save()")
        interface.append("")

        open(os.path.join(path, "pins.py"), "w").write("\n".join(interface))
        open(os.path.join(path, "rio.sdc"), "w").write("")
