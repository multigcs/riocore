import os

from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "serv"
        self.INFO = "minimal risc-v softcore"
        self.DESCRIPTION = "minimal risc-v cpu for testing"
        self.KEYWORDS = "risc-v softcore cpu"
        self.ORIGIN = ""
        self.NEEDS = ["fpga"]
        uid = self.plugin_setup["uid"]
        self.VERILOGS = ["ram32.v", "ser_add.v", "ser_lt.v", "ser_shift.v", "serv_alu.v", "serv_bufreg.v", "serv_csr.v", "serv_ctrl.v", "serv_decode.v", "serv_mem_if.v", "serv_rf_if.v", "serv_rf_ram_if.v", "serv_rf_ram.v", "serv_rf_top.v", "serv_state.v", "serv_top.v", "shift_reg.v"]
        self.SRCFILES = ["src/makehex.py", "src/link.ld", "src/serv_params.vh", "src/main.c"]
        self.PLUGIN_CONFIGS = {"Source-Editor": "config.py"}
        self.OPTIONS = {
            "ramsize": {
                "type": "select",
                "options": ["512", "768", "1024", "2048", "4096", "8192"],
                "default": "512",
                "description": "size of ram in bytes",
            },
        }
        self.PINDEFAULTS = {}
        self.source = self.plugin_setup.get("source", open(os.path.join(os.path.dirname(__file__), "src", "main.c"), "r").read())
        self.gpios = self.plugin_setup.get("gpios", {})
        for gpio in self.gpios:
            self.PINDEFAULTS[gpio.upper()] = {
                "direction": "inout",
                "optional": True,
            }
        self.VERILOGS_GEN = [f"serv_{uid}.v"]

    def gateware_instances(self, gateware=None):
        uid = self.plugin_setup["uid"]
        if gateware:
            self.gateware = gateware
            self.fpga_toolchain = gateware.jdata["toolchain"]
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance["module"] = f"serv_{uid}"
        instance_arguments = instance["arguments"]
        gpio_n = 0
        for gpio in self.gpios:
            if gpio.upper() in instance_arguments:
                var = instance_arguments[gpio.upper()]
                del instance_arguments[gpio.upper()]
                instance_arguments[f"gpio{gpio_n}"] = var
            gpio_n += 1
        return instances

    @classmethod
    def serv_v(cls, instance):
        uid = instance.plugin_setup["uid"]
        ramsize = int(instance.plugin_setup.get("ramsize", instance.OPTIONS["ramsize"]["default"]))
        output = []
        output.append(f"module serv_{uid} (")
        gpio_n = 0
        for gpio in instance.gpios:
            output.append(f"    inout wire gpio{gpio_n},")
            gpio_n += 1
        output.append("    input wire clk")
        output.append(");")
        output.append(f"    parameter RAM_SIZE = {ramsize};")
        output.append(f'    parameter INITIAL_FILE = "src/prog_{uid}.hex";')

        output.append("""
    reg resetn = 0;
    reg [1:0] counter = 1;
    always @(posedge clk) begin
        if (counter == 0) begin
            resetn <= 1;
        end else begin
            counter <= counter - 1;
        end
    end

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
        output.append("")
        output.append("    assign i_dbus_rdt = (o_dbus_adr == 'h80000000) ? {gdir, gpio15, gpio14, gpio13, gpio12, gpio11, gpio10, gpio9, gpio8, gpio7, gpio6, gpio5, gpio4, gpio3, gpio2, gpio1, gpio0} : 32'h00;")
        output.append("")
        output.append("    always @(posedge clk) begin")
        output.append("        if (o_dbus_cyc && o_dbus_we && o_dbus_adr == 'h80000000) begin")
        output.append("            gout <= o_dbus_dat[15:0];")
        if instance.fpga_toolchain != "icestorm":
            output.append("            gdir <= o_dbus_dat[31:16];")
        output.append("        end")
        output.append("    end")

        output.append("endmodule")
        output.append("")
        return output

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

""")
        for instance in instances:
            uid = instance.plugin_setup["uid"]
            ramsize = int(instance.plugin_setup.get("ramsize", instance.OPTIONS["ramsize"]["default"]))

            serv_v = cls.serv_v(instance)
            target = os.path.join(parent.gateware_path, f"serv_{uid}.v")
            open(target, "w").write("\n".join(serv_v))

            startup = []
            startup.append("")
            startup.append(".text")
            startup.append(".global _start")
            startup.append("_start:")
            startup.append(f"	li x2, {ramsize}")
            startup.append("	call main")
            startup.append("")
            target = os.path.join(parent.gateware_path, "src", f"startup_{uid}.s")
            open(target, "w").write("\n".join(startup))

            target = os.path.join(parent.gateware_path, "src", f"main_{uid}.c")
            open(target, "w").write(instance.source)

            instance.march = "rv32i"
            instance.mabi = "ilp32"
            instance.gcc_options = ""

            output.append(f"""
echo "compile prog_{uid}.hex"
rm -f prog_{uid}.elf prog_{uid}.bin prog_{uid}.hex

FLAGS="-nostartfiles -nostdlib -static -Os"

#$RISCV_BIN-gcc -nostdlib -nostartfiles -march=rv32i -mabi=ilp32 -Tlink.ld -oprog_{uid}.elf prog_{uid}.S

$RISCV_BIN-gcc -mno-save-restore -march={instance.march} -mabi={instance.mabi} {instance.gcc_options} $FLAGS -c main_{uid}.c
$RISCV_BIN-gcc -mno-save-restore -march={instance.march} -mabi={instance.mabi} {instance.gcc_options} $FLAGS -Tlink.ld -o prog_{uid}.elf startup_{uid}.s main_{uid}.o
$RISCV_BIN-size -G -d prog_{uid}.elf

$RISCV_BIN-objcopy -O binary prog_{uid}.elf prog_{uid}.bin
python3 makehex.py prog_{uid}.bin {ramsize // 4} > prog_{uid}.hex
#rm -rf prog_{uid}.bin prog_{uid}.elf
    """)

        target = os.path.join(parent.gateware_path, "prepare.sh")
        open(target, "w").write("\n".join(output))
