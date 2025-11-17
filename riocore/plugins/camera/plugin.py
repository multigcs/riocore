from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "camera"
        self.COMPONENT = "camera"
        self.INFO = "gui component to display an camera image"
        self.DESCRIPTION = ""
        self.KEYWORDS = "jog gui robot"
        self.TYPE = "base"
        self.IMAGE_SHOW = True
        self.PLUGIN_TYPE = "gpio"
        self.IMAGE = ""
        self.ORIGIN = ""
        self.SIGNALS = {}
        self.PINDEFAULTS = {}
        self.FILES = []
        self.OPTIONS = {
            "device": {
                "type": str,
                "default": "/dev/video0",
            },
        }

    def ini(self, parent, ini_setup):
        tabname = "camera"
        ini_setup["DISPLAY"]["EMBED_TAB_NAME|camera"] = tabname
        if parent.gui_tablocation:
            ini_setup["DISPLAY"]["EMBED_TAB_LOCATION|camera"] = parent.gui_tablocation

        camera_device = self.plugin_setup.get("device", self.option_default("device"))
        ini_setup["DISPLAY"]["EMBED_TAB_COMMAND|camera"] = f"mplayer -wid {{XID}} tv:// -tv driver=v4l2:device={camera_device} -vf rectangle=-1:2:-1:240,rectangle=2:-1:320:-1 -really-quiet"
