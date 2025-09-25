import os

from qtpyvcp.widgets.dialogs.base_dialog import BaseDialog


class ZeroXY(BaseDialog):
    def __init__(self, ui_file):
        super(ZeroXY, self).__init__(stay_on_top=True, ui_file=ui_file)

    def open(self):
        super(ZeroXY, self).open()

    def on_close_button_clicked(self):
        super(ZeroXY, self).close()

    def on_zero_xy_button_clicked(self):
        super(ZeroXY, self).close()
