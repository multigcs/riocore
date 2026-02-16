from riocore import PluginImages
from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "image"
        self.COMPONENT = "image"
        self.INFO = "only an image for the flow plan"
        self.DESCRIPTION = ""
        self.KEYWORDS = ""
        self.IMAGES = list(PluginImages.images)
        self.PLUGIN_TYPE = "background"
