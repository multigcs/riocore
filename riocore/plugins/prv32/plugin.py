import os

from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "prv32"
        self.INFO = "picorv32 based risc-v softcore"
        self.DESCRIPTION = "picorv32 risc-v cpu for testing\ni using this riscv-toolchain: https://github.com/xpack-dev-tools/riscv-none-elf-gcc-xpack/releases/tag/v15.2.0-1"
        self.KEYWORDS = "risc-v softcore cpu"
        self.ORIGIN = ""
        self.NEEDS = ["fpga"]
        self.VERILOGS = ["prv32_timer.v", "prv32_reset.v", "prv32_gpio.v", "prv32_rio.v", "prv32_uart_wrap.v", "prv32_simpleuart.v", "picorv32.v"]
        self.SRCFILES = ["src/link_cmd.ld", "src/main.c", "src/uart.c", "src/spi.c", "src/conv_to_init.c", "src/timer.c", "src/makehex.py"]
        self.PLUGIN_CONFIGS = {"Source-Editor": "config.py"}
        self.OPTIONS = {
            "ENABLE_MUL": {
                "type": bool,
                "default": True,
            },
            "ENABLE_DIV": {
                "type": bool,
                "default": True,
            },
            "ENABLE_COMPRESSED": {
                "type": bool,
                "default": False,
            },
            "ramsize": {
                "type": int,
                "min": 512,
                "max": 8192,
                "default": 8192,
                "description": "size of ram in byte",
            },
        }
        self.fpga_toolchain = None
        self.ramsize = self.plugin_setup.get("ramsize", self.OPTIONS["ramsize"]["default"])
        self.uarts = self.plugin_setup.get("uarts", 0)
        self.gpios = self.plugin_setup.get("gpios", {})
        self.variables = self.plugin_setup.get("riovars", {})
        self.source = self.plugin_setup.get("source", open(os.path.join(os.path.dirname(__file__), "src", "main.c"), "r").read())
        for uart_n in range(self.uarts):
            self.PINDEFAULTS = {
                f"uart{uart_n}_rx": {
                    "direction": "input",
                    "optional": True,
                },
                f"uart{uart_n}_tx": {
                    "direction": "output",
                    "optional": True,
                },
            }
        for gpio in self.gpios:
            self.PINDEFAULTS[gpio.upper()] = {
                "direction": "inout",
                "optional": True,
            }

        uid = self.plugin_setup["uid"]
        self.VERILOGS_GEN = [f"prv32_sram_{uid}.v", f"prv32_{uid}.v"]
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
                "bool": bsize == 1,
            }

        if self.ramsize % 4:
            print("ERROR: ramsize must be multiple of 4")

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
                self.SRCFILES.append("src/sram_gowin.v")
            else:
                self.uart_baud_scale = 1
                self.SRCFILES.append("src/sram_bram.v")
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        instance["module"] = f"prv32_{uid}"
        instance_parameter["BARREL_SHIFTER"] = "0"
        instance_parameter["ENABLE_MUL"] = str(int(self.plugin_setup.get("ENABLE_MUL", self.OPTIONS["ENABLE_MUL"]["default"])))
        instance_parameter["ENABLE_DIV"] = str(int(self.plugin_setup.get("ENABLE_DIV", self.OPTIONS["ENABLE_DIV"]["default"])))
        instance_parameter["ENABLE_FAST_MUL"] = "0"
        instance_parameter["ENABLE_COMPRESSED"] = str(int(self.plugin_setup.get("ENABLE_COMPRESSED", self.OPTIONS["ENABLE_COMPRESSED"]["default"])))
        instance_parameter["ENABLE_IRQ_QREGS"] = "0"
        return instances

    @classmethod
    def extra_files(cls, parent, instances):
        output = []
        output.append("""#!/bin/sh
#
# https://github.com/xpack-dev-tools/riscv-none-elf-gcc-xpack/releases/tag/v15.2.0-1
#
set -x
set -e

# RISCV_BIN="riscv64-unknown-elf"
RISCV_BIN="riscv-none-elf"

cd src/

""")
        for instance in instances:
            uid = instance.plugin_setup["uid"]
            os.makedirs(os.path.join(parent.gateware_path, "src", f"inc_{uid}"), exist_ok=True)

            if instance.fpga_toolchain == "gowin":
                if instance.ramsize != 8192:
                    instance.ramsize = 8192
                    print(f"  INFO: set ram size to {instance.ramsize} (gowin)")
            elif instance.ramsize > 8192:
                instance.ramsize = 8192
                print(f"  INFO: limit ram size to {instance.ramsize}")

            instance.addrbits = instance.clog2(instance.ramsize)
            instance.mabi = "ilp32"
            instance.march = "rv32i"
            instance.gcc_options = ""
            if instance.plugin_setup.get("ENABLE_MUL", instance.OPTIONS["ENABLE_MUL"]["default"]) and instance.plugin_setup.get("ENABLE_DIV", instance.OPTIONS["ENABLE_DIV"]["default"]):
                instance.march += "m"
            if instance.plugin_setup.get("ENABLE_COMPRESSED", instance.OPTIONS["ENABLE_COMPRESSED"]["default"]):
                instance.march += "c"
            instance.march += "2p0"

            startup = []
            startup.append("")
            startup.append(".text")
            startup.append(".global _start")
            startup.append("_start:")
            startup.append(f"	li x2, {instance.ramsize}")
            startup.append("	call main")
            startup.append("")
            target = os.path.join(parent.gateware_path, "src", f"startup_{uid}.s")
            open(target, "w").write("\n".join(startup))

            soc = cls.soc(instance)
            target = os.path.join(parent.gateware_path, f"prv32_{uid}.v")
            open(target, "w").write("\n".join(soc))

            rio_h = cls.rio_h(instance)
            target = os.path.join(parent.gateware_path, "src", f"inc_{uid}", "rio.h")
            open(target, "w").write("\n".join(rio_h))

            rio_c = cls.rio_c(instance)
            target = os.path.join(parent.gateware_path, "src", f"rio_{uid}.c")
            open(target, "w").write("\n".join(rio_c))

            target = os.path.join(parent.gateware_path, "src", f"main_{uid}.c")
            open(target, "w").write(instance.source)

            output.append(f"""

TOOLCHAIN="{instance.fpga_toolchain}"

rm -f conv_to_init prog_{uid}.elf prog_{uid}.hex prog_{uid}.bin main_{uid}.o timer.o uart.o spi.o

$RISCV_BIN-gcc -mno-save-restore -march={instance.march} -mabi={instance.mabi} {instance.gcc_options} -nostartfiles -nostdlib -static -O1 -c timer.c -Iinc_{uid}
$RISCV_BIN-gcc -mno-save-restore -march={instance.march} -mabi={instance.mabi} {instance.gcc_options} -nostartfiles -nostdlib -static -O1 -c uart.c -Iinc_{uid}
$RISCV_BIN-gcc -mno-save-restore -march={instance.march} -mabi={instance.mabi} {instance.gcc_options} -nostartfiles -nostdlib -static -O1 -c spi.c -Iinc_{uid}
$RISCV_BIN-gcc -mno-save-restore -march={instance.march} -mabi={instance.mabi} {instance.gcc_options} -nostartfiles -nostdlib -static -O1 -c main_{uid}.c -Iinc_{uid}
$RISCV_BIN-gcc -mno-save-restore -march={instance.march} -mabi={instance.mabi} {instance.gcc_options} -nostartfiles -nostdlib -static -O1 -c rio_{uid}.c -Iinc_{uid}
$RISCV_BIN-gcc -mno-save-restore -march={instance.march} -mabi={instance.mabi} {instance.gcc_options} -nostartfiles -nostdlib -static -O1 -Tlink_cmd.ld -o prog_{uid}.elf startup_{uid}.s main_{uid}.o rio_{uid}.o timer.o uart.o spi.o
$RISCV_BIN-objcopy prog_{uid}.elf -O binary prog_{uid}.bin
$RISCV_BIN-size -G -d prog_{uid}.elf

rm -f ../mem_init_{uid}.v


if test "$TOOLCHAIN" = "gowin"
then
    # od -v -Ax -t x4 prog_{uid}.bin > prog_{uid}.hex
    gcc -o conv_to_init conv_to_init.c
    ./conv_to_init prog_{uid}.bin > ../mem_init_{uid}.v
    sed "s|include .*|include \\"mem_init_{uid}.v\\"|g" sram_gowin.v | sed "s|module prv32_sram|module prv32_sram_{uid}|g" > ../prv32_sram_{uid}.v
else
    sed "s|src/prog.hex|src/prog_{uid}.hex|g" sram_bram.v | sed "s|module prv32_sram|module prv32_sram_{uid}|g" > ../prv32_sram_{uid}.v
fi
python3 makehex.py prog_{uid}.bin {(instance.ramsize + 3) // 4} > prog_{uid}.hex

""")
        target = os.path.join(parent.gateware_path, "prepare.sh")
        open(target, "w").write("\n".join(output))

    @classmethod
    def rio_h(cls, instance):
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
        output.append('#define CPU_TYPE       "PicoRV32"')
        output.append(f'#define CPU_MABI       "{instance.mabi}"')
        output.append(f'#define CPU_MARCH      "{instance.march}"')
        if instance.fpga_toolchain:
            output.append(f'#define FPGA_TOOLCHAIN "{instance.fpga_toolchain}"')
        if instance.fpga_family:
            output.append(f'#define FPGA_FAMILY    "{instance.fpga_family}"')
        if instance.fpga_type:
            output.append(f'#define FPGA_TYPE      "{instance.fpga_type}"')
        output.append("")
        if instance.plugin_setup.get("ENABLE_MUL", instance.OPTIONS["ENABLE_MUL"]["default"]):
            output.append("#define ENABLE_MUL")
        if instance.plugin_setup.get("ENABLE_DIV", instance.OPTIONS["ENABLE_DIV"]["default"]):
            output.append("#define ENABLE_DIV")
        if instance.plugin_setup.get("ENABLE_COMPRESSED", instance.OPTIONS["ENABLE_COMPRESSED"]["default"]):
            output.append("#define ENABLE_COMPRESSED")

        output.append("")
        if instance.gpios:
            output.append("#define INPUT  0")
            output.append("#define OUTPUT 1")
            output.append("#define LOW    0")
            output.append("#define HIGH   1")
            output.append("#define TOGGLE 2")
            output.append("#define GPIOS ((volatile unsigned int *) 0x80000000)")
            gpio_n = 0
            for pname, pdata in instance.PINDEFAULTS.items():
                if pdata["direction"] == "inout":
                    output.append(f"#define GPIO_{pname.upper()}  {gpio_n}")
                    gpio_n += 1
            output.append("extern void pinMode(uint8_t num, uint8_t dir);")
            output.append("extern void digitalWrite(uint8_t num, uint8_t value);")
            output.append("extern uint8_t digitalRead(uint8_t num);")
            output.append("extern uint32_t mills(void);")
            output.append("")
        output.append("")
        output.append("#define CDT_COUNTER ((volatile unsigned int *) 0x80000010)")
        output.append("#define CDT_COUNTER_H0 ((volatile unsigned short *) 0x80000010)")
        output.append("#define CDT_COUNTER_H2 ((volatile unsigned short *) 0x80000012)")
        output.append("#define CDT_COUNTER_B0 ((volatile unsigned char *) 0x80000010)")
        output.append("#define CDT_COUNTER_B1 ((volatile unsigned char *) 0x80000011)")
        output.append("#define CDT_COUNTER_B2 ((volatile unsigned char *) 0x80000012)")
        output.append("#define CDT_COUNTER_B3 ((volatile unsigned char *) 0x80000013)")
        output.append("")
        output.append("#define UTIMER ((volatile unsigned int *) 0x80000020)")
        output.append("")
        for iname, idata in instance.variables.items():
            ctype = idata.get("ctype", "uint32_t")
            output.append(f"#define RIO_{iname.upper():10s} *((volatile {ctype} *) 0x{idata['addr']:x})")
        output.append("")
        if instance.uarts:
            for baud in (1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600, 1000000, 2500000):
                output.append(f"#define UART_B{baud!s:7s} {instance.gateware.jdata['speed'] * instance.uart_baud_scale // baud}")
            for uart_n in range(instance.uarts):
                output.append(f"#define UART{uart_n}_DIV  ((volatile unsigned int *) 0x80000008)")
                output.append(f"#define UART{uart_n}_DATA ((volatile unsigned int *) 0x8000000c)")
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
        output.append("#ifdef GPIO_SPI0_SCLK")
        output.append("extern unsigned char spi0_transfer_byte(unsigned char send_val);")
        output.append("#endif")
        output.append("")
        output.append("extern void cdt_wbyte0(const unsigned char value);")
        output.append("extern void cdt_wbyte1(const unsigned char value);")
        output.append("extern void cdt_wbyte2(const unsigned char value);")
        output.append("extern void cdt_wbyte3(const unsigned char value);")
        output.append("")
        output.append("extern void cdt_whalf0(const unsigned short value);")
        output.append("extern void cdt_whalf2(const unsigned short value);")
        output.append("")
        output.append("extern void cdt_write(const unsigned int value);")
        output.append("extern unsigned int cdt_read(void);")
        output.append("extern void cdt_delay(const unsigned int value);")
        output.append("extern void delay(const unsigned int value);")
        output.append("")
        output.append("#endif")
        output.append("")
        return output

    @classmethod
    def rio_c(cls, instance):
        output = []
        output.append("#include <rio.h>")
        output.append("")
        output.append("""
// GPIO functions
void pinMode(uint8_t num, uint8_t dir) {
    if (dir == OUTPUT) {
        *GPIOS |= (1<<(num + 16));
    } else {
        *GPIOS &= ~(1<<(num + 16));
    }
}

void digitalWrite(uint8_t num, uint8_t value) {
    if (value == HIGH) {
        *GPIOS |= (1<<num);
    } else if (value == LOW) {
        *GPIOS &= ~(1<<num);
    } else if (TOGGLE) {
        if ((*GPIOS & (1<<num)) != 0) {
            *GPIOS &= ~(1<<num);
        } else {
            *GPIOS |= (1<<num);
        }
    }
}

uint8_t digitalRead(uint8_t num) {
    if ((*GPIOS & (1<<num)) != 0) {
        return HIGH;
    }
    return LOW;
}

// UTIMER
uint32_t mills(void) {
    return *UTIMER;
}

""")
        output.append("")
        return output

    @classmethod
    def soc(cls, instance):
        output = []
        addr = 0x80000030
        uid = instance.plugin_setup["uid"]
        for iname, idata in instance.variables.items():
            idata["addr"] = addr
            addr += 0x04

        output.append(f"module prv32_{uid} (")
        output.append("        input wire  clk,")
        output.append("        input wire  uart0_rx,")
        output.append("        output wire uart0_tx,")
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
            if bsize > 1:
                output.append(f"        {direction} wire [{bsize - 1}:0] {iname},")
            else:
                output.append(f"        {direction} wire {iname},")

        gpio_pins = []
        for pname, pdata in instance.PINDEFAULTS.items():
            if pdata["direction"] == "inout":
                gpio_pins.append(f"inout wire {pname}")

        output.append("        " + ",\n        ".join(gpio_pins))
        output.append("    );")
        output.append("")
        output.append("    parameter [0:0] BARREL_SHIFTER = 0;")
        output.append("    parameter [0:0] ENABLE_MUL = 0;")
        output.append("    parameter [0:0] ENABLE_DIV = 0;")
        output.append("    parameter [0:0] ENABLE_FAST_MUL = 0;")
        output.append("    parameter [0:0] ENABLE_COMPRESSED = 0;")
        output.append("    parameter [0:0] ENABLE_IRQ_QREGS = 0;")
        output.append(f"    parameter MEMBYTES = {instance.ramsize};")
        output.append(f"    parameter ADDRWIDTH = {instance.addrbits};")
        output.append(f"    parameter UART_DIV = {instance.gateware.jdata['speed'] * instance.uart_baud_scale // 115200};")
        output.append("""
    parameter [31:0] STACKADDR = (MEMBYTES); // Grows down. Software should set it.
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

    wire                       uart0_sel;
    wire [31:0]                uart0_data_o;
    wire                       uart0_ready;

    wire                       utimer_sel;
    wire                       utimer_ready;
    wire [31:0]                utimer_data_o;

    wire                       gpios_sel;
    wire                       gpios_ready;
    wire [31:0]                gpios_data_o;
""")

        for iname, idata in instance.variables.items():
            output.append(f"    wire                       {iname}_sel;")
            output.append(f"    wire                       {iname}_ready;")
            output.append(f"    wire [31:0]                {iname}_data_o;")
        output.append("")

        output.append("    // Establish memory map for all slaves:")
        output.append("    //   SRAM       0x00000000 - 0x0001ffff")
        output.append("    //   GPIO       0x80000000")
        output.append("    //   UART       0x80000008 - 0x8000000f")
        output.append("    //   CDT        0x80000010 - 0x80000014")
        output.append("    //   UTIMER     0x80000020 - 0x80000024")
        for iname, idata in instance.variables.items():
            output.append(f"    //   RIO_{iname.upper():10s} 0x{idata['addr']:x} - 0x{idata['addr'] + 3:x}")
        output.append("")

        output.append("    assign sram_sel   = mem_valid && (mem_addr < 32'h00002000);")
        output.append("    assign gpios_sel  = mem_valid && (mem_addr == 32'h80000000);")
        output.append("    assign uart0_sel  = mem_valid && ((mem_addr & 32'hfffffff8) == 32'h80000008);")
        output.append("    assign cdt_sel    = mem_valid && (mem_addr == 32'h80000010);")
        output.append("    assign utimer_sel = mem_valid && (mem_addr == 32'h80000020);")
        for iname, idata in instance.variables.items():
            output.append(f"    assign {iname}_sel = mem_valid && (mem_addr == 32'h{idata['addr']:x});")
        output.append("")

        output.append("    // Core can proceed regardless of *which* slave was targetted and is now ready.")
        output.append("    assign mem_ready = mem_valid & (")
        output.append("        sram_ready |")
        output.append("        gpios_ready |")
        output.append("        uart0_ready |")
        output.append("        cdt_ready |")
        output.append("        utimer_ready |")
        for iname, idata in instance.variables.items():
            output.append(f"        {iname}_ready |")
        output.append("        0);")
        output.append("")

        output.append("    // Select which slave's output data is to be fed to core.")
        output.append("    assign mem_rdata = ")
        output.append("        sram_sel   ? sram_data_o :")
        output.append("        gpios_sel  ? gpios_data_o :")
        output.append("        uart0_sel  ? uart0_data_o :")
        output.append("        cdt_sel    ? cdt_data_o  :")
        output.append("        utimer_sel ? utimer_data_o :")
        for iname, idata in instance.variables.items():
            output.append(f"        {iname}_sel  ? {iname}_data_o  :")
        output.append("        32'h0;")
        output.append("")

        output.append("""
    prv32_reset_control reset_controller (
        .clk(clk),
        .reset_button_n(reset_button_n),
        .reset_n(reset_n)
    );

    prv32_uart_wrap #(.DEFAULT_DIV(UART_DIV)) uart0 (
        .clk(clk),
        .reset_n(reset_n),
        .uart_tx(uart0_tx),
        .uart_rx(uart0_rx),
        .uart_sel(uart0_sel),
        .addr(mem_addr[3:0]),
        .uart_wstrb(mem_wstrb),
        .uart_di(mem_wdata),
        .uart_do(uart0_data_o),
        .uart_ready(uart0_ready)
    );

    prv32_timer cdt (
        .clk(clk),
        .reset_n(reset_n),
        .cdt_sel(cdt_sel),
        .cdt_data_i(mem_wdata),
        .we(mem_wstrb),
        .cdt_ready(cdt_ready),
        .cdt_data_o(cdt_data_o)
    );
""")

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

        gpio_n = 0
        gpio_pins = []
        for pname, pdata in instance.PINDEFAULTS.items():
            if pdata["direction"] == "inout":
                gpio_pins.append(f".gpio{gpio_n}({pname})")
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
            output.append(f"    prv32_rio_v{direction} soc_val_{iname} (")
            output.append("        .clk(clk),")
            output.append("        .reset_n(reset_n),")
            output.append(f"        .v{direction}_sel({iname}_sel),")
            output.append(f"        .v{direction}_data_i(mem_wdata),")
            output.append("        .we(mem_wstrb[0]),")
            output.append(f"        .v{direction}_ready({iname}_ready),")
            output.append(f"        .v{direction}_data_o({iname}_data_o),")
            output.append(f"        .v{direction}({iname})")
            output.append("    );")
            output.append("")

        output.append(f"    prv32_utimer #(.MS_DIVIDER({instance.gateware.jdata['speed'] // 1000})) soc_utimer (")
        output.append("        .clk(clk),")
        output.append("        .reset_n(reset_n),")
        output.append("        .utimer_sel(utimer_sel),")
        output.append("        .utimer_data_i(mem_wdata),")
        output.append("        .we(mem_wstrb[0]),")
        output.append("        .utimer_ready(utimer_ready),")
        output.append("        .utimer_data_o(utimer_data_o)")
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
        .irq         ('b0)
    );

endmodule

""")
        return output
