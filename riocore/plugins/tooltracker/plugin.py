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
        self.FILES = ["tooltracker.py"]
        self.OPTIONS = {
            "debug": {
                "type": bool,
                "default": False,
            },
            "display": {
                "type": "select",
                "default": "bar",
                "options": ["off", "bar", "meter"],
            },
            "section": {
                "type": str,
                "default": "tooltracker",
            },
        }

    def hal(self, parent):
        display = self.plugin_setup.get("display", self.option_default("display"))
        section = self.plugin_setup.get("section", self.option_default("section"))
        if display != "off":
            parent.vcp_values.append(
                {
                    "direction": "input",
                    "halname": "tooltracker.num",
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
                    "halname": "tooltracker.time",
                    "userconfig": {
                        "display": {
                            "section": section,
                            "group": "Tooltracker",
                            "title": "Time",
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
                    "halname": "tooltracker.limit",
                    "userconfig": {
                        "display": {
                            "section": section,
                            "group": "Tooltracker",
                            "title": "Limit",
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
                            "region": [[0, 75, "green"], [75, 90, "yellow"], [90, 100, "red"]],
                        },
                    },
                },
            )
            parent.vcp_values.append(
                {
                    "direction": "input",
                    "halname": "tooltracker.warning",
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
                    "halname": "tooltracker.critical",
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
