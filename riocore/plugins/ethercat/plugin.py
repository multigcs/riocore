import json
import os
import sys

import riocore

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
                    "GPIO",
                    "ek1100",
                    "el1008",
                    "el2008",
                    "el7411",
                ],
                "description": "Type",
            },
        }
        self.json_data = None
        node_type = self.plugin_setup.get("node_type", self.option_default("node_type"))
        if node_type == "Master":
            self.TYPE = "base"
            self.IMAGE_SHOW = True
            self.IMAGE = "image.png"
            self.INFO = "Ethercat - Master"
            self.PINDEFAULTS = {
                "BUS:out": {
                    "pin": f"{self.instances_name}:BUS:out",
                    "comment": "ethercat-master",
                    "pos": [100, 110],
                    "direction": "all",
                    "edge": "source",
                    "type": "ETHERCAT",
                },
            }

        elif node_type == "ek1100":
            self.IMAGE_SHOW = True
            self.IMAGE = "modules/ek1100.png"
            self.INFO = "EtherCAT Coupler"
            self.PINDEFAULTS = {
                "BUS:in": {
                    "direction": "all",
                    "edge": "target",
                    "type": "ETHERCAT",
                    "pos": (70, 165),
                },
                "BUS:out": {
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
            for key in self.plugin_setup.get("sub", {}):
                self.plugin_setup["sub"][key]["keep"] = False
            for mn, module in enumerate(modules.split()):
                key = f"{self.instances_name}-{mn}"
                if "sub" not in self.plugin_setup:
                    self.plugin_setup["sub"] = {}
                if key not in self.plugin_setup["sub"]:
                    self.plugin_setup["sub"][key] = {"type": "ethercat", "node_type": module, "uid": f"{puid}-{mn}", "rpos": [px, 0.0]}
                else:
                    if self.plugin_setup["sub"][key]["node_type"] != module:
                        self.plugin_setup["sub"][key] = {"type": "ethercat", "node_type": module, "uid": f"{puid}-{mn}", "rpos": [px, 0.0]}
                    self.plugin_setup["sub"][key]["type"] = "ethercat"
                self.plugin_setup["sub"][key]["node_type"] = module
                self.plugin_setup["sub"][key]["rpos"] = [px, 0.0]
                self.plugin_setup["sub"][key]["uid"] = f"{puid}-{mn}"
                self.plugin_setup["sub"][key]["keep"] = True
                self.SUB_PLUGINS.append(self.plugin_setup["sub"][key])
                px += 75

            for key in list(self.plugin_setup.get("sub", {}).keys()):
                if self.plugin_setup["sub"][key]["keep"]:
                    del self.plugin_setup["sub"][key]["keep"]
                else:
                    del self.plugin_setup["sub"][key]

        elif node_type == "Servo/Stepper":
            self.TYPE = "joint"
            self.IMAGE = "modules/ethercat-servo.png"
            self.IMAGE_SHOW = True
            self.INFO = "EtherCAT Servo"
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
                "BUS:in": {
                    "direction": "all",
                    "edge": "target",
                    "type": "ETHERCAT",
                    "pos": [95, 270],
                },
                "BUS:out": {
                    "direction": "all",
                    "edge": "source",
                    "type": "ETHERCAT",
                    "pos": [170, 270],
                },
            }
            self.SIGNALS = {
                "position-cmd": {
                    "direction": "output",
                    "absolute": False,
                    "description": "set position",
                    "pos": [25, 700],
                },
                "position-fb": {
                    "direction": "input",
                    "unit": "steps",
                    "absolute": False,
                    "description": "position feedback",
                    "pos": [25, 730],
                },
                "position-scale": {
                    "direction": "output",
                    "absolute": False,
                    "description": "steps / unit",
                    "pos": [25, 760],
                },
            }
            din = self.plugin_setup.get("din", self.option_default("din"))
            if din:
                for pn, pin in enumerate(
                    (
                        "limit-neg",
                        "limit-pos",
                        "home-switch",
                        "din1",
                        "din2",
                        "din3",
                        "din4",
                    )
                ):
                    self.SIGNALS[f"{pin}"] = {
                        "direction": "input",
                        "bool": True,
                        "pos": [25, 370 + pn * 30],
                    }
        elif node_type == "GPIO":
            self.PINDEFAULTS = {
                "BUS:in": {
                    "direction": "input",
                    "edge": "target",
                    "type": "ETHERCAT",
                },
                "BUS:out": {
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

        elif os.path.exists(os.path.join(os.path.dirname(__file__), "modules", f"module_{node_type}.json")):
            self.json_data = json.loads(open(os.path.join(os.path.dirname(__file__), "modules", f"module_{node_type}.json")).read())
            self.IMAGE_SHOW = True
            self.IMAGE = f"modules/module_{node_type}.png"
            self.INFO = self.json_data.get("info", "EtherCAT Module")
            self.DESCRIPTION = self.json_data.get("description", self.DESCRIPTION)
            self.PINDEFAULTS = {}
            self.SIGNALS = {}
            for pin_name, pin_data in self.json_data["pins"].items():
                if pin_data["type"] == "SIGNAL":
                    self.SIGNALS[pin_name] = pin_data
                else:
                    pin_data["suffix"] = pin_data["pin"]
                    pin_data["pin"] = f"{self.instances_name}:{pin_name}"
                    self.PINDEFAULTS[pin_name] = pin_data

            for option_name, option_data in self.json_data.get("options", {}).items():
                option_data["type"] = {"float": float, "bool": bool}.get(option_data["type"], option_data["type"])
                self.OPTIONS[option_name] = option_data

        else:
            riocore.log(f"ethercat: node_type not found: {node_type}")
            self.INFO = "EtherCAT Placeholder / Unsupported Device"
            self.PINDEFAULTS = {
                "BUS:in": {
                    "direction": "input",
                    "edge": "target",
                    "type": "ETHERCAT",
                },
                "BUS:out": {
                    "direction": "output",
                    "edge": "source",
                    "type": "ETHERCAT",
                },
            }
            self.SIGNALS = {}

        self.PREFIX_CIA402 = ""
        self.inverted_outputs = []

    @classmethod
    def update_prefixes(cls, parent, instances):
        cia402_num = 0
        lcec_num = 0
        for instance in instances:
            node_type = instance.plugin_setup.get("node_type", instance.option_default("node_type"))
            instance.PREFIX = f"lcec.{lcec_num}.{instance.instances_name}"
            if node_type == "Servo/Stepper":
                instance.PREFIX_CIA402 = f"cia402.{cia402_num}"
                cia402_num += 1

    def update_pins(self, parent):
        self.inverted_outputs = []
        for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=self.instances_name):
            psetup = connected_pin["setup"]
            pin = connected_pin["pin"]
            direction = connected_pin["direction"]
            inverted = connected_pin["inverted"]
            if pin in self.PINDEFAULTS and "pin" in self.PINDEFAULTS[pin] and not pin.startswith("BUS:"):
                if inverted:
                    if direction == "input":
                        psetup["pin"] = f"{self.PREFIX}.{self.PINDEFAULTS[pin]['suffix']}-not"
                    else:
                        psetup["pin"] = f"{self.PREFIX}.{self.PINDEFAULTS[pin]['suffix']}"
                        self.inverted_outputs.append(psetup["pin"])
                else:
                    psetup["pin"] = f"{self.PREFIX}.{self.PINDEFAULTS[pin]['suffix']}"

    @classmethod
    def extra_files(cls, parent, instances):
        output = []
        output.append("<masters>")
        servo_period = parent.project.config["jdata"].get("linuxcnc", {}).get("ini", {}).get("EMCMOT", {}).get("SERVO_PERIOD", 1000000)

        master = None
        for instance in instances:
            node_type = instance.plugin_setup.get("node_type", instance.option_default("node_type"))
            if node_type == "Master":
                master = instance
        if not master:
            print("no master found")
            sys.exit(1)

        last = master.instances_name
        found_next = True
        bus_list = []
        while found_next:
            found_next = False
            for instance in instances:
                if instance in bus_list:
                    continue
                if last == instance.instances_name:
                    # is master
                    continue

                node_type = instance.plugin_setup.get("node_type", instance.option_default("node_type"))
                sub_parent = instance.plugin_setup.get("parent")
                if sub_parent and sub_parent.instances_name == last:
                    bus_list.append(instance)
                    found_next = True
                    break
                if instance.plugin_setup.get("pins", {}).get("BUS:in", {}).get("pin") == f"{last}:BUS:out":
                    bus_list.append(instance)
                    found_next = True
                    last = instance.instances_name
                    break

        output.append(f'  <master idx="0" appTimePeriod="{servo_period}" refClockSyncCycles="1">')
        for idx, instance in enumerate(bus_list):
            node_type = instance.plugin_setup.get("node_type", instance.option_default("node_type"))
            # grep "{\"E[A-Z][0-9][0-9][0-9][0-9]\", LCEC_\|BECKHOFF_AOUT_DEVICE(\"" linuxcnc-ethercat-1.40.0/src/devices/lcec_*.c  | sed "s/.*{\"\|.*BECKHOFF_AOUT_DEVICE(\"//g" | cut -d"\"" -f1 | sort -u | awk '{print "\""$1"\","}
            lcec_supported = {
                "EJ4002",
                "EJ4004",
                "EJ4008",
                "EJ4018",
                "EJ4024",
                "EJ4132",
                "EJ4134",
                "EJ5002",
                "EK1100",
                "EK1101",
                "EK1110",
                "EK1122",
                "EL1002",
                "EL1004",
                "EL1008",
                "EL1012",
                "EL1014",
                "EL1018",
                "EL1024",
                "EL1034",
                "EL1084",
                "EL1088",
                "EL1094",
                "EL1098",
                "EL1104",
                "EL1114",
                "EL1124",
                "EL1134",
                "EL1144",
                "EL1804",
                "EL1808",
                "EL1809",
                "EL1819",
                "EL1904",
                "EL2002",
                "EL2004",
                "EL2008",
                "EL2022",
                "EL2024",
                "EL2032",
                "EL2034",
                "EL2042",
                "EL2084",
                "EL2088",
                "EL2124",
                "EL2202",
                "EL2521",
                "EL2612",
                "EL2622",
                "EL2624",
                "EL2634",
                "EL2652",
                "EL2798",
                "EL2808",
                "EL2809",
                "EL2828",
                "EL2904",
                "EL3102",
                "EL3112",
                "EL3122",
                "EL3142",
                "EL3152",
                "EL3162",
                "EL3255",
                "EL3403",
                "EL4001",
                "EL4002",
                "EL4004",
                "EL4008",
                "EL4011",
                "EL4012",
                "EL4014",
                "EL4018",
                "EL4021",
                "EL4022",
                "EL4024",
                "EL4028",
                "EL4031",
                "EL4032",
                "EL4034",
                "EL4038",
                "EL4102",
                "EL4104",
                "EL4112",
                "EL4114",
                "EL4122",
                "EL4124",
                "EL4132",
                "EL4134",
                "EL5002",
                "EL5032",
                "EL5101",
                "EL5102",
                "EL5151",
                "EL5152",
                "EL6090",
                "EL6900",
                "EL7031",
                "EL7041",
                "EL7211",
                "EL7221",
                "EL7342",
                "EL7411",
                "EL9410",
                "EL9505",
                "EL9508",
                "EL9510",
                "EL9512",
                "EL9515",
                "EL9576",
                "EM7004",
                "EP1008",
                "EP1018",
                "EP1122",
                "EP1819",
                "EP2008",
                "EP2028",
                "EP2809",
                "EP4174",
                "EP7041",
                "EP9214",
            }
            if node_type.upper() in lcec_supported:
                output.append(f'    <slave idx="{idx}" type="{node_type.upper()}" name="{instance.plugin_setup["uid"]}"/>')
            elif node_type == "Servo/Stepper":
                vid = instance.plugin_setup.get("vid", instance.option_default("vid"))
                pid = instance.plugin_setup.get("pid", instance.option_default("pid"))
                din = instance.plugin_setup.get("din", instance.option_default("din"))
                extra_atrributes = []
                if vid:
                    extra_atrributes.append(f'vid="{vid}"')
                if pid:
                    extra_atrributes.append(f'pid="{pid}"')
                output.append(f'    <slave idx="{idx}" type="generic" {" ".join(extra_atrributes)} configPdos="true" name="{instance.instances_name}">')
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
                output.append(f'    <slave idx="{idx}" type="generic" vid="00001337" pid="000004d2" configPdos="true" name="{instance.instances_name}">')
                output.append('      <dcConf assignActivate="300" sync0Cycle="*1" sync0Shift="25000"/>')
                output.append('      <watchdog divider="2498" intervals="1000"/>')
                output.append('      <syncManager idx="1" dir="in">')
                output.append('        <pdo idx="1A00">')
                for pin in range(32):
                    output.append(f'          <pdoEntry idx="0006" subIdx="{pin:02x}" bitLen="1" halPin="in{pin}" halType="bit"/>')
                output.append("        </pdo>")
                output.append("      </syncManager>")
                output.append("    </slave>")
            else:
                output.append(f'    <slave idx="{idx}" type="generic" name="{instance.plugin_setup["uid"]}"/>')

        output.append("  </master>")
        output.append("</masters>")
        target = os.path.join(parent.component_path, "ethercat-conf.xml")
        open(target, "w").write("\n".join(output))

    @classmethod
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
        for output in self.inverted_outputs:
            parent.halg.setp_add(f"{output}-invert", "1")
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
            parent.halg.joint_add(parent, axis_name, joint_n, "position", cmd_halname, feedback_halname=feedback_halname, scale_halname=scale_halname, enable_halname=enable_halname, fault_halname=fault_halname)
            parent.halg.setp_add(f"{cia402}.csp-mode", "1")
        elif self.json_data:
            for option_name in self.json_data.get("options", {}):
                option_value = self.plugin_setup.get(option_name, self.option_default(option_name))
                parent.halg.setp_add(f"{lcec}.{option_name}", option_value)
