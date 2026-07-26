import os

from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        uid = self.plugin_setup["uid"]
        self.NAME = "prv32"
        self.INFO = "picorv32 based risc-v softcore"
        self.DESCRIPTION = "picorv32 risc-v cpu for testing\ni using this riscv-toolchain: https://github.com/xpack-dev-tools/riscv-none-elf-gcc-xpack/releases/tag/v15.2.0-1"
        self.KEYWORDS = "risc-v softcore cpu"
        self.ORIGIN = "https://github.com/YosysHQ/picorv32"
        self.NEEDS = ["fpga"]
        self.VERILOGS = ["prv32_timer.v", "prv32_reset.v", "prv32_gpio.v", "prv32_rio.v", "prv32_uart_wrap.v", "prv32_simpleuart.v", "picorv32.v"]
        self.SRCFILES = [
            f"src/makehex.py:src_{uid}/makehex.py",
            f"src/link.ld:src_{uid}/link.ld",
            f"src/main.c:src_{uid}/main.c",
            f"src/rio.c:src_{uid}/rio.c",
            f"src/uart.c:src_{uid}/uart.c",
            f"src/pwm.c:src_{uid}/pwm.c",
            f"src/spi.c:src_{uid}/spi.c",
            f"src/conv_to_init.c:src_{uid}/conv_to_init.c",
            f"src/timer.c:src_{uid}/timer.c",
        ]
        self.VERILOGS_GEN = [f"prv32_sram_{uid}.v", f"prv32_{uid}.v"]
        self.PLUGIN_CONFIGS = {"Source-Editor": "config.py"}
        self.SYSTIMER = True
        # self.RESET = True
        self.cpu_type = "PicoRV32"
        self.ofiles = "main.o rio.o timer.o uart.o pwm.o spi.o"
        self.v_parameter_bool = {"BARREL_SHIFTER": False, "ENABLE_MUL": True, "ENABLE_DIV": True, "ENABLE_FAST_MUL": False, "ENABLE_COMPRESSED": False, "ENABLE_IRQ_QREGS": False}
        self.OPTIONS = {}
        for param, default in self.v_parameter_bool.items():
            self.OPTIONS[param] = {
                "type": bool,
                "default": default,
            }
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
                self.VERILOGS.append("prv32_mem_gowin.v")
                self.SRCFILES.append(f"src/sram_gowin.v:src_{uid}/sram_gowin.v")
            else:
                self.uart_baud_scale = 1
                self.SRCFILES.append(f"src/sram_bram.v:src_{uid}/sram_bram.v")
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
            if instance.fpga_toolchain == "gowin" and instance.ramsize != 8192:
                instance.ramsize = 8192
                print(f"  INFO: set ram size to {instance.ramsize} (gowin)")

            instance.mabi = "ilp32"
            instance.march = "rv32i"
            instance.gcc_options = ""
            if instance.plugin_setup.get("ENABLE_MUL", instance.OPTIONS["ENABLE_MUL"]["default"]) and instance.plugin_setup.get("ENABLE_DIV", instance.OPTIONS["ENABLE_DIV"]["default"]):
                instance.march += "m"
            if instance.plugin_setup.get("ENABLE_COMPRESSED", instance.OPTIONS["ENABLE_COMPRESSED"]["default"]):
                instance.march += "c"
            instance.march += "2p0"

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
        output.append(f"#define F_CPU          {instance.gateware.jdata['speed']}")
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

        # CDT_COUNTER
        output.append("#define CDT_COUNTER ((volatile unsigned int *) 0x80000010)")
        output.append("#define CDT_COUNTER_H0 ((volatile unsigned short *) 0x80000010)")
        output.append("#define CDT_COUNTER_H2 ((volatile unsigned short *) 0x80000012)")
        output.append("#define CDT_COUNTER_B0 ((volatile unsigned char *) 0x80000010)")
        output.append("#define CDT_COUNTER_B1 ((volatile unsigned char *) 0x80000011)")
        output.append("#define CDT_COUNTER_B2 ((volatile unsigned char *) 0x80000012)")
        output.append("#define CDT_COUNTER_B3 ((volatile unsigned char *) 0x80000013)")
        output.append("extern void cdt_wbyte0(const unsigned char value);")
        output.append("extern void cdt_wbyte1(const unsigned char value);")
        output.append("extern void cdt_wbyte2(const unsigned char value);")
        output.append("extern void cdt_wbyte3(const unsigned char value);")
        output.append("extern void cdt_whalf0(const unsigned short value);")
        output.append("extern void cdt_whalf2(const unsigned short value);")
        output.append("extern void cdt_write(const unsigned int value);")
        output.append("extern unsigned int cdt_read(void);")
        output.append("extern void cdt_delay(const unsigned int value);")
        output.append("extern void delay(const unsigned int value);")
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
            main_c = open(os.path.join(os.path.dirname(__file__), f"src_{uid}", "main.c"), "r").read()
        return main_c

    @classmethod
    def compile_sh(cls, parent, instance):
        uid = instance.plugin_setup["uid"]
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
rm -f $FILES prog.elf prog.bin prog.hex ../mem_init_{uid}.v

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

if test "$FPGA_TOOLCHAIN" = "gowin"
then
    gcc -o conv_to_init conv_to_init.c
    ./conv_to_init prog.bin > ../mem_init_{uid}.v
    sed "s|include .*|include \\"mem_init_{uid}.v\\"|g" sram_gowin.v | sed "s|module prv32_sram|module prv32_sram_{uid}|g" > ../prv32_sram_{uid}.v
else
    sed "s|src/prog.hex|src_{uid}/prog.hex|g" sram_bram.v | sed "s|module prv32_sram|module prv32_sram_{uid}|g" > ../prv32_sram_{uid}.v
fi

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
        output.append(f"module prv32_{uid} (")
        output.append("    input wire clk,")
        # output.append("    input wire resetn,")
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
        output.append("")
        output.append("    parameter [0:0] BARREL_SHIFTER = 0;")
        output.append("    parameter [0:0] ENABLE_MUL = 0;")
        output.append("    parameter [0:0] ENABLE_DIV = 0;")
        output.append("    parameter [0:0] ENABLE_FAST_MUL = 0;")
        output.append("    parameter [0:0] ENABLE_COMPRESSED = 0;")
        output.append("    parameter [0:0] ENABLE_IRQ_QREGS = 0;")
        output.append(f"    parameter MEMBYTES = {instance.ramsize};")
        output.append(f"    parameter ADDRWIDTH = {instance.clog2(instance.ramsize)};")
        output.append(f"    parameter UART_DIV = {instance.gateware.jdata['speed'] * instance.uart_baud_scale // 115200};")
        output.append("""
    parameter [31:0] STACKADDR = (MEMBYTES);
    parameter [31:0] PROGADDR_RESET = 32'h0000_0000;
    parameter [31:0] PROGADDR_IRQ = 32'h0000_0000;

	reg reset_button_n = 0;
	reg [15:0] counter = 10000;
	always @(posedge clk) begin
		if (counter == 0) begin
			reset_button_n <= 1;
		end else begin
			counter <= counter - 1;
        end
    end

    wire                       reset_n;
    wire [31:0]                mem_addr;
    wire [31:0]                mem_wdata;
    wire [31:0]                mem_rdata;
    wire [3:0]                 mem_wstrb;
    wire                       mem_ready;
    wire                       mem_inst;

    wire                       sram_sel;
    wire                       sram_ready;
    wire [31:0]                sram_data_o;

    wire                       cdt_sel;
    wire                       cdt_ready;
    wire [31:0]                cdt_data_o;

    wire                       utimer_sel;
    wire                       utimer_ready;
    wire [31:0]                utimer_data_o;

    wire                       gpios_sel;
    wire                       gpios_ready;
    wire [31:0]                gpios_data_o;
""")

        for uart_n in range(instance.uarts):
            output.append(f"    wire                       uart{uart_n}_sel;")
            output.append(f"    wire                       uart{uart_n}_ready;")
            output.append(f"    wire [31:0]                uart{uart_n}_data_o;")
            output.append("")

        for pwm_n in range(instance.pwms):
            output.append(f"    wire                       pwm{pwm_n}_sel;")
            output.append(f"    wire                       pwm{pwm_n}_ready;")
            output.append(f"    wire [31:0]                pwm{pwm_n}_data_o;")
            output.append("")

        for iname, idata in instance.variables.items():
            output.append(f"    wire                       rio_{iname}_sel;")
            output.append(f"    wire                       rio_{iname}_ready;")
            output.append(f"    wire [31:0]                rio_{iname}_data_o;")
            output.append("")

        output.append("    assign sram_sel         = mem_valid && (mem_addr < 32'h00002000);")
        output.append("    assign gpios_sel        = mem_valid && (mem_addr == 32'h80000000);")
        output.append("    assign cdt_sel          = mem_valid && (mem_addr == 32'h80000010);")
        output.append("    assign utimer_sel       = mem_valid && (mem_addr == 32'h80000020);")

        ubase = 0x80000018
        for uart_n in range(instance.uarts):
            output.append(f"    assign uart{uart_n}_sel        = mem_valid && ((mem_addr & 32'hffffff{ubase & 0xFF:x}) == 32'h{ubase:x});")
            ubase += 0x10

        pbase = 0x80000030
        for pwm_n in range(instance.pwms):
            sel = f"pwm{pwm_n}_sel"
            output.append(f"    assign {sel:16s} = mem_valid && (mem_addr == 32'h{pbase:x} || mem_addr == 32'h{pbase + 4:x});")
            pbase += 8
        for iname, idata in instance.variables.items():
            sel = f"rio_{iname}_sel"
            output.append(f"    assign {sel:16s} = mem_valid && (mem_addr == 32'h{idata['addr']:x});")
        output.append("")

        output.append("    // Core can proceed regardless of *which* slave was targetted and is now ready.")
        output.append("    assign mem_ready = mem_valid & (")
        output.append("        sram_ready |")
        output.append("        gpios_ready |")
        output.append("        cdt_ready |")
        output.append("        utimer_ready |")
        for uart_n in range(instance.uarts):
            output.append(f"        uart{uart_n}_ready |")
        for pwm_n in range(instance.pwms):
            output.append(f"        pwm{pwm_n}_ready |")
        for iname, idata in instance.variables.items():
            output.append(f"        rio_{iname}_ready |")
        output.append("        0);")
        output.append("")

        output.append("    // Select which slave's output data is to be fed to core.")
        output.append("    assign mem_rdata = ")
        output.append("        sram_sel         ? sram_data_o :")
        output.append("        gpios_sel        ? gpios_data_o :")
        output.append("        cdt_sel          ? cdt_data_o  :")
        output.append("        utimer_sel       ? utimer_data_o :")
        for uart_n in range(instance.uarts):
            output.append(f"        uart{uart_n}_sel        ? uart{uart_n}_data_o :")
        for pwm_n in range(instance.pwms):
            sel = f"pwm{pwm_n}_sel"
            output.append(f"        {sel:16s} ? pwm{pwm_n}_data_o  :")
        for iname, idata in instance.variables.items():
            sel = f"rio_{iname}_sel"
            output.append(f"        {sel:16s} ? rio_{iname}_data_o  :")
        output.append("        32'h0;")
        output.append("")

        output.append("    prv32_reset_control reset_controller (")
        output.append("        .clk(clk),")
        output.append("        .reset_button_n(reset_button_n),")
        output.append("        .reset_n(reset_n)")
        output.append("    );")
        output.append("")

        output.append("    prv32_timer cdt (")
        output.append("        .clk(clk),")
        output.append("        .reset_n(reset_n),")
        output.append("        .cdt_sel(cdt_sel),")
        output.append("        .cdt_data_i(mem_wdata),")
        output.append("        .we(mem_wstrb),")
        output.append("        .cdt_ready(cdt_ready),")
        output.append("        .cdt_data_o(cdt_data_o)")
        output.append("    );")
        output.append("")

        output.append(f"    prv32_sram_{uid} #(.ADDRWIDTH(ADDRWIDTH), .MEMBYTES(MEMBYTES)) memory (")
        output.append("        .clk(clk),")
        output.append("        .resetn(reset_n),")
        output.append("        .sram_sel(sram_sel),")
        output.append("        .wstrb(mem_wstrb),")
        output.append("        .addr(mem_addr[ADDRWIDTH-1:0]),")
        output.append("        .sram_data_i(mem_wdata),")
        output.append("        .sram_ready(sram_ready),")
        output.append("        .sram_data_o(sram_data_o)")
        output.append("    );")
        output.append("")

        for uart_n in range(instance.uarts):
            output.append(f"    prv32_uart_wrap #(.DEFAULT_DIV(UART_DIV)) uart{uart_n} (")
            output.append("        .clk(clk),")
            output.append("        .reset_n(reset_n),")
            output.append(f"        .uart_tx(uart{uart_n}_tx),")
            output.append(f"        .uart_rx(uart{uart_n}_rx),")
            output.append(f"        .uart_sel(uart{uart_n}_sel),")
            output.append("        .addr(mem_addr[3:0]),")
            output.append("        .uart_wstrb(mem_wstrb),")
            output.append("        .uart_di(mem_wdata),")
            output.append(f"        .uart_do(uart{uart_n}_data_o),")
            output.append(f"        .uart_ready(uart{uart_n}_ready)")
            output.append("    );")
            output.append("")

        gpio_n = 0
        gpio_pins = []
        for pname, pdata in instance.PINDEFAULTS.items():
            if pdata["direction"] == "inout":
                gpio_pins.append(f".gpio{gpio_n}(gpio{gpio_n})")
                gpio_n += 1
        if gpio_pins:
            output.append("    prv32_gpio soc_gpios (")
            output.append("        .clk(clk),")
            output.append("        .reset_n(reset_n),")
            output.append("        .gpios_sel(gpios_sel),")
            output.append("        .gpios_data_i(mem_wdata),")
            output.append("        .we(mem_wstrb[0]),")
            output.append("        .gpios_ready(gpios_ready),")
            output.append("        .gpios_data_o(gpios_data_o),")
            output.append("        " + ",\n        ".join(gpio_pins))
            output.append("    );")
            output.append("")

        for iname, idata in instance.variables.items():
            direction = {"output": "out", "input": "in"}.get(idata.get("dir", "output"))
            output.append(f"    prv32_rio_v{direction} soc_val_rio_{iname} (")
            output.append("        .clk(clk),")
            output.append("        .reset_n(reset_n),")
            output.append(f"        .v{direction}_sel(rio_{iname}_sel),")
            output.append(f"        .v{direction}_data_i(mem_wdata),")
            output.append("        .we(mem_wstrb[0]),")
            output.append(f"        .v{direction}_ready(rio_{iname}_ready),")
            output.append(f"        .v{direction}_data_o(rio_{iname}_data_o),")
            output.append(f"        .v{direction}(rio_{iname})")
            output.append("    );")
            output.append("")

        pbase = 0x80000030
        for pwm_n in range(instance.pwms):
            output.append(f"    prv32_pwm soc_pwm{pwm_n} (")
            output.append("        .clk(clk),")
            output.append("        .reset_n(reset_n),")
            output.append(f"        .pwm_addr(mem_addr - 32'h{pbase:x}),")
            output.append(f"        .pwm_sel(pwm{pwm_n}_sel),")
            output.append("        .pwm_data_i(mem_wdata),")
            output.append("        .we(mem_wstrb[0]),")
            output.append(f"        .pwm_ready(pwm{pwm_n}_ready),")
            output.append(f"        .pwm_data_o(pwm{pwm_n}_data_o),")
            output.append(f"        .pwm(pwm{pwm_n})")
            output.append("    );")
            output.append("")
            pbase += 8

        output.append("    prv32_utimer soc_utimer (")
        output.append("        .clk(clk),")
        output.append("        .reset_n(reset_n),")
        output.append("        .utimer_sel(utimer_sel),")
        output.append("        .utimer_data_i(mem_wdata),")
        output.append("        .we(mem_wstrb[0]),")
        output.append("        .utimer_ready(utimer_ready),")
        output.append("        .utimer_data_o(utimer_data_o),")
        output.append("        .systimer(systimer)")
        output.append("    );")
        output.append("")

        output.append("""
    picorv32 #(
        .STACKADDR(STACKADDR),
        .PROGADDR_RESET(PROGADDR_RESET),
        .PROGADDR_IRQ(PROGADDR_IRQ),
        .BARREL_SHIFTER(BARREL_SHIFTER),
        .COMPRESSED_ISA(ENABLE_COMPRESSED),
        .ENABLE_MUL(ENABLE_MUL),
        .ENABLE_DIV(ENABLE_DIV),
        .ENABLE_FAST_MUL(ENABLE_FAST_MUL),
        .ENABLE_IRQ(1),
        .ENABLE_IRQ_QREGS(ENABLE_IRQ_QREGS)
    ) cpu (
        .clk         (clk),
        .resetn      (reset_n),
        .mem_valid   (mem_valid),
        .mem_instr   (mem_instr),
        .mem_ready   (mem_ready),
        .mem_addr    (mem_addr),
        .mem_wdata   (mem_wdata),
        .mem_wstrb   (mem_wstrb),
        .mem_rdata   (mem_rdata),
        .irq         ('b0),
        .pcpi_wr     ('b0),
        .pcpi_rd     ('b0),
        .pcpi_wait   ('b0),
        .pcpi_ready  ('b0)
    );

endmodule

""")
        return output
