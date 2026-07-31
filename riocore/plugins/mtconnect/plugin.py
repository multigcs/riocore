import os
import shutil

from riocore.plugins import PluginBase

riocore_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "mtconnect"
        self.INFO = "mtconnect support"
        self.DESCRIPTION = "mtconnect agent"
        self.URL = "https://github.com/sliptonic/linuxcnc/tree/feature/mtconnect-agent"
        self.ORIGIN = "https://github.com/sliptonic/linuxcnc/tree/feature/mtconnect-agent"
        self.NEEDS = []
        self.KEYWORDS = "log mqtt mtconnect digital-twin"
        self.TYPE = "base"
        self.IMAGE_SHOW = True
        self.IMAGE = ""
        self.ORIGIN = ""
        self.SIGNALS = {}
        self.PINDEFAULTS = {}
        self.FILES = []
        self.OPTIONS = {
            "device_name": {
                "type": str,
                "default": "mtconnect_demo",
            },
            "uuid": {
                "type": str,
                "default": "linuxcnc-rio-0001",
            },
            "sample_hz": {
                "type": int,
                "min": 1,
                "max": 1000,
                "default": 10,
            },
            "transport": {
                "type": "select",
                "options": ["http", "mqtt", "both"],
                "default": "http",
            },
            "http_port": {
                "type": int,
                "min": 1024,
                "max": 49151,
                "default": 5000,
            },
            "mqtt_broker": {
                "type": str,
                "default": "localhost",
            },
            "mqtt_port": {
                "type": int,
                "min": 10,
                "max": 65535,
                "default": 1883,
            },
            "mqtt_prefix": {
                "type": str,
                "default": "MTConnect",
            },
            "model_auto": {
                "type": str,
                "default": "1",
            },
            "model_chain": {
                "type": str,
                "default": "X Y Z",
            },
            "model_parent_z": {
                "type": str,
                "default": "BASE",
            },
            "model_invert": {
                "type": str,
                "default": "X Y",
            },
        }

    def ini(self, parent, ini_setup):
        device_name = self.plugin_setup.get("device_name", self.option_default("device_name"))
        uuid = self.plugin_setup.get("uuid", self.option_default("uuid"))
        transport = self.plugin_setup.get("transport", self.option_default("transport"))
        http_port = self.plugin_setup.get("http_port", self.option_default("http_port"))
        sample_hz = self.plugin_setup.get("sample_hz", self.option_default("sample_hz"))
        model_auto = self.plugin_setup.get("model_auto", self.option_default("model_auto"))
        model_chain = self.plugin_setup.get("model_chain", self.option_default("model_chain"))
        model_parent_z = self.plugin_setup.get("model_parent_z", self.option_default("model_parent_z"))
        model_invert = self.plugin_setup.get("model_invert", self.option_default("model_invert"))
        mqtt_broker = self.plugin_setup.get("mqtt_broker", self.option_default("mqtt_broker"))
        mqtt_port = self.plugin_setup.get("mqtt_port", self.option_default("mqtt_port"))
        mqtt_prefix = self.plugin_setup.get("mqtt_prefix", self.option_default("mqtt_prefix"))

        ini_setup["MTCONNECT"] = {
            "ENABLE": "1",
            "DEVICE_NAME": device_name,
            "UUID": uuid,
            "HTTP_PORT": http_port,
            "TRANSPORT": transport,
            "SAMPLE_HZ": sample_hz,
            "MODEL_AUTO": model_auto,
            "MODEL_CHAIN": model_chain,
            "MODEL_PARENT_Z": model_parent_z,
            "MODEL_INVERT": model_invert,
        }
        if transport in {"mqtt", "both"}:
            ini_setup["MTCONNECT"]["MQTT_BROKER"] = mqtt_broker
            ini_setup["MTCONNECT"]["MQTT_PORT"] = mqtt_port
            ini_setup["MTCONNECT"]["MQTT_PREFIX"] = mqtt_prefix

        ini_setup["APPLICATIONS"] = {
            "DELAY": "3",
            "APP": "./mtconnect-agent",
        }

    @classmethod
    def extra_files(cls, parent, instances):
        source_path = os.path.join(os.path.dirname(__file__), "files")
        target_path = os.path.join(parent.configuration_path)
        shutil.copytree(source_path, target_path, dirs_exist_ok=True)
