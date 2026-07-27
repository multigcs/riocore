import os

from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        uid = self.plugin_setup["uid"]
        self.NAME = "serv"
        self.INFO = "minimal risc-v softcore"
        self.DESCRIPTION = "minimal risc-v cpu for testing"
        self.KEYWORDS = "risc-v softcore cpu"
        self.ORIGIN = "https://github.com/olofk/serv"
        self.NEEDS = ["fpga"]
        self.VERILOGS = ["ram32.v", "ser_add.v", "ser_lt.v", "ser_shift.v", "serv_alu.v", "serv_bufreg.v", "serv_csr.v", "serv_ctrl.v", "serv_decode.v", "serv_mem_if.v", "serv_rf_if.v", "serv_rf_ram_if.v", "serv_rf_ram.v", "serv_rf_top.v", "serv_state.v", "serv_top.v", "shift_reg.v"]
        self.SRCFILES = [
            "serv_params.vh",
            f"src/makehex.py:src_{uid}/makehex.py",
            f"src/link.ld:src_{uid}/link.ld",
            f"src/main.c:src_{uid}/main.c",
            f"src/rio.c:src_{uid}/rio.c",
        ]
        self.VERILOGS_GEN = [f"serv_{uid}.v"]
        self.PLUGIN_CONFIGS = {"Source-Editor": "config.py"}
        self.SYSTIMER = True
        self.cpu_type = "SERV"
        self.ofiles = "main.o rio.o"
        self.v_parameter_bool = {}
        self.RESET = True
        self.OPTIONS = {}
        for param, default in self.v_parameter_bool.items():
            self.OPTIONS[param] = {
                "type": bool,
                "default": default,
            }
        """
        self.OPTIONS["uarts"] = {
            "type": int,
            "min": 0,
            "max": 1,
            "default": 0,
            "description": "number of uarts",
        }
        self.OPTIONS["pwms"] = {
            "type": int,
            "min": 0,
            "max": 1,
            "default": 0,
            "description": "number of pwms",
        }
        """
        self.OPTIONS["ramsize"] = {
            "type": "select",
            "options": ["512", "768", "1024", "2048", "4096", "8192"],
            "default": "1024",
            "description": "size of ram in bytes",
        }
        self.fpga_toolchain = None
        self.ramsize = int(self.plugin_setup.get("ramsize", self.OPTIONS["ramsize"]["default"]))
        self.uarts = self.plugin_setup.get("uarts", 0)
        self.pwms = self.plugin_setup.get("pwms", 0)
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
        for pwm_n in range(self.pwms):
            self.PINDEFAULTS[f"pwm{pwm_n}"] = {
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

        if self.ramsize % 4:
            print("ERROR: ramsize must be multiple of 4")

        addr = 0x80000100
        for iname, idata in self.variables.items():
            idata["addr"] = addr
            addr += 0x04

        # uart baudrate scale (ice40 = 1 / tangnano = 12) ????
        self.uart_baud_scale = 1

    def gateware_instances(self, gateware=None):
        uid = self.plugin_setup["uid"]
        if gateware:
            self.gateware = gateware
            self.fpga_toolchain = gateware.jdata["toolchain"]
            self.fpga_family = gateware.jdata.get("family")
            self.fpga_type = gateware.jdata.get("type")
            if self.fpga_toolchain == "gowin":
                if self.fpga_family == "GW1N-9C":
                    self.uart_baud_scale = 12
                elif self.fpga_family == "GW5A-25A":
                    self.uart_baud_scale = 4
            else:
                self.uart_baud_scale = 1
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance["module"] = f"{self.NAME}_{uid}"
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
        instance_parameter = instance["parameter"]
        for param in self.v_parameter_bool:
            instance_parameter[param] = str(int(self.plugin_setup.get(param, self.OPTIONS[param]["default"])))
        return instances

    @classmethod
    def extra_files(cls, parent, instances):
        for instance in instances:
            uid = instance.plugin_setup["uid"]
            os.makedirs(os.path.join(parent.gateware_path, f"src_{uid}"), exist_ok=True)

            instance.mabi = "ilp32"
            instance.march = "rv32i"
            instance.gcc_options = ""

            open(os.path.join(parent.gateware_path, f"src_{uid}", "rio.h"), "w").write("\n".join(cls.rio_h(parent, instance)))
            open(os.path.join(parent.gateware_path, f"src_{uid}", "startup.s"), "w").write("\n".join(cls.startup_s(parent, instance)))
            open(os.path.join(parent.gateware_path, f"src_{uid}", "main.c"), "w").write(cls.main_c(parent, instance))
            open(os.path.join(parent.gateware_path, f"{instance.NAME}_{uid}.v"), "w").write("\n".join(cls.soc_v(parent, instance)))
            open(os.path.join(parent.gateware_path, f"src_{uid}", "compile.sh"), "w").write("\n".join(cls.compile_sh(parent, instance)))
            cls.compile_run(parent, instance)

    @classmethod
    def startup_s(cls, parent, instance):
        startup = []
        startup.append("")
        startup.append(".text")
        startup.append(".global _start")
        startup.append("_start:")
        startup.append(f"	li x2, {instance.ramsize}")
        startup.append("	call main")
        startup.append("")
        return startup

    @classmethod
    def rio_h(cls, parent, instance):
        uid = instance.plugin_setup["uid"]
        output = []
        output.append("#ifndef RIO_H")
        output.append("#define RIO_H")
        output.append("")
        output.append("#include <stdint.h>")
        output.append("")
        # output.append(f"#define F_CPU          {instance.gateware.jdata['speed']}")
        output.append(f'#define SYSNAME        "{uid}"')
        output.append(f"#define MEMBYTES       {instance.ramsize}")
        output.append(f'#define CPU_TYPE       "{instance.cpu_type}"')
        output.append(f'#define CPU_MABI       "{instance.mabi}"')
        output.append(f'#define CPU_MARCH      "{instance.march}"')
        if instance.fpga_toolchain:
            output.append(f'#define FPGA_TOOLCHAIN "{instance.fpga_toolchain}"')
        if instance.fpga_family:
            output.append(f'#define FPGA_FAMILY    "{instance.fpga_family}"')
        if instance.fpga_type:
            output.append(f'#define FPGA_TYPE      "{instance.fpga_type}"')
        output.append("")
        for param in instance.v_parameter_bool:
            if instance.plugin_setup.get(param, instance.OPTIONS[param]["default"]):
                output.append(f"#define {param}")
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
            output.append("#define GPIOS ((volatile unsigned int *) 0x80000000)")
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
            output.append(f"#define RIO_{iname.upper():10s} *((volatile {ctype} *) 0x{idata['addr']:x})")
        output.append("")

        # SYSTIMER
        output.append("#define UTIMER ((volatile unsigned int *) 0x80000020)")
        output.append("extern uint32_t mills(void);")
        output.append("extern void delay_nop(uint32_t delay);")
        output.append("")

        # PWMS
        if instance.pwms:
            output.append("#ifdef ENABLE_MUL")
            output.append("#ifdef ENABLE_DIV")
            pbase = 0x80000030
            output.append(f"#define PWM_BASE ((volatile unsigned int *) 0x{pbase:x})")
            output.append(f"#define PWM_MAX  {instance.pwms}")
            for pwms_n in range(instance.pwms):
                output.append(f"#define PWM{pwms_n}_PULSE ((volatile unsigned int *) 0x{pbase:x})")
                output.append(f"#define PWM{pwms_n}_TOTAL ((volatile unsigned int *) 0x{pbase + 4:x})")
                pbase += 8
            output.append("#endif")
            output.append("#endif")
            output.append("")
            output.append("void pwm_set_total(unsigned int pwm, unsigned int total);")
            output.append("void pwm_set_pulse(unsigned int pwm, unsigned int pulse);")
            output.append("")

        # UARTS
        if instance.uarts:
            for baud in (1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600, 1000000, 2500000):
                output.append(f"#define UART_B{baud!s:7s} {instance.gateware.jdata['speed'] * instance.uart_baud_scale // baud}")
            ubase = 0x80000018
            for uart_n in range(instance.uarts):
                output.append(f"#define UART{uart_n}_DIV  ((volatile unsigned int *) 0x{ubase:x})")
                output.append(f"#define UART{uart_n}_DATA ((volatile unsigned int *) 0x{ubase + 4:x})")
                ubase += 0x10
            output.append("")
            output.append("#ifdef ENABLE_MUL")
            output.append("#ifdef ENABLE_DIV")
            output.append("extern void uart_set_baud(unsigned int uart, unsigned int baud);")
            output.append("#endif")
            output.append("#endif")
            output.append("extern void uart_set_div(unsigned int uart, unsigned int div);")
            output.append("extern void uart_print_hex(unsigned int uart, unsigned int val);")
            output.append("extern void uart_print_dec(unsigned int uart, unsigned int val);")
            output.append("extern char uart_getchar(unsigned int uart);")
            output.append("extern char uart_available(unsigned int uart);")
            output.append("extern void uart_putc(unsigned int uart, char ch);")
            output.append("extern void uart_puts(unsigned int uart, char *s);")
            output.append("")

        # SPIs
        """
        output.append("#ifdef GPIO_SPI0_SCLK")
        output.append("extern unsigned char spi0_transfer_byte(unsigned char send_val);")
        output.append("#endif")
        output.append("")
        """

        output.append("#endif")
        output.append("")
        return output

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
            if not main_c:
                cpath = os.path.join(parent.project.config["json_path"], "main.c")
                if os.path.isfile(cpath):
                    print(f"  INFO: {uid}: using c-file {cpath}")
                    main_c = open(cpath, "r").read()
            if not main_c:
                cpath = os.path.join(parent.project.config["json_path"], f"{uid}.c")
                if os.path.isfile(cpath):
                    print(f"  INFO: {uid}: using c-file {cpath}")
                    main_c = open(cpath, "r").read()
        if not main_c:
            main_c = open(os.path.join(os.path.dirname(__file__), "src", "main.c"), "r").read()
        return main_c

    @classmethod
    def compile_sh(cls, parent, instance):
        output = []
        output.append(f"""#!/bin/sh
#
# https://github.com/xpack-dev-tools/riscv-none-elf-gcc-xpack/releases/tag/v15.2.0-1
#
set -x
set -e

WORKING_DIR=`dirname "$0"`
cd $WORKING_DIR

# RISCV_BIN="riscv64-unknown-elf"
RISCV_BIN="riscv-none-elf"
FPGA_TOOLCHAIN="{instance.fpga_toolchain}"
FLAGS="-nostartfiles -nostdlib -static -Os"
FILES="{instance.ofiles}"

# clean
rm -f $FILES prog.elf prog.bin prog.hex

# build
for O_FILE in $FILES
do
    C_FILE=`echo $O_FILE | sed "s|o$|c|g"`
    $RISCV_BIN-gcc -mno-save-restore -march={instance.march} -mabi={instance.mabi} {instance.gcc_options} $FLAGS -c $C_FILE -I.
done
$RISCV_BIN-gcc -mno-save-restore -march={instance.march} -mabi={instance.mabi} {instance.gcc_options} $FLAGS -Tlink.ld -o prog.elf startup.s $FILES
$RISCV_BIN-strip prog.elf
$RISCV_BIN-objcopy prog.elf -O binary prog.bin
$RISCV_BIN-size -G -d prog.elf

# convert
python3 makehex.py prog.bin {instance.ramsize // 4} > prog.hex

""")
        return output

    @classmethod
    def compile_run(cls, parent, instance):
        uid = instance.plugin_setup["uid"]
        log = os.path.join(parent.gateware_path, f"src_{uid}", "compile.log")
        print(f"  INFO: {uid}: running compiler script: {log}")
        ret = os.system(f"cd {parent.gateware_path}/src_{uid} ; bash compile.sh > compile.log 2>&1")
        if ret != 0:
            print(f"  ERROR: {uid}: running compiler script")
            for line in open(log, "r").read().split("\n"):
                print(f"    {line}")
            exit(1)

    @classmethod
    def soc_v(cls, parent, instance):
        uid = instance.plugin_setup["uid"]
        output = []
        output.append(f"module serv_{uid} (")
        output.append("    input wire clk,")
        output.append("    input wire resetn,")
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
            if direction == "output":
                ptype = "reg "
            if bsize > 1:
                output.append(f"    {direction} {ptype} [{bsize - 1}:0] rio_{iname},")
            else:
                output.append(f"    {direction} {ptype} rio_{iname},")

        output.append("    input wire [31:0] systimer")
        output.append(");")
        output.append(f"    parameter RAM_SIZE = {instance.ramsize};")
        output.append(f'    parameter INITIAL_FILE = "src_{uid}/prog.hex";')
        output.append("")

        for gn in range(gpio_n, 16):
            output.append(f"    wire gpio{gn};")

        output += cls.soc_v_top(parent, instance)
        output += cls.soc_v_mem(parent, instance)

        bus_outs = []
        output.append("    // GPIOs")
        if instance.fpga_toolchain == "icestorm":
            print("  ------------------------------------------------")
            print("  WARNING: disable GPIO inputs (bug in icestorm ?)")
            print("  ------------------------------------------------")
            output.append("    reg [15:0] gdir = 16'hFFFF;")
        else:
            output.append("    reg [15:0] gdir = 16'd0;")
        output.append("    reg [15:0] gout = 'd0;")
        for n in range(16):
            output.append(f"    assign gpio{n} = gdir[{n}] ? gout[{n}] : 1'bz;")
        output.append("    wire gpio_sel = (o_dbus_adr == 'h80000000);")
        output.append("    wire [31:0] gpio_out = {gdir, gpio15, gpio14, gpio13, gpio12, gpio11, gpio10, gpio9, gpio8, gpio7, gpio6, gpio5, gpio4, gpio3, gpio2, gpio1, gpio0};")
        output.append("    always @(posedge clk) begin")
        output.append("        if (o_dbus_cyc && o_dbus_we && gpio_sel) begin")
        output.append("            gout <= o_dbus_dat[15:0];")
        if instance.fpga_toolchain != "icestorm":
            output.append("            gdir <= o_dbus_dat[31:16];")
        output.append("        end")
        output.append("    end")
        output.append("")
        bus_outs.append("gpio")

        output.append("    // System-Timer")
        output.append("    wire utimer_sel = (o_dbus_adr == 'h80000020);")
        output.append("    wire [31:0] utimer_out = systimer;")
        output.append("")
        bus_outs.append("utimer")

        for name, data in instance.variables.items():
            direction = data.get("dir", "output")
            ctype = data.get("ctype", "uint32_t")
            bsize = 32
            if ctype == "bool":
                bsize = 1
            elif ctype.endswith("int8_t"):
                bsize = 8
            elif ctype.endswith("int16_t"):
                bsize = 16

            output.append(f"    // RIO-Variable: {name}")
            output.append(f"    wire rio_{name}_sel = (o_dbus_adr == 'h{data['addr']:x});")
            output.append(f"    wire [31:0] rio_{name}_out = rio_{name};")
            if direction == "input":
                output.append("    always @(posedge clk) begin")
                output.append(f"        if (o_dbus_cyc && o_dbus_we && rio_{name}_sel) begin")
                output.append(f"            rio_{name} <= o_dbus_dat;")
                output.append("        end")
                output.append("    end")
            output.append("")
            bus_outs.append(f"rio_{name}")

        output.append("    assign i_dbus_rdt = ")
        for out in bus_outs:
            sel = f"{out}_sel"
            output.append(f"        {sel:16s} ? {out}_out :")
        output.append("        32'h0;")

        output.append("endmodule")
        output.append("")
        return output

    @classmethod
    def soc_v_top(cls, parent, instance):
        output = []
        output.append("""
    wire i_rst;
    wire i_timer_irq;
    wire [31:0] o_ibus_adr;
    wire o_ibus_cyc;
    wire [31:0] i_ibus_rdt;
    reg i_ibus_ack;
    wire [31:0] o_dbus_adr;
    wire [31:0] o_dbus_dat;
    wire [3:0] o_dbus_sel;
    wire o_dbus_we;
    wire o_dbus_cyc;
    wire [31:0] i_dbus_rdt;
    reg i_dbus_ack;
    wire o_rf_rreq;
    wire o_rf_wreq;
    wire i_rf_ready;
    wire [5:0] o_wreg0;
    wire [5:0] o_wreg1;
    wire o_wen0;
    wire o_wen1;
    wire o_wdata0;
    wire o_wdata1;
    wire [5:0] o_rreg0;
    wire [5:0] o_rreg1;
    wire i_rdata0;
    wire i_rdata1;

    serv_top serv_top_inst(
        .clk(clk),
        .i_rst(i_rst),
        .i_timer_irq(i_timer_irq),
        .o_ibus_adr(o_ibus_adr),
        .o_ibus_cyc(o_ibus_cyc),
        .i_ibus_rdt(i_ibus_rdt),
        .i_ibus_ack(i_ibus_ack),
        .o_dbus_adr(o_dbus_adr),
        .o_dbus_dat(o_dbus_dat),
        .o_dbus_sel(o_dbus_sel),
        .o_dbus_we(o_dbus_we),
        .o_dbus_cyc(o_dbus_cyc),
        .i_dbus_rdt(i_dbus_rdt),
        .i_dbus_ack(i_dbus_ack),
        .o_rf_rreq(o_rf_rreq),
        .o_rf_wreq(o_rf_wreq),
        .i_rf_ready(i_rf_ready),
        .o_wreg0(o_wreg0),
        .o_wreg1(o_wreg1),
        .o_wen0(o_wen0),
        .o_wen1(o_wen1),
        .o_wdata0(o_wdata0),
        .o_wdata1(o_wdata1),
        .o_rreg0(o_rreg0),
        .o_rreg1(o_rreg1),
        .i_rdata0(i_rdata0),
        .i_rdata1(i_rdata1)
    );
""")
        return output

    @classmethod
    def soc_v_mem(cls, parent, instance):
        output = []
        output.append("""
    assign i_rst = !resetn;
    assign i_timer_irq = 0;
    wire [7:0] rf_waddr;
    wire rf_wen;
    wire [7:0] rf_wdata;
    wire [7:0] rf_raddr;
    reg [7:0] rf_rdata;

    serv_rf_ram_if rf_ram_if(
        .i_clk(clk),
        .i_rst(!resetn),
        .i_wreq(o_rf_wreq),
        .i_rreq(o_rf_rreq),
        .o_ready(i_rf_ready),
        .i_wreg0(o_wreg0),
        .i_wreg1(o_wreg1),
        .i_wen0(o_wen0),
        .i_wen1(o_wen1),
        .i_wdata0(o_wdata0),
        .i_wdata1(o_wdata1),
        .i_rreg0(o_rreg0),
        .i_rreg1(o_rreg1),
        .o_rdata0(i_rdata0),
        .o_rdata1(i_rdata1),
        .o_waddr(rf_waddr),
        .o_wen(rf_wen),
        .o_wdata(rf_wdata),
        .o_raddr(rf_raddr),
        .i_rdata(rf_rdata)
    );

    reg [7:0] rf_mem [0:255];
    always @(posedge clk) begin
        if (rf_wen) begin
            rf_mem[rf_waddr] <= rf_wdata;
        end
        rf_rdata <= rf_mem[rf_raddr];
    end

    ram32 #(
        .INITIAL_FILE(INITIAL_FILE),
        .RAM_SIZE(RAM_SIZE)
    ) iram(
        .clk(clk),
        .resetn(resetn),
        .addr(o_ibus_adr[9:2]),
        .ce(o_ibus_cyc),
        .we(0),
        .data_in(0),
        .data_out(i_ibus_rdt)
    );

    always @(posedge clk) begin
        i_ibus_ack <= (!resetn ? 0 : o_ibus_cyc && !i_ibus_ack);
    end

    always @(posedge clk) begin
        i_dbus_ack <= (!resetn ? 0 : o_dbus_cyc && !i_dbus_ack);
    end
""")
        return output
