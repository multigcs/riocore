from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "camjog"
        self.COMPONENT = "camjog"
        self.INFO = "gui component to jog via camera image"
        self.DESCRIPTION = ""
        self.KEYWORDS = "jog gui robot"
        self.TYPE = "base"
        self.IMAGE_SHOW = True
        self.PLUGIN_TYPE = "gpio"
        self.IMAGE = ""
        self.ORIGIN = ""
        self.SIGNALS = {}
        self.PINDEFAULTS = {}
        self.FILES = ["camjog.py"]
        self.OPTIONS = {
            "device": {
                "type": str,
                "default": "/dev/video0",
            },
            "width": {
                "type": int,
                "default": 640,
            },
            "height": {
                "type": int,
                "default": 480,
            },
            "scale": {
                "type": float,
                "default": 1.0,
            },
            "tabname": {
                "type": str,
                "default": "camjog",
            },
        }

    def ini(self, parent, ini_setup):
        camjog_num = 0
        camjog_device = self.plugin_setup.get("device", self.option_default("device"))
        width = self.plugin_setup.get("width", self.option_default("width"))
        height = self.plugin_setup.get("height", self.option_default("height"))
        scale = self.plugin_setup.get("scale", self.option_default("scale"))
        tabname = self.plugin_setup.get("tabname", self.option_default("tabname"))
        ini_setup["DISPLAY"][f"EMBED_TAB_NAME|CAMJOG{camjog_num}"] = tabname
        if parent.gui_tablocation:
            ini_setup["DISPLAY"][f"EMBED_TAB_LOCATION|CAMJOG{camjog_num}"] = parent.gui_tablocation
        cmd_args = ["halcmd loadusr -Wn camjog ./camjog.py"]
        cmd_args.append("--xid {XID}")
        if camjog_device.startswith("/dev/video"):
            cmd_args.append(f"--video {camjog_device[-1]}")
        elif camjog_device.startswith("rtsp://"):
            cmd_args.append(f"--camera {camjog_device}")
        elif len(camjog_device) <= 2:
            cmd_args.append(f"--video {camjog_device}")
        else:
            cmd_args.append(f"--camera {camjog_device[-1]}")
        cmd_args.append(f"--width {width}")
        cmd_args.append(f"--height {height}")
        cmd_args.append(f"--scale {scale}")
        ini_setup["DISPLAY"][f"EMBED_TAB_COMMAND|CAMJOG{camjog_num}"] = f"{' '.join(cmd_args)}"
