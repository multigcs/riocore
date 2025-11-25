from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "axi"
        self.INFO = "axi interface for armcore comunication"
        self.DESCRIPTION = "axi driver for the interface communication to an embedded arm-core"
        self.KEYWORDS = "zynq xilinx interface"
        self.ORIGIN = ""
        self.TYPE = "interface"
        self.VERILOGS = []
        self.PINDEFAULTS = {}
        self.EXPERIMENTAL = True
        self.OPTIONS = {}
        self.PASSTHROUGH = {
            "S_AXI_ACLK": {"direction": "input", "size": 1},
            "S_AXI_ARESETN": {"direction": "input", "size": 1},
            "S_AXI_AWADDR": {"direction": "input", "size": 7},
            "S_AXI_AWPROT": {"direction": "input", "size": 3},
            "S_AXI_AWVALID": {"direction": "input", "size": 1},
            "S_AXI_AWREADY": {"direction": "output", "size": 1},
            "S_AXI_WDATA": {"direction": "input", "size": 32},
            "S_AXI_WSTRB": {"direction": "input", "size": 4},
            "S_AXI_WVALID": {"direction": "input", "size": 1},
            "S_AXI_WREADY": {"direction": "output", "size": 1},
            "S_AXI_BRESP": {"direction": "output", "size": 2},
            "S_AXI_BVALID": {"direction": "output", "size": 1},
            "S_AXI_BREADY": {"direction": "input", "size": 1},
            "S_AXI_ARADDR": {"direction": "input", "size": 7},
            "S_AXI_ARPROT": {"direction": "input", "size": 3},
            "S_AXI_ARVALID": {"direction": "input", "size": 1},
            "S_AXI_ARREADY": {"direction": "output", "size": 1},
            "S_AXI_RDATA": {"direction": "output", "size": 32},
            "S_AXI_RRESP": {"direction": "output", "size": 2},
            "S_AXI_RVALID": {"direction": "output", "size": 1},
            "S_AXI_RREADY": {"direction": "input", "size": 1},
        }

    def post_setup(self, project):
        verilog_data = [
            """
module axi
    #(
         parameter BUFFER_SIZE=16'd64
     )
     (
        // AXI
        input wire S_AXI_ACLK,
        input wire S_AXI_ARESETN,
        input wire [6:0] S_AXI_AWADDR,
        input wire [2:0] S_AXI_AWPROT,
        input wire S_AXI_AWVALID,
        output wire S_AXI_AWREADY,
        input wire [31:0] S_AXI_WDATA,
        input wire [3:0] S_AXI_WSTRB,
        input wire S_AXI_WVALID,
        output wire S_AXI_WREADY,
        output wire [1:0] S_AXI_BRESP,
        output wire S_AXI_BVALID,
        input wire S_AXI_BREADY,
        input wire [6:0] S_AXI_ARADDR,
        input wire [2:0] S_AXI_ARPROT,
        input wire S_AXI_ARVALID,
        output wire S_AXI_ARREADY,
        output wire [31:0] S_AXI_RDATA,
        output wire [1:0] S_AXI_RRESP,
        output wire S_AXI_RVALID,
        input wire S_AXI_RREADY,
        input wire clk,
        input wire [BUFFER_SIZE-1:0] tx_data,
        output reg [BUFFER_SIZE-1:0] rx_data = 0,
        output reg sync = 0
    );

    reg [BUFFER_SIZE-1:0] rx_data_buffer = 0;
    reg [BUFFER_SIZE-1:0] tx_data_buffer = 0;

    // AXI4LITE signals
    reg [6:0] axi_awaddr;
    reg axi_awready;
    reg axi_wready;
    reg [1:0] axi_bresp;
    reg axi_bvalid;
    reg [6:0] axi_araddr;
    reg axi_arready;
    reg [31:0] axi_rdata;
    reg [1:0] axi_rresp;
    reg axi_rvalid;

    localparam integer ADDR_LSB = 2;
    localparam integer OPT_MEM_ADDR_BITS = 4;
    reg [31:0] slv_reg0;
    wire slv_reg_rden;
    wire slv_reg_wren;
    reg [31:0] reg_data_out;
    integer byte_index;
    reg aw_en;

    assign S_AXI_AWREADY = axi_awready;
    assign S_AXI_WREADY  = axi_wready;
    assign S_AXI_BRESP   = axi_bresp;
    assign S_AXI_BVALID  = axi_bvalid;
    assign S_AXI_ARREADY = axi_arready;
    assign S_AXI_RDATA   = axi_rdata;
    assign S_AXI_RRESP   = axi_rresp;
    assign S_AXI_RVALID  = axi_rvalid;

    assign slv_reg_rden = axi_arready & S_AXI_ARVALID & ~axi_rvalid;
    assign slv_reg_wren = axi_wready && S_AXI_WVALID && axi_awready && S_AXI_AWVALID;

    always @( posedge S_AXI_ACLK ) begin
        if ( S_AXI_ARESETN == 1'b0 ) begin
            axi_awready <= 1'b0;
            aw_en <= 1'b1;
        end  else begin    
            if (~axi_awready && S_AXI_AWVALID && S_AXI_WVALID && aw_en) begin
                axi_awready <= 1'b1;
                aw_en <= 1'b0;
            end else if (S_AXI_BREADY && axi_bvalid) begin
                aw_en <= 1'b1;
                axi_awready <= 1'b0;
            end else begin
                axi_awready <= 1'b0;
            end
        end 
    end       

    always @( posedge S_AXI_ACLK ) begin
        if ( S_AXI_ARESETN == 1'b0 ) begin
            axi_awaddr <= 0;
        end else begin    
            if (~axi_awready && S_AXI_AWVALID && S_AXI_WVALID && aw_en) begin
                axi_awaddr <= S_AXI_AWADDR;
            end
        end 
    end       

    always @( posedge S_AXI_ACLK ) begin
        if ( S_AXI_ARESETN == 1'b0 ) begin
            axi_wready <= 1'b0;
        end else begin    
            if (~axi_wready && S_AXI_WVALID && S_AXI_AWVALID && aw_en ) begin
                axi_wready <= 1'b1;
            end else begin
                axi_wready <= 1'b0;
            end
        end 
    end       

    always @( posedge S_AXI_ACLK ) begin
        sync <= 0;
        if ( S_AXI_ARESETN == 1'b0 ) begin
            slv_reg0 <= 0;
        end else begin
            if (slv_reg_wren) begin
                case ( axi_awaddr[ADDR_LSB+OPT_MEM_ADDR_BITS:ADDR_LSB] )"""
        ]

        flen = project.buffer_size // 8 // 4
        flen32 = (flen * 8 + 31) // 32 * 4
        pos = project.buffer_size
        for n in range(flen32):
            verilog_data.append(f"                    5'h{n:02x}:")
            end = pos - 32
            size = 32
            if end < 0:
                size += end
                end = 0
            verilog_data.append(f"                        rx_data_buffer[{pos - 1}:{end}] <= S_AXI_WDATA[31:{32 - size}];")
            pos -= 32

        verilog_data.append(f"                    5'h{flen32:02x}: begin")
        verilog_data += [
            """                        rx_data <= rx_data_buffer;
                        tx_data_buffer <= tx_data;
                        sync <= 1;
                    end

                    default : begin
                        slv_reg0 <= slv_reg0;
                    end
                endcase
            end
        end
    end    

    always @( posedge S_AXI_ACLK ) begin
        if ( S_AXI_ARESETN == 1'b0 ) begin
            axi_bvalid  <= 0;
            axi_bresp   <= 2'b0;
        end else begin    
            if (axi_awready && S_AXI_AWVALID && ~axi_bvalid && axi_wready && S_AXI_WVALID) begin
                axi_bvalid <= 1'b1;
                axi_bresp  <= 2'b0;
            end else begin
                if (S_AXI_BREADY && axi_bvalid) begin
                    axi_bvalid <= 1'b0; 
                end  
            end
        end
    end   

    always @( posedge S_AXI_ACLK ) begin
        if ( S_AXI_ARESETN == 1'b0 ) begin
            axi_arready <= 1'b0;
            axi_araddr  <= 32'b0;
        end else begin    
            if (~axi_arready && S_AXI_ARVALID) begin
                axi_arready <= 1'b1;
                axi_araddr  <= S_AXI_ARADDR;
            end else begin
                axi_arready <= 1'b0;
            end
        end 
    end       

    always @( posedge S_AXI_ACLK ) begin
        if ( S_AXI_ARESETN == 1'b0 ) begin
            axi_rvalid <= 0;
            axi_rresp  <= 0;
        end else begin    
            if (axi_arready && S_AXI_ARVALID && ~axi_rvalid) begin
                axi_rvalid <= 1'b1;
                axi_rresp  <= 2'b0;
            end else if (axi_rvalid && S_AXI_RREADY) begin
                axi_rvalid <= 1'b0;
            end                
        end
    end    

    always @(*) begin
        case ( axi_araddr[ADDR_LSB+OPT_MEM_ADDR_BITS:ADDR_LSB] )"""
        ]
        flen = project.buffer_size // 8 // 4
        flen32 = (flen * 8 + 31) // 32 * 4
        pos = project.buffer_size
        for n in range(flen32):
            end = pos - 32
            size = 32
            if end < 0:
                size += end
                end = 0
                verilog_data.append(f"            5'h{n:02x}: reg_data_out <= {{tx_data_buffer[{pos - 1}:{end}], {32 - size}'h00}};")
            else:
                verilog_data.append(f"            5'h{n:02x}: reg_data_out <= tx_data_buffer[{pos - 1}:{end}];")
            pos -= 32

        verilog_data += [
            """            default : reg_data_out <= axi_araddr[ADDR_LSB+OPT_MEM_ADDR_BITS:ADDR_LSB];
        endcase
    end

    always @( posedge S_AXI_ACLK ) begin
        if ( S_AXI_ARESETN == 1'b0 ) begin
            axi_rdata  <= 0;
        end else begin    
            if (slv_reg_rden) begin
                axi_rdata <= reg_data_out;
            end   
        end
    end    

endmodule
"""
        ]
        self.VERILOGS_DATA = {"axi.v": "\n".join(verilog_data)}

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        instance_parameter["BUFFER_SIZE"] = "BUFFER_SIZE"
        return instances
