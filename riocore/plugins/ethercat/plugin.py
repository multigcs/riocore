import os
from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "ethercat"
        self.COMPONENT = "ethercat"
        self.INFO = "experimental ethercat plugin"
        self.EXPERIMENTAL = True
        self.DESCRIPTION = ""
        self.KEYWORDS = "stepper servo master"
        self.IMAGES = []
        self.PLUGIN_TYPE = "gpio"
        self.ORIGIN = ""
        self.OPTIONS = {}
        self.SIGNALS = {}
        self.mode_pins = {}
        self.OPTIONS = {
            "node_type": {
                "default": "Master",
                "type": "select",
                "options": [
                    "Master",
                    "Servo/Stepper",
                    "GPIOs",
                    "ek1100",
                    "el1008",
                    "el2008",
                ],
                "description": "Type",
            },
            "idx": {
                "default": -2,
                "type": int,
                "min": -2,
                "max": 255,
                "description": "bus-index",
            },
        }

        node_type = self.plugin_setup.get("node_type", self.option_default("node_type"))
        if node_type == "Master":
            self.TYPE = "base"
            self.IMAGE_SHOW = True
            self.IMAGE = "image.png"
            self.PINDEFAULTS = {
                "out": {
                    "pin": f"{self.instances_name}:master",
                    "comment": "ethercat-master",
                    "pos": [100, 110],
                    "direction": "all",
                    "edge": "source",
                    "type": "ETHERCAT",
                },
            }

        elif node_type == "ek1100":
            self.IMAGE_SHOW = True
            self.IMAGE = "ek1100.png"

            self.PINDEFAULTS = {
                "in": {
                    "direction": "all",
                    "edge": "target",
                    "type": "ETHERCAT",
                    "pos": (70, 165),
                },
                "out": {
                    "direction": "all",
                    "edge": "source",
                    "type": "ETHERCAT",
                    "pos": (70, 355),
                },
            }

            self.OPTIONS.update(
                {
                    "modules": {
                        "default": "",
                        "type": str,
                        "description": "list of slave modules",
                    },
                }
            )
            modules = self.plugin_setup.get("modules", self.option_default("modules")).strip()

            px = 263
            self.SUB_PLUGINS = []
            puid = self.plugin_setup.get("uid")
            for mn, module in enumerate(modules.split()):
                mn = str(mn)
                if "sub" not in self.plugin_setup:
                    self.plugin_setup["sub"] = {}

                if mn not in self.plugin_setup["sub"]:
                    self.plugin_setup["sub"][mn] = {"type": "ethercat", "node_type": module, "uid": f"{puid}-{mn}", "rpos": [px, 0.0], "idx": -2}
                self.plugin_setup["sub"][mn]["node_type"] = module
                self.plugin_setup["sub"][mn]["rpos"] = [px, 0.0]
                self.plugin_setup["sub"][mn]["uid"] = f"{puid}-{mn}"
                self.SUB_PLUGINS.append(self.plugin_setup["sub"][mn])
                px += 75

        elif node_type == "el1008":
            self.IMAGE_SHOW = True
            self.IMAGE = "el1008.png"
            self.PINDEFAULTS = {
                "IN:I0": {
                    "direction": "input",
                    "edge": "source",
                    "type": "GPIO",
                    "pin": "din-0",
                    "pos": (17, 217),
                },
                "IN:I1": {
                    "direction": "input",
                    "edge": "source",
                    "type": "GPIO",
                    "pin": "din-1",
                    "pos": (50, 217),
                },
                "IN:I2": {
                    "direction": "input",
                    "edge": "source",
                    "type": "GPIO",
                    "pin": "din-2",
                    "pos": (17, 322),
                },
                "IN:I3": {
                    "direction": "input",
                    "edge": "source",
                    "type": "GPIO",
                    "pin": "din-3",
                    "pos": (50, 322),
                },
                "IN:I4": {
                    "direction": "input",
                    "edge": "source",
                    "type": "GPIO",
                    "pin": "din-4",
                    "pos": (17, 437),
                },
                "IN:I5": {
                    "direction": "input",
                    "edge": "source",
                    "type": "GPIO",
                    "pin": "din-5",
                    "pos": (50, 437),
                },
                "IN:I6": {
                    "direction": "input",
                    "edge": "source",
                    "type": "GPIO",
                    "pin": "din-6",
                    "pos": (17, 552),
                },
                "IN:I7": {
                    "direction": "input",
                    "edge": "source",
                    "type": "GPIO",
                    "pin": "din-7",
                    "pos": (50, 552),
                },
            }

        elif node_type == "el2008":
            self.IMAGE_SHOW = True
            self.IMAGE = "el2008.png"
            self.PINDEFAULTS = {
                "OUT:O0": {
                    "direction": "output",
                    "edge": "source",
                    "type": "GPIO",
                    "pin": "dout-0",
                    "pos": (17, 217),
                },
                "OUT:O1": {
                    "direction": "output",
                    "edge": "source",
                    "type": "GPIO",
                    "pin": "dout-1",
                    "pos": (50, 217),
                },
                "OUT:O2": {
                    "direction": "output",
                    "edge": "source",
                    "type": "GPIO",
                    "pin": "dout-2",
                    "pos": (17, 322),
                },
                "OUT:O3": {
                    "direction": "output",
                    "edge": "source",
                    "type": "GPIO",
                    "pin": "dout-3",
                    "pos": (50, 322),
                },
                "OUT:O4": {
                    "direction": "output",
                    "edge": "source",
                    "type": "GPIO",
                    "pin": "dout-4",
                    "pos": (17, 437),
                },
                "OUT:O5": {
                    "direction": "output",
                    "edge": "source",
                    "type": "GPIO",
                    "pin": "dout-5",
                    "pos": (50, 437),
                },
                "OUT:O6": {
                    "direction": "output",
                    "edge": "source",
                    "type": "GPIO",
                    "pin": "dout-6",
                    "pos": (17, 552),
                },
                "OUT:O7": {
                    "direction": "output",
                    "edge": "source",
                    "type": "GPIO",
                    "pin": "dout-7",
                    "pos": (50, 552),
                },
            }

        elif node_type == "Servo/Stepper":
            self.TYPE = "joint"
            self.IMAGES = ["ethercatservo"]
            self.JOINT_MODE = "position"
            self.OPTIONS.update(
                {
                    "vid": {
                        "default": "00400000",
                        "type": str,
                        "description": "device vid",
                    },
                    "pid": {
                        "default": "00000715",
                        "type": str,
                        "description": "device pid",
                    },
                    "din": {
                        "default": True,
                        "type": bool,
                        "description": "activate digital inputs (home / limits /...)",
                    },
                }
            )
            self.PINDEFAULTS = {
                "in": {
                    "direction": "all",
                    "edge": "target",
                    "type": "ETHERCAT",
                },
                "out": {
                    "direction": "all",
                    "edge": "source",
                    "type": "ETHERCAT",
                },
            }
            self.SIGNALS = {
                "position-cmd": {
                    "direction": "output",
                    "absolute": False,
                    "description": "set position",
                },
                "position-fb": {
                    "direction": "input",
                    "unit": "steps",
                    "absolute": False,
                    "description": "position feedback",
                },
                "position-scale": {
                    "direction": "output",
                    "absolute": False,
                    "description": "steps / unit",
                },
            }
            din = self.plugin_setup.get("din", self.option_default("din"))
            if din:
                for pin in ("limit-neg", "limit-pos", "home-switch", "din1", "din2", "din3", "din4"):
                    self.SIGNALS[f"{pin}"] = {
                        "direction": "input",
                        "bool": True,
                    }
        elif node_type == "GPIO":
            self.PINDEFAULTS = {
                "in": {
                    "direction": "input",
                    "edge": "target",
                    "type": "ETHERCAT",
                },
                "out": {
                    "direction": "output",
                    "edge": "source",
                    "type": "ETHERCAT",
                },
            }
            self.SIGNALS = {}
            for pin in range(32):
                self.SIGNALS[f"in{pin}"] = {
                    "direction": "input",
                    "bool": True,
                }
        else:
            self.PINDEFAULTS = {
                "in": {
                    "direction": "input",
                    "edge": "target",
                    "type": "ETHERCAT",
                },
                "out": {
                    "direction": "output",
                    "edge": "source",
                    "type": "ETHERCAT",
                },
            }
        self.PREFIX_CIA402 = ""

    def update_prefixes(cls, parent, instances):
        cia402_num = 0
        lcec_num = 0
        for instance in instances:
            node_type = instance.plugin_setup.get("node_type", instance.option_default("node_type"))
            instance.PREFIX = f"lcec.{lcec_num}.{instance.title}"
            if node_type == "Servo/Stepper":
                instance.PREFIX_CIA402 = f"cia402.{cia402_num}"
                cia402_num += 1

    def update_pins(self, parent):
        for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=self.instances_name):
            psetup = connected_pin["setup"]
            pin = connected_pin["pin"]
            if pin in self.PINDEFAULTS and "pin" in self.PINDEFAULTS[pin]:
                psetup["pin"] = f"{self.PREFIX}.{self.PINDEFAULTS[pin]['pin']}"

    def extra_files(cls, parent, instances):
        output = []
        output.append("<masters>")
        servo_period = parent.project.config["jdata"].get("linuxcnc", {}).get("ini", {}).get("EMCMOT", {}).get("SERVO_PERIOD", 1000000)
        output.append(f'  <master idx="0" appTimePeriod="{servo_period}" refClockSyncCycles="1">')
        for num, instance in enumerate(instances):
            node_type = instance.plugin_setup.get("node_type", instance.option_default("node_type"))
            idx = instance.plugin_setup.get("idx", instance.option_default("idx"))
            if idx < 0 or node_type == "Master":
                # only connected slaves
                continue
            elif node_type in {"ek1100", "el2008", "el1008"}:
                output.append(f'    <slave idx="{idx}" type="{node_type.upper()}" name="{instance.plugin_setup["uid"]}"/>')
            elif node_type == "Servo/Stepper":
                vid = instance.plugin_setup.get("vid", instance.option_default("vid"))
                pid = instance.plugin_setup.get("pid", instance.option_default("pid"))
                din = instance.plugin_setup.get("din", instance.option_default("din"))
                output.append(f'    <slave idx="{idx}" type="generic" vid="{vid}" pid="{pid}" configPdos="true" name="{instance.title}">')
                output.append('      <dcConf assignActivate="300" sync0Cycle="*1" sync0Shift="25000"/>')
                output.append('      <watchdog divider="2498" intervals="1000"/>')
                output.append('      <syncManager idx="2" dir="out">')
                output.append('        <pdo idx="1600">')
                output.append('          <pdoEntry idx="6040" subIdx="00" bitLen="16" halPin="control-word" halType="u32"/>')
                output.append('          <pdoEntry idx="607A" subIdx="00" bitLen="32" halPin="target-position" halType="s32"/>')
                output.append('          <pdoEntry idx="60B8" subIdx="00" bitLen="16" halPin="touch-probe-function" halType="u32"/>')
                output.append("        </pdo>")
                output.append("      </syncManager>")
                output.append('      <syncManager idx="3" dir="in">')
                output.append('        <pdo idx="1A00">')
                output.append('          <pdoEntry idx="6041" subIdx="00" bitLen="16" halPin="status-word" halType="u32"/>')
                output.append('          <pdoEntry idx="6064" subIdx="00" bitLen="32" halPin="pos-actual" halType="s32"/>')
                output.append('          <pdoEntry idx="60BA" subIdx="00" bitLen="32" halPin="touch-probe-1" halType="s32"/>')
                output.append('          <pdoEntry idx="60BC" subIdx="00" bitLen="32" halPin="touch-probe-2" halType="s32"/>')
                output.append('          <pdoEntry idx="60B9" subIdx="00" bitLen="16" halPin="touch-probe-status" halType="s32"/>')
                output.append('          <pdoEntry idx="603F" subIdx="00" bitLen="16" halPin="fault-code" halType="s32"/>')
                output.append('          <pdoEntry idx="60F4" subIdx="00" bitLen="32" halPin="follow-error" halType="s32"/>')
                if din:
                    output.append('          <pdoEntry idx="60FD" subIdx="00" bitLen="32" halType="complex">')
                    output.append('            <complexEntry bitLen="1" halPin="limit-neg" halType="bit"/>')
                    output.append('            <complexEntry bitLen="1" halPin="limit-pos" halType="bit"/>')
                    output.append('            <complexEntry bitLen="1" halPin="home-switch" halType="bit"/>')
                    output.append('            <complexEntry bitLen="13" />')
                    output.append('            <complexEntry bitLen="1" halPin="din1" halType="bit"/>')
                    output.append('            <complexEntry bitLen="1" halPin="din2" halType="bit"/>')
                    output.append('            <complexEntry bitLen="1" halPin="din3" halType="bit"/>')
                    output.append('            <complexEntry bitLen="1" halPin="din4" halType="bit"/>')
                    output.append("          </pdoEntry>")
                output.append("        </pdo>")
                output.append("      </syncManager>")
                output.append("    </slave>")
            elif node_type == "GPIO":
                output.append(f'    <slave idx="{idx}" type="generic" vid="00001337" pid="000004d2" configPdos="true" name="{instance.title}">')
                output.append('      <dcConf assignActivate="300" sync0Cycle="*1" sync0Shift="25000"/>')
                output.append('      <watchdog divider="2498" intervals="1000"/>')
                output.append('      <syncManager idx="1" dir="in">')
                output.append('        <pdo idx="1A00">')
                for pin in range(32):
                    output.append(f'          <pdoEntry idx="0006" subIdx="{pin:02x}" bitLen="1" halPin="in{pin}" halType="bit"/>')
                output.append("        </pdo>")
                output.append("      </syncManager>")
                output.append("    </slave>")

        output.append("  </master>")
        output.append("</masters>")
        target = os.path.join(parent.component_path, "ethercat-conf.xml")
        open(target, "w").write("\n".join(output))

    def component_loader(cls, instances):
        output = []
        output.append("# ethercat component")
        output.append("loadusr -W lcec_conf ethercat-conf.xml")
        output.append("loadrt lcec")

        cia402_num = 0
        lcec_num = 0
        for instance in instances:
            node_type = instance.plugin_setup.get("node_type", instance.option_default("node_type"))
            if node_type == "Master":
                lcec_num += 1
            elif node_type == "Servo/Stepper":
                cia402_num += 1

        output.append(f"loadrt cia402 count={cia402_num}")
        output.append("addf lcec.read-all servo-thread")
        cia402_num = 0
        for instance in instances:
            node_type = instance.plugin_setup.get("node_type", instance.option_default("node_type"))
            if node_type == "Servo/Stepper":
                output.append(f"addf cia402.{cia402_num}.read-all servo-thread")
                output.append(f"addf cia402.{cia402_num}.write-all servo-thread")
                cia402_num += 1
        output.append("addf lcec.write-all servo-thread")
        output.append("")
        return "\n".join(output)

    def hal(self, parent):
        lcec = self.PREFIX
        cia402 = self.PREFIX_CIA402
        node_type = self.plugin_setup.get("node_type", self.option_default("node_type"))
        if node_type == "Servo/Stepper" and "joint_data" in self.plugin_setup:
            joint_data = self.plugin_setup["joint_data"]
            axis_name = joint_data["axis"]
            joint_n = joint_data["num"]

            cmd_halname = f"{cia402}.pos-cmd"
            feedback_halname = f"{cia402}.pos-fb"
            enable_halname = f"{cia402}.enable"
            scale_halname = f"{cia402}.pos-scale"
            fault_halname = f"{cia402}.drv-fault"

            parent.halg.net_add(f"{lcec}.status-word", f"{cia402}.statusword", f"j{joint_n}statusword")
            parent.halg.net_add(f"{lcec}.pos-actual", f"{cia402}.drv-actual-position", f"j{joint_n}drv-pos")
            parent.halg.net_add(f"{cia402}.controlword", f"{lcec}.control-word", f"j{joint_n}control")
            parent.halg.net_add(f"{cia402}.drv-target-position", f"{lcec}.target-position", f"j{joint_n}target-pos")
            parent.halg.joint_add(
                parent, axis_name, joint_n, "position", cmd_halname, feedback_halname=feedback_halname, scale_halname=scale_halname, enable_halname=enable_halname, fault_halname=fault_halname
            )
            parent.halg.setp_add(f"{cia402}.csp-mode", "1")
