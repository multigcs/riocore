
from qtvcp.core import Status, Action
from qtvcp import logger

STATUS = Status()
ACTION = Action()
LOG = logger.getLogger(__name__)

class HandlerClass:

    def __init__(self, halcomp,widgets,paths):
        self.hal = halcomp
        self.w = widgets
        self.PATHS = paths

    def initialized__(self):
        pass

    def __getitem__(self, item):
        return getattr(self, item)
    def __setitem__(self, item, value):
        return setattr(self, item, value)

def get_handlers(halcomp,widgets,paths):
     return [HandlerClass(halcomp,widgets,paths)]
