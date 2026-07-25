import os

from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        uid = self.plugin_setup["uid"]
        self.NAME = "gowin_empu"
        self.INFO = "TangNano4K ARM core"
        self.DESCRIPTION = "Cortex M3 ARM core inside TangNano4K"
        self.KEYWORDS = "arm hardcore cpu"
        self.ORIGIN = "https://github.com/grughuhler/tang_4k_getting_started/tree/main"
        self.NEEDS = ["fpga", "gowin_empu"]
        self.VERILOGS = ["gowin_empu.v"]
        self.SRCFILES = [
            f"src/Makefile:src_{uid}/Makefile",
            f"src/link_cmd.ld:src_{uid}/link_cmd.ld",
            f"src/startup.S:src_{uid}/startup.S",
            f"src/cont_startup.c:src_{uid}/cont_startup.c",
            f"src/gpio.c:src_{uid}/gpio.c",
            f"src/gpio.h:src_{uid}/gpio.h",
            f"src/main.c:src_{uid}/main.c",
            f"src/uart.c:src_{uid}/uart.c",
            f"src/uart.h:src_{uid}/uart.h",
        ]
        # self.RESET = True
        self.OPTIONS = {}
        self.OPTIONS["ramsize"] = {
            "type": "select",
            "options": ["512", "768", "1024", "2048", "4096", "8192"],
            "default": "1024",
            "description": "size of ram in bytes",
        }
        self.gpios = self.plugin_setup.get("gpios", {})
        # set pins
        self.PINDEFAULTS = {}
        for gpio in self.gpios:
            self.PINDEFAULTS[gpio.upper()] = {
                "direction": "inout",
                "optional": True,
            }
        # set interface/signals
        self.INTERFACE = {}
        self.SIGNALS = {}

    def gateware_instances(self, gateware=None):
        uid = self.plugin_setup["uid"]
        if gateware:
            gateware.jdata["firmware_file"] = f"src_{uid}/prog.bin"
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance["module"] = "Gowin_EMPU_Top"
        instance_arguments = instance["arguments"]
        gpios = []
        gpio_n = 0
        for gpio in self.gpios:
            if gpio.upper() in instance_arguments:
                var = instance_arguments[gpio.upper()]
                gpios.append(var)
                del instance_arguments[gpio.upper()]
            gpio_n += 1
        del instance_arguments["clk"]
        instance_arguments["sys_clk"] = "sysclk"
        if self.RESET:
            del instance_arguments["resetn"]
            instance_arguments["reset_n"] = "resetn"
        else:
            instance_arguments["reset_n"] = "1'b1"
        instance_arguments["gpio"] = f"{{{', '.join(reversed(gpios))}}}"

        return instances

    @classmethod
    def extra_files(cls, parent, instances):
        for instance in instances:
            uid = instance.plugin_setup["uid"]
            os.makedirs(os.path.join(parent.gateware_path, f"src_{uid}"), exist_ok=True)

            log = os.path.join(parent.gateware_path, f"src_{uid}", "compile.log")
            print(f"  INFO: {uid}: running compiler script: {log}")
            ret = os.system(f"cd {parent.gateware_path}/src_{uid} && make clean prog.bin > compile.log 2>&1")
            if ret != 0:
                print(f"  ERROR: {uid}: running compiler script")
                for line in open(log, "r").read().split("\n"):
                    print(f"    {line}")
                exit(1)
