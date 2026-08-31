import os
import shutil

from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "tooltracker"
        self.INFO = "simple tool time tracker"
        self.DESCRIPTION = "simple tool time tracker"
        self.KEYWORDS = "tool time tracker"
        self.TYPE = "base"
        self.IMAGE_SHOW = True
        self.NEEDS = []
        self.IMAGE = ""
        self.EXPERIMENTAL = True
        self.ORIGIN = ""
        self.SIGNALS = {}
        self.PINDEFAULTS = {}
        self.FILES = ["tooltracker.py", "tooledit.py"]
        self.OPTIONS = {
            "section": {
                "type": str,
                "default": "tooltracker",
                "comment": "vcp tab name",
            },
            "display": {
                "type": "select",
                "default": "bar",
                "options": ["off", "bar", "meter"],
                "comment": "percentage display type",
            },
            "sister": {
                "type": bool,
                "default": False,
                "comment": "manage sister tools (remap T)",
            },
        }

    def ini(self, parent, ini_setup):
        sister = self.plugin_setup.get("sister", self.option_default("sister"))
        if sister:
            ini_setup["RS274NGC"]["REMAP|prepare"] = "T python=prepare"
            # ini_setup["RS274NGC"]["REMAP|M6"] = "M6 modalgroup=6 ngc=change"
        ini_setup["DISPLAY"]["TOOL_EDITOR"] = "./tooledit.py"

    @classmethod
    def extra_files(cls, parent, instances):
        filenames = ["tttable.py"]
        sister = instances[0].plugin_setup.get("sister", instances[0].option_default("sister"))
        if sister:
            filenames.append("remap.py")
        for filename in filenames:
            source_path = os.path.join(os.path.dirname(__file__), filename)
            os.makedirs(os.path.join(parent.configuration_path, "python"), exist_ok=True)
            target_path = os.path.join(parent.configuration_path, "python", filename)
            shutil.copy(source_path, target_path)

    def hal(self, parent):
        display = self.plugin_setup.get("display", self.option_default("display"))
        section = self.plugin_setup.get("section", self.option_default("section"))
        parent.halg.net_add("halui.spindle.0.is-on", "tooltracker.running")
        parent.halg.net_add("halui.tool.number", "tooltracker.tool")
        if display != "off":
            parent.vcp_values.append(
                {
                    "direction": "input",
                    "halname": "tooltracker.tool",
                    "userconfig": {
                        "display": {
                            "section": section,
                            "group": "Tooltracker",
                            "title": "Number",
                            "type": "number_u32",
                            "unit": "#",
                        },
                    },
                },
            )
            parent.vcp_values.append(
                {
                    "direction": "input",
                    "halname": "tooltracker.timer",
                    "userconfig": {
                        "display": {
                            "section": section,
                            "group": "Tooltracker",
                            "title": "Timer",
                            "type": "number",
                            "unit": "s",
                            "format": "0.0f",
                        },
                    },
                },
            )
            parent.vcp_values.append(
                {
                    "direction": "input",
                    "halname": "tooltracker.warning_level",
                    "userconfig": {
                        "display": {
                            "section": section,
                            "group": "Tooltracker",
                            "title": "Warning",
                            "type": "number",
                            "unit": "s",
                            "format": "0.0f",
                        },
                    },
                },
            )
            parent.vcp_values.append(
                {
                    "direction": "input",
                    "halname": "tooltracker.critical_level",
                    "userconfig": {
                        "display": {
                            "section": section,
                            "group": "Tooltracker",
                            "title": "Critical",
                            "type": "number",
                            "unit": "s",
                            "format": "0.0f",
                        },
                    },
                },
            )
            parent.vcp_values.append(
                {
                    "direction": "input",
                    "halname": "tooltracker.percent",
                    "userconfig": {
                        "display": {
                            "section": section,
                            "group": "Tooltracker",
                            "title": "Livetime",
                            "type": display,
                            "unit": "%",
                            "format": "0.1f",
                            "min": 0.0,
                            "max": 100.0,
                            # "region": [[0, 75, "green"], [75, 90, "yellow"], [90, 100, "red"]],
                        },
                    },
                },
            )
            parent.vcp_values.append(
                {
                    "direction": "input",
                    "halname": "tooltracker.warning_flag",
                    "userconfig": {
                        "display": {
                            "section": section,
                            "group": "Tooltracker",
                            "title": "Warning",
                            "type": "rectled",
                            "color": "yellow",
                            "off_color": "green",
                        },
                    },
                },
            )
            parent.vcp_values.append(
                {
                    "direction": "input",
                    "halname": "tooltracker.critical_flag",
                    "userconfig": {
                        "display": {
                            "section": section,
                            "group": "Tooltracker",
                            "title": "Critical",
                            "type": "rectled",
                            "color": "red",
                            "off_color": "green",
                        },
                    },
                },
            )

    @classmethod
    def component_loader(cls, instances):
        debug = instances[0].plugin_setup.get("debug", instances[0].option_default("debug"))
        output = []
        args = ""
        if debug:
            args = " -d"
        output.append("# simple tooltracker")
        output.append(f"loadusr -Wn tooltracker ./tooltracker.py{args}")
        output.append("")
        return "\n".join(output)
