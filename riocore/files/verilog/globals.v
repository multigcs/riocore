localparam FPGA_FAMILY = "verilator";
localparam FPGA_TYPE = "verilator";
localparam TOOLCHAIN = "icestorm";

`define DSP_CALC

// replacement for $clog2
function integer clog2;
  input integer value;
  begin
    value = value-1;
    for (clog2=0; value>0; clog2=clog2+1)
      value = value>>1;
  end
endfunction
