import os

from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "prv32"
        self.INFO = "risc-v softcore"
        self.DESCRIPTION = "picorv32 risc-v cpu for testing"
        self.KEYWORDS = "risc-v softcore cpu"
        self.ORIGIN = ""
        self.NEEDS = ["fpga"]
        self.VERILOGS = ["countdown_timer.v", "reset.v", "gowin_sp.v", "gpio.v", "uart_wrap.v", "simpleuart.v", "picorv32.v"]
        self.SRCFILES = ["src/sram.v", "src/link_cmd.ld", "src/main.c", "src/uart.c", "src/conv_to_init.c", "src/countdown_timer.c"]
        self.OPTIONS = {
            "source": {
                "type": "multiline",
                "description": "source code (asm)",
                "default": "",
            },
        }
        self.PINDEFAULTS = {
            "uart_rx": {
                "direction": "input",
            },
            "uart_tx": {
                "direction": "output",
            },
        }
        for led in range(6):
            self.PINDEFAULTS[f"led{led}"] = {
                "direction": "output",
            }
        uid = self.plugin_setup["uid"]
        self.VERILOGS_GEN = [f"sram_{uid}.v", f"prv32_{uid}.v"]
        self.OPTIONS["source"]["default"] = open(os.path.join(os.path.dirname(__file__), "src", "main.c"), "r").read()
        self.INTERFACE = {
            "vin": {
                "size": 32,
                "direction": "input",
            },
            "vout": {
                "size": 32,
                "direction": "output",
            },
        }
        self.SIGNALS = {
            "vin": {
                "direction": "input",
            },
            "vout": {
                "direction": "output",
            },
        }

    def gateware_instances(self):
        # uid = self.plugin_setup["uid"]
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        instance_parameter["BARREL_SHIFTER"] = "0"
        instance_parameter["ENABLE_MUL"] = "0"
        instance_parameter["ENABLE_DIV"] = "0"
        instance_parameter["ENABLE_FAST_MUL"] = "0"
        instance_parameter["ENABLE_COMPRESSED"] = "0"
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

RISCV_BIN="riscv64-unknown-elf"
RISCV_BIN="riscv-none-elf"

cd src/
rm -rf conv_to_init
gcc -o conv_to_init conv_to_init.c

""")
        for instance in instances:
            uid = instance.plugin_setup["uid"]
            os.makedirs(os.path.join(parent.gateware_path, "src", f"inc_{uid}"), exist_ok=True)
            instance.memsize = 8192

            startup = []
            startup.append("")
            startup.append(".text")
            startup.append(".global _start")
            startup.append("_start:")
            startup.append(f"	li x2, {instance.memsize}")
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

            source = instance.plugin_setup.get("source", instance.OPTIONS["source"]["default"])
            target = os.path.join(parent.gateware_path, "src", f"main_{uid}.c")
            open(target, "w").write(source)

            output.append(f"""

rm -f prog_{uid}.elf prog_{uid}.hex prog_{uid}.bin main_{uid}.o countdown_timer.o uart.o
$RISCV_BIN-gcc -mno-save-restore -march=rv32i2p0 -mabi=ilp32 -nostartfiles -nostdlib -static -O1 -c countdown_timer.c -Iinc_{uid}
$RISCV_BIN-gcc -mno-save-restore -march=rv32i2p0 -mabi=ilp32 -nostartfiles -nostdlib -static -O1 -c uart.c -Iinc_{uid}
$RISCV_BIN-gcc -mno-save-restore -march=rv32i2p0 -mabi=ilp32 -nostartfiles -nostdlib -static -O1 -c main_{uid}.c -Iinc_{uid}
$RISCV_BIN-gcc -mno-save-restore -march=rv32i2p0 -mabi=ilp32 -nostartfiles -nostdlib -static -O1 -c rio_{uid}.c -Iinc_{uid}
$RISCV_BIN-gcc -mno-save-restore -march=rv32i2p0 -mabi=ilp32 -nostartfiles -nostdlib -static -O1 -Tlink_cmd.ld -o prog_{uid}.elf startup_{uid}.s main_{uid}.o rio_{uid}.o countdown_timer.o uart.o

$RISCV_BIN-objcopy prog_{uid}.elf -O binary prog_{uid}.bin
rm -f ../mem_init_{uid}.v
od -v -Ax -t x4 prog_{uid}.bin > prog_{uid}.hex

./conv_to_init prog_{uid}.bin > ../mem_init_{uid}.v

# sed "s|include .*|include \\"mem_init_{uid}.v\\"|g" sram.v | sed "s|module sram|module sram_{uid}|g" > ../sram_{uid}.v
sed "s|include .*|include \\"mem_init_{uid}.v\\"|g" sram.v > ../sram_{uid}.v

""")

        target = os.path.join(parent.gateware_path, "prepare.sh")
        open(target, "w").write("\n".join(output))

    @classmethod
    def rio_h(cls, instance):
        output = []
        output.append("#ifndef RIO_H")
        output.append("#define RIO_H")
        output.append("")
        output.append("#define LEDS ((volatile unsigned char *) 0x80000000)")
        output.append("")
        output.append("#define UART_DIV ((volatile unsigned char *) 0x80000008)")
        output.append("#define UART_DATA ((volatile unsigned char *) 0x8000000c)")
        output.append("")
        output.append("#define CDT_COUNTER ((volatile unsigned int *) 0x80000010)")
        output.append("#define CDT_COUNTER_H0 ((volatile unsigned short *) 0x80000010)")
        output.append("#define CDT_COUNTER_H2 ((volatile unsigned short *) 0x80000012)")
        output.append("#define CDT_COUNTER_B0 ((volatile unsigned char *) 0x80000010)")
        output.append("#define CDT_COUNTER_B1 ((volatile unsigned char *) 0x80000011)")
        output.append("#define CDT_COUNTER_B2 ((volatile unsigned char *) 0x80000012)")
        output.append("#define CDT_COUNTER_B3 ((volatile unsigned char *) 0x80000013)")
        output.append("")
        for iname, idata in instance.INTERFACE.items():
            if idata["size"] == 32:
                output.append(f"#define RIO_{iname.upper():10s} ((volatile unsigned int *) 0x{idata['addr']:x})")
        output.append("")

        output.append("extern void set_leds(unsigned char val);")
        output.append("extern unsigned char get_leds(void);")
        output.append("")
        output.append("extern void uart_set_div(unsigned int div);")
        output.append("extern void uart_print_hex(unsigned int val);")
        output.append("extern char uart_getchar(void);")
        output.append("extern void uart_putchar(char ch);")
        output.append("extern void uart_puts(char *s);")
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
        output.append("")
        output.append("#endif")
        output.append("")
        return output

    @classmethod
    def rio_c(cls, instance):
        output = []
        output.append('#include "rio.h"')
        output.append("")
        output.append("""
void set_leds(unsigned char val) {
  *LEDS = val;
}

unsigned char get_leds(void) {
  return *LEDS;
}
""")
        output.append("")
        return output

    @classmethod
    def soc(cls, instance):
        output = []
        addr = 0x80000020
        for iname, idata in instance.INTERFACE.items():
            if (idata["direction"] == "output" and idata["size"] == 32) or (idata["direction"] == "input" and idata["size"] == 32):
                idata["addr"] = addr
                addr += 0x10

        output.append("""
module prv32 (
        input wire  clk,
""")
        output.append("""
        input wire  uart_rx,
        output wire uart_tx,
""")

        for iname, idata in instance.INTERFACE.items():
            if idata["direction"] == "output" and idata["size"] == 32:
                output.append(f"        input  wire [31:0] {iname},")
            elif idata["direction"] == "input" and idata["size"] == 32:
                output.append(f"        output  wire [31:0] {iname},")

        output.append("""
        output wire led0,
        output wire led1,
        output wire led2,
        output wire led3,
        output wire led4,
        output wire led5
    );

    parameter [0:0] BARREL_SHIFTER = 0;
    parameter [0:0] ENABLE_MUL = 0;
    parameter [0:0] ENABLE_DIV = 0;
    parameter [0:0] ENABLE_FAST_MUL = 0;
    parameter [0:0] ENABLE_COMPRESSED = 0;
    parameter [0:0] ENABLE_IRQ_QREGS = 0;
""")
        output.append(f"    parameter integer MEMBYTES = {instance.memsize};")
        output.append("""
    parameter [31:0] STACKADDR = (MEMBYTES); // Grows down. Software should set it.
    parameter [31:0] PROGADDR_RESET = 32'h0000_0000;
    parameter [31:0] PROGADDR_IRQ = 32'h0000_0000;

	wire [5:0] gpios;
	assign led0 = gpios[0];
	assign led1 = gpios[1];
	assign led2 = gpios[2];
	assign led3 = gpios[3];
	assign led4 = gpios[4];
	assign led5 = gpios[5];

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
    wire                       gpios_sel;
    wire                       gpios_ready;
    wire [31:0]                gpios_data_o;
    wire                       cdt_sel;
    wire                       cdt_ready;
    wire [31:0]                cdt_data_o;
    wire                       uart_sel;
    wire [31:0]                uart_data_o;
    wire                       uart_ready;
""")

        for iname, idata in instance.INTERFACE.items():
            if idata["size"] == 32:
                output.append(f"    wire                       {iname}_sel;")
                output.append(f"    wire                       {iname}_ready;")
                output.append(f"    wire [31:0]                {iname}_data_o;")
        output.append("")

        output.append("    // Establish memory map for all slaves:")
        output.append("    //   SRAM       0x00000000 - 0x0001ffff")
        output.append("    //   LED        0x80000000")
        output.append("    //   UART       0x80000008 - 0x8000000f")
        output.append("    //   CDT        0x80000010 - 0x80000014")
        for iname, idata in instance.INTERFACE.items():
            if idata["size"] == 32:
                output.append(f"    //   RIO_{iname.upper():10s} 0x{idata['addr']:x} - 0x{idata['addr'] + 4:x}")
        output.append("")

        output.append("    assign sram_sel  = mem_valid && (mem_addr < 32'h00002000);")
        output.append("    assign gpios_sel = mem_valid && (mem_addr == 32'h80000000);")
        output.append("    assign uart_sel  = mem_valid && ((mem_addr & 32'hfffffff8) == 32'h80000008);")
        output.append("    assign cdt_sel   = mem_valid && (mem_addr == 32'h80000010);")
        for iname, idata in instance.INTERFACE.items():
            if idata["size"] == 32:
                output.append(f"    assign {iname}_sel = mem_valid && (mem_addr == 32'h{idata['addr']:x});")
        output.append("")

        output.append("    // Core can proceed regardless of *which* slave was targetted and is now ready.")
        output.append("    assign mem_ready = mem_valid & (")
        output.append("        sram_ready |")
        output.append("        gpios_ready |")
        output.append("        uart_ready |")
        output.append("        cdt_ready |")
        for iname, idata in instance.INTERFACE.items():
            if idata["size"] == 32:
                output.append(f"        {iname}_ready |")
        output.append("        0);")
        output.append("")

        output.append("    // Select which slave's output data is to be fed to core.")
        output.append("    assign mem_rdata = ")
        output.append("        sram_sel ? sram_data_o :")
        output.append("        gpios_sel ? gpios_data_o :")
        output.append("        uart_sel ? uart_data_o :")
        output.append("        cdt_sel  ? cdt_data_o  :")
        for iname, idata in instance.INTERFACE.items():
            if idata["size"] == 32:
                output.append(f"        {iname}_sel  ? {iname}_data_o  :")
        output.append("        32'h0;")
        output.append("")

        output.append("""

    assign gpios = ~gpios_data_o[5:0]; // Connect to the gpios off the FPGA

    reset_control reset_controller (
        .clk(clk),
        .reset_button_n(reset_button_n),
        .reset_n(reset_n)
    );

    uart_wrap uart (
        .clk(clk),
        .reset_n(reset_n),
        .uart_tx(uart_tx),
        .uart_rx(uart_rx),
        .uart_sel(uart_sel),
        .addr(mem_addr[3:0]),
        .uart_wstrb(mem_wstrb),
        .uart_di(mem_wdata),
        .uart_do(uart_data_o),
        .uart_ready(uart_ready)
    );

    countdown_timer cdt (
        .clk(clk),
        .reset_n(reset_n),
        .cdt_sel(cdt_sel),
        .cdt_data_i(mem_wdata),
        .we(mem_wstrb),
        .cdt_ready(cdt_ready),
        .cdt_data_o(cdt_data_o)
    );

    sram #(.ADDRWIDTH(13)) memory (
        .clk(clk),
        .resetn(reset_n),
        .sram_sel(sram_sel),
        .wstrb(mem_wstrb),
        .addr(mem_addr[12:0]),
        .sram_data_i(mem_wdata),
        .sram_ready(sram_ready),
        .sram_data_o(sram_data_o)
    );

    gpio soc_gpios (
        .clk(clk),
        .reset_n(reset_n),
        .gpios_sel(gpios_sel),
        .gpios_data_i(mem_wdata[5:0]),
        .we(mem_wstrb[0]),
        .gpios_ready(gpios_ready),
        .gpios_data_o(gpios_data_o)
    );
""")

        for iname, idata in instance.INTERFACE.items():
            if idata["direction"] == "output" and idata["size"] == 32:
                output.append(f"    rio_vout soc_val_{iname} (")
                output.append("        .clk(clk),")
                output.append("        .reset_n(reset_n),")
                output.append(f"        .vout_sel({iname}_sel),")
                output.append("        .vout_data_i(mem_wdata),")
                output.append("        .we(mem_wstrb[0]),")
                output.append(f"        .vout_ready({iname}_ready),")
                output.append(f"        .vout_data_o({iname}_data_o),")
                output.append(f"        .vout({iname})")
                output.append("    );")
            elif idata["direction"] == "input" and idata["size"] == 32:
                output.append(f"    rio_vin soc_val_{iname} (")
                output.append("        .clk(clk),")
                output.append("        .reset_n(reset_n),")
                output.append(f"        .vin_sel({iname}_sel),")
                output.append("        .vin_data_i(mem_wdata),")
                output.append("        .we(mem_wstrb[0]),")
                output.append(f"        .vin_ready({iname}_ready),")
                output.append(f"        .vin_data_o({iname}_data_o),")
                output.append(f"        .vin({iname})")
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

module rio_vin (
    input wire         clk,
    input wire         reset_n,
    input wire         vin_sel,
    input wire [31:0]  vin_data_i,
    input wire         we,
    output wire        vin_ready,
    output wire [31:0]  vin_data_o,
    output reg [31:0]  vin
    );

    assign vin_ready = vin_sel;
    assign vin_data_o = vin;

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            vin <= 'b0;
        end else if (vin_sel) begin
            if (we) begin
                vin <= vin_data_i;
            end
        end
    end
endmodule

module rio_vout (
    input wire         clk,
    input wire         reset_n,
    input wire         vout_sel,
    input wire [31:0]  vout_data_i,
    input wire         we,
    output wire        vout_ready,
    output wire [31:0] vout_data_o,
    input wire [31:0]  vout
    );

    assign vout_ready = vout_sel;
    assign vout_data_o = vout;

endmodule
""")
        return output
