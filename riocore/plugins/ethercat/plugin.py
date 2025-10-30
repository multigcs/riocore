import os
from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "ethercat"
        self.COMPONENT = "ethercat"
        self.INFO = "experimental ethercat driver"
        self.EXPERIMENTAL = True
        self.DESCRIPTION = ""
        self.KEYWORDS = "stepper servo master"
        self.IMAGES = ["ethercatservo"]
        self.PLUGIN_TYPE = "gpio"
        self.ORIGIN = ""
        self.OPTIONS = {}
        self.SIGNALS = {}
        self.mode_pins = {}
        self.OPTIONS = {
            "node_type": {
                "default": "Servo/Stepper",
                "type": "select",
                "options": [
                    "Master",
                    "Servo/Stepper",
                    "GPIOs",
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
        elif node_type == "Servo/Stepper":
            self.TYPE = "joint"
            self.JOINT_MODE = "position"
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

    def update_prefixes(cls, instances):
        cia402_num = 0
        lcec_num = 0
        for instance in instances:
            # node_type = instance.plugin_setup.get("node_type", instance.option_default("node_type"))
            instance.PREFIX = f"lcec.{lcec_num}.{instance.title}"
            instance.PREFIX_CIA402 = f"cia402.{cia402_num}"

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
            if node_type == "Servo/Stepper":
                output.append(f'    <slave idx="{idx}" type="generic" vid="00400000" pid="00000715" configPdos="true" name="{instance.title}">')
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
                output.append('          <pdoEntry idx="60FD" subIdx="00" bitLen="32" halPin="DI-status" halType="u32"/>')
                output.append('          <pdoEntry idx="60F4" subIdx="00" bitLen="32" halPin="follow-error" halType="s32"/>')
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
        # lcec_num = 0
        for instance in instances:
            node_type = instance.plugin_setup.get("node_type", instance.option_default("node_type"))
            if node_type == "Master":
                cia402_num += 1

        output.append(f"loadrt cia402 count={cia402_num}")
        output.append("addf lcec.read-all servo-thread")
        cia402_num = 0
        # lcec_num = 0
        for instance in instances:
            node_type = instance.plugin_setup.get("node_type", instance.option_default("node_type"))
            if node_type == "Master":
                # TODO: .PREFIX_CIA402
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

        if node_type == "Master":
            parent.halg.setp_add(f"{cia402}.csp-mode", "1")
