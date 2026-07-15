from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "serv"
        self.INFO = "minimal risc-v softcore"
        self.DESCRIPTION = "minimal risc-v cpu for testing"
        self.KEYWORDS = "risc-v softcore cpu"
        self.ORIGIN = ""
        self.NEEDS = ["fpga"]
        self.VERILOGS = ["serv.v", "ram32.v", "ser_add.v", "ser_lt.v", "ser_shift.v", "serv_alu.v", "serv_bufreg.v", "serv_csr.v", "serv_ctrl.v", "serv_decode.v", "serv_mem_if.v", "serv_rf_if.v", "serv_rf_ram_if.v", "serv_rf_ram.v", "serv_rf_top.v", "serv_state.v", "serv_top.v", "shift_reg.v", "serv_params.vh"]
        self.SRCFILES = ["prog.S", "makehex.py", "link.ld", "prepare.sh"]
        self.PINDEFAULTS = {
            "gpio0": {
                "direction": "output",
                "invert": False,
                "pull": None,
            },
            "gpio1": {
                "direction": "output",
                "invert": False,
                "pull": None,
            },
            "gpio2": {
                "direction": "output",
                "invert": False,
                "pull": None,
            },
        }
