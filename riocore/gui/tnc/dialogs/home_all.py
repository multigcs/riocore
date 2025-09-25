import os

from qtpyvcp.widgets.dialogs.base_dialog import BaseDialog


class HomeAll(BaseDialog):
    def __init__(self, ui_file):
        super(HomeAll, self).__init__(stay_on_top=True, ui_file=ui_file)

    def open(self):
        super(HomeAll, self).open()

    def on_close_button_clicked(self):
        super(HomeAll, self).close()

    def on_homeall_abutton_clicked(self):
        super(HomeAll, self).close()
