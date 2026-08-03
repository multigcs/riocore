import os

from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        uid = self.plugin_setup["uid"]
        self.NAME = "gowin_empu"
        self.INFO = "TangNano4K ARM core"
        self.DESCRIPTION = "Cortex M3 ARM core inside TangNano4K"
        self.EMPU_INFO = "EMPU: GPIO / APB2-Master1 / UART0"
        self.KEYWORDS = "arm hardcore cpu"
        self.ORIGIN = "https://github.com/grughuhler/tang_4k_getting_started/tree/main"
        self.NEEDS = ["fpga", "gowin_empu"]
        self.VERILOGS = ["gowin_empu_top.v"]
        self.SRCFILES = [
            f"src/Makefile:src_{uid}/Makefile",
            f"src/link_cmd.ld:src_{uid}/link_cmd.ld",
            f"src/startup.S:src_{uid}/startup.S",
            f"src/cont_startup.c:src_{uid}/cont_startup.c",
            f"src/gpio.c:src_{uid}/gpio.c",
            f"src/gpio.h:src_{uid}/gpio.h",
            f"src/main.c:src_{uid}/main.c",
            f"src/uart.c:src_{uid}/uart.c",
            f"src/uart.h:src_{uid}/uart.h",
            f"src/rio.c:src_{uid}/rio.c",
        ]
        self.VERILOGS_GEN = ["gowin_empu.v"]
        self.PLUGIN_CONFIGS = {"Source-Editor": "config.py"}
        self.SYSTIMER = True
        self.RESET = True
        self.cpu_type = "Cortex M3"
        self.OPTIONS = {}
        self.OPTIONS["uarts"] = {
            "type": int,
            "min": 0,
            "max": 1,
            "default": 0,
            "description": "number of uarts",
        }
        self.fpga_toolchain = None
        if not self.plugin_setup.get("gpios"):
            self.plugin_setup["gpios"] = {
                "led0": {
                    "name": "led0",
                }
            }
        self.uarts = self.plugin_setup.get("uarts", 0)
        self.gpios = self.plugin_setup.get("gpios", {})
        self.variables = self.plugin_setup.get("riovars", {})
        self.source = self.plugin_setup.get("source", "")
        # set pins
        self.PINDEFAULTS = {}
        for gpio in self.gpios:
            self.PINDEFAULTS[gpio.upper()] = {
                "direction": "inout",
                "optional": True,
            }
        for uart_n in range(self.uarts):
            self.PINDEFAULTS[f"uart{uart_n}_rx"] = {
                "direction": "input",
                "optional": True,
            }
            self.PINDEFAULTS[f"uart{uart_n}_tx"] = {
                "direction": "output",
                "optional": True,
            }
        # set interface/signals
        self.INTERFACE = {}
        self.SIGNALS = {}

        for name, data in self.variables.items():
            ctype = data.get("ctype", "uint32_t")
            bsize = 32
            if ctype == "bool":
                bsize = 1
            elif ctype.endswith("int8_t"):
                bsize = 8
            elif ctype.endswith("int16_t"):
                bsize = 16
            self.INTERFACE[name] = {
                "size": bsize,
                "direction": data.get("dir", "output"),
            }
            self.SIGNALS[name] = {
                "direction": data.get("dir", "output"),
            }
            if ctype == "bool":
                self.SIGNALS[name]["bool"] = True
            elif ctype == "uint8_t":
                self.SIGNALS[name]["min"] = 0
                self.SIGNALS[name]["max"] = 255
            elif ctype == "int8_t":
                self.SIGNALS[name]["min"] = -127
                self.SIGNALS[name]["max"] = 127

    def gateware_instances(self, gateware=None):
        uid = self.plugin_setup["uid"]
        addr = 0x40002400
        for iname, idata in self.variables.items():
            idata["addr"] = addr
            addr += 0x04
        self.systimer_addr = addr
        addr += 0x04
        if gateware:
            self.gateware = gateware
            self.fpga_toolchain = gateware.jdata["toolchain"]
            self.fpga_family = gateware.jdata.get("family")
            self.fpga_type = gateware.jdata.get("type")
            gateware.jdata["firmware_file"] = f"src_{uid}/prog.bin"

        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]

        # instance["module"] = "Gowin_EMPU_Top"
        instance_arguments = instance["arguments"]
        gpio_n = 0
        for gpio in self.gpios:
            if gpio.upper() in instance_arguments:
                var = instance_arguments[gpio.upper()]
                del instance_arguments[gpio.upper()]
                instance_arguments[f"gpio{gpio_n}"] = var
            gpio_n += 1
        for iname, idata in self.variables.items():
            if iname in instance_arguments:
                var = instance_arguments[iname]
                del instance_arguments[iname]
                instance_arguments[f"rio_{iname}"] = var
        if self.SYSTIMER:
            instance_arguments["systimer"] = "systimer"

        return instances

    @classmethod
    def extra_files(cls, parent, instances):
        for ins_n, instance in enumerate(instances):
            uid = instance.plugin_setup["uid"]
            instance.instance_num = ins_n
            os.makedirs(os.path.join(parent.gateware_path, f"src_{uid}"), exist_ok=True)

            open(os.path.join(parent.gateware_path, f"src_{uid}", "rio.h"), "w").write("\n".join(cls.rio_h(parent, instance)))
            open(os.path.join(parent.gateware_path, f"src_{uid}", "main.c"), "w").write(cls.main_c(parent, instance))
            open(os.path.join(parent.gateware_path, "gowin_empu.v"), "w").write("\n".join(cls.soc_v(parent, instance)))

            log = os.path.join(parent.gateware_path, f"src_{uid}", "compile.log")
            print(f"  INFO: {uid}: running compiler script: {log}")
            ret = os.system(f"cd {parent.gateware_path}/src_{uid} && make clean prog.bin > compile.log 2>&1")
            if ret != 0:
                print(f"  ERROR: {uid}: running compiler script")
                for line in open(log, "r").read().split("\n"):
                    print(f"    {line}")
                exit(1)

    @classmethod
    def main_c(cls, parent, instance):
        uid = instance.plugin_setup["uid"]
        main_c = ""
        if instance.source:
            if len(instance.source.split("\n")) == 1 and os.path.isfile(instance.source):
                print(f"  INFO: {uid}: using c-file {instance.source}")
                main_c = open(instance.source, "r").read()
            else:
                main_c = instance.source
        if parent.configuration_path:
            for main_name in (f"main_{uid}.c", f"main_{instance.NAME}.c"):
                if not main_c:
                    cpath = os.path.join(parent.project.config["json_path"], main_name)
                    if os.path.isfile(cpath):
                        print(f"  INFO: {uid}: using c-file {cpath}")
                        main_c = open(cpath, "r").read()
        if not main_c:
            main_c = open(os.path.join(os.path.dirname(__file__), "src", "main.c"), "r").read()
        return main_c

    @classmethod
    def rio_h(cls, parent, instance):
        uid = instance.plugin_setup["uid"]
        output = []
        output.append("#ifndef RIO_H")
        output.append("#define RIO_H")
        output.append("")
        output.append("#include <stdint.h>")
        output.append('#include "uart.h"')
        output.append('#include "gpio.h"')
        output.append("")
        output.append(f"#define F_CPU          {instance.gateware.jdata['speed']}")
        output.append(f'#define SYSNAME        "{uid}"')
        output.append("#define MEMBYTES       16384")
        output.append(f'#define CPU_TYPE       "{instance.cpu_type}"')
        if instance.fpga_toolchain:
            output.append(f'#define FPGA_TOOLCHAIN "{instance.fpga_toolchain}"')
        if instance.fpga_family:
            output.append(f'#define FPGA_FAMILY    "{instance.fpga_family}"')
        if instance.fpga_type:
            output.append(f'#define FPGA_TYPE      "{instance.fpga_type}"')
        output.append(f"#define INSTANCE_N     {instance.instance_num}")
        output.append("")
        output.append("extern void sysinit();")
        output.append("")

        # GPIOS
        if instance.gpios:
            output.append("#define INPUT  0")
            output.append("#define OUTPUT 1")
            output.append("#define LOW    0")
            output.append("#define HIGH   1")
            output.append("#define TOGGLE 2")
            gpio_n = 0
            for gpio in instance.gpios:
                output.append(f"#define GPIO_{gpio.upper()}  {gpio_n}")
                gpio_n += 1
            output.append("extern void pinMode(uint8_t num, uint8_t dir);")
            output.append("extern void digitalWrite(uint8_t num, uint8_t value);")
            output.append("extern uint8_t digitalRead(uint8_t num);")
            output.append("")

        # VARIABLES
        for iname, idata in instance.variables.items():
            ctype = idata.get("ctype", "uint32_t")
            output.append(f"#define RIO_{iname.upper():10s} (*((volatile {ctype} *) (0x{idata['addr']:x})))")
        output.append("")

        if instance.SYSTIMER:
            output.append(f"#define UTIMER ((volatile unsigned int *) 0x{instance.systimer_addr:x})")
            output.append("extern uint32_t mills(void);")
            output.append("")

        output.append("#endif")
        output.append("")
        return output

    @classmethod
    def soc_v(cls, parent, instance):
        output = []
        output.append("module gowin_empu (")
        output.append("    input wire clk,")
        for uart_n in range(instance.uarts):
            output.append(f"    input wire  uart{uart_n}_rx,")
            output.append(f"    output wire uart{uart_n}_tx,")
        gpio_n = 0
        for gpio in instance.gpios:
            output.append(f"    inout wire gpio{gpio_n},")
            gpio_n += 1
        for iname, idata in instance.variables.items():
            direction = {"input": "output", "output": "input"}.get(idata.get("dir", "output"))
            ctype = idata.get("ctype", "uint32_t")
            bsize = 32
            if ctype == "bool":
                bsize = 1
            elif ctype.endswith("int8_t"):
                bsize = 8
            elif ctype.endswith("int16_t"):
                bsize = 16
            ptype = "wire"
            if bsize > 1:
                output.append(f"    {direction} {ptype} [{bsize - 1}:0] rio_{iname},")
            else:
                output.append(f"    {direction} {ptype} rio_{iname},")
        if instance.SYSTIMER:
            output.append("    input wire [31:0] systimer,")
        output.append("    input wire resetn")
        output.append(");")
        output.append("")
        for gn in range(gpio_n, 16):
            output.append(f"    wire gpio{gn};")
        output.append("")

        output.append("    wire        pclk;")
        output.append("    wire        preset_n;")
        output.append("    wire        penable;")
        output.append("    wire [7:0]  paddr;")
        output.append("    wire        pwrite;")
        output.append("    wire [31:0] pwdata;")
        output.append("    wire [3:0]  pstrb;")
        output.append("    wire [2:0]  pprot;")
        output.append("    wire        psel1;")
        output.append("    wire [31:0] prdata1;")
        output.append("    wire        pready1;")
        # output.append("    wire        psel2;")
        # output.append("    wire [31:0] prdata2;")
        # output.append("    wire        pready2;")
        output.append("")

        output.append("    Gowin_EMPU_Top empu0 (")
        output.append("        .sys_clk(clk),")
        output.append("        .uart0_rxd(uart0_rx),")
        output.append("        .uart0_txd(uart0_tx),")
        output.append("        .gpio({gpio15, gpio14, gpio13, gpio12, gpio11, gpio10, gpio9, gpio8, gpio7, gpio6, gpio5, gpio4, gpio3, gpio2, gpio1, gpio0}),")
        output.append("        .master_pclk(pclk),")
        output.append("        .master_prst(preset_n),")
        output.append("        .master_penable(penable),")
        output.append("        .master_paddr(paddr),")
        output.append("        .master_pwrite(pwrite),")
        output.append("        .master_pwdata(pwdata),")
        output.append("        .master_pstrb(pstrb),")
        output.append("        .master_pprot(pprot),")
        output.append("        .master_psel1(psel1),")
        output.append("        .master_prdata1(prdata1),")
        output.append("        .master_pready1(pready1),")
        output.append("        .master_pslverr1(1'b0),")
        # output.append("        .master_psel2(psel2),")
        # output.append("        .master_prdata2(prdata2),")
        # output.append("        .master_pready2(pready2),")
        # output.append("        .master_pslverr2(1'b0),")
        output.append("        .reset_n(1'b1)")
        output.append("    );")
        output.append("")

        output.append("    rio_vars rio_vars0 (")
        output.append("        .pclk(pclk),")
        output.append("        .penable(penable),")
        output.append("        .paddr(paddr),")
        output.append("        .pwrite(pwrite),")
        output.append("        .pwdata(pwdata),")
        output.append("        .pstrb(pstrb),")
        output.append("        .pprot(pprot),")
        output.append("        .psel(psel1),")
        output.append("        .prdata(prdata1),")
        output.append("        .pready(pready1),")
        for iname, idata in instance.variables.items():
            output.append(f"        .rio_{iname}(rio_{iname}),")
        if instance.SYSTIMER:
            output.append("        .systimer(systimer),")
        output.append("        .preset_n(preset_n)")
        output.append("    );")
        output.append("endmodule")
        output.append("")

        output.append("module rio_vars (")
        output.append("    input wire        pclk,")
        output.append("    input wire        penable,")
        output.append("    input wire [7:0]  paddr,")
        output.append("    input wire        pwrite,")
        output.append("    input wire [31:0] pwdata,")
        output.append("    input wire [3:0]  pstrb,")
        output.append("    input wire [2:0]  pprot,")
        output.append("    input wire        psel,")
        output.append("    output reg [31:0] prdata,")
        output.append("    output reg        pready,")
        for iname, idata in instance.variables.items():
            direction = {"input": "output", "output": "input"}.get(idata.get("dir", "output"))
            ctype = idata.get("ctype", "uint32_t")
            bsize = 32
            if ctype == "bool":
                bsize = 1
            elif ctype.endswith("int8_t"):
                bsize = 8
            elif ctype.endswith("int16_t"):
                bsize = 16
            ptype = "wire"
            if direction == "output":
                ptype = "reg "
            if bsize > 1:
                output.append(f"    {direction} {ptype} [{bsize - 1}:0] rio_{iname},")
            else:
                output.append(f"    {direction} {ptype} rio_{iname},")
        if instance.SYSTIMER:
            output.append("    input wire [31:0] systimer,")
        output.append("    input wire        preset_n")
        output.append(");")
        output.append("")
        output.append("    wire [5:0] wordaddr = paddr[7:2];")
        output.append("")
        output.append("    always @(posedge pclk or negedge preset_n) begin")
        output.append("        if (!preset_n) begin")
        output.append("            pready <= 1'b0;")
        output.append("        end else begin")
        output.append("            if (psel & !penable) begin")
        output.append("                if (pwrite) begin")
        var_n = 0
        for iname, idata in instance.variables.items():
            ctype = idata.get("ctype", "uint32_t")
            bsize = 32
            if ctype == "bool":
                bsize = 1
            elif ctype.endswith("int8_t"):
                bsize = 8
            elif ctype.endswith("int16_t"):
                bsize = 16
            if idata.get("dir", "output") == "input":
                output.append(f"                    if (wordaddr == {var_n} && pstrb[0]) rio_{iname}[7:0] <= pwdata[7:0];")
                if bsize >= 16:
                    output.append(f"                    if (wordaddr == {var_n} && pstrb[1]) rio_{iname}[15:8] <= pwdata[15:8];")
                if bsize >= 24:
                    output.append(f"                    if (wordaddr == {var_n} && pstrb[2]) rio_{iname}[23:16] <= pwdata[23:16];")
                if bsize >= 32:
                    output.append(f"                    if (wordaddr == {var_n} && pstrb[3]) rio_{iname}[31:24] <= pwdata[31:24];")
            var_n += 1
        output.append("                end else begin")
        var_n = 0
        for iname, idata in instance.variables.items():
            output.append(f"                    if (wordaddr == {var_n}) prdata <= rio_{iname};")
            var_n += 1

        if instance.SYSTIMER:
            output.append(f"                    if (wordaddr == {var_n}) prdata <= systimer;")
            var_n += 1

        output.append("                end")
        output.append("                pready <= 1'b1;")
        output.append("            end else begin ")
        output.append("                pready <= 1'b0;")
        output.append("            end")
        output.append("        end")
        output.append("    end")
        output.append("endmodule")
        output.append("")

        return output
