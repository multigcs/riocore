localparam FPGA_FAMILY = "GW1N-9C";
localparam FPGA_TYPE = "GW1NR-LV9QN88PC6/I5";
localparam TOOLCHAIN = "gowin";


// replacement for $clog2
function integer clog2;
  input integer value;
  begin
    value = value-1;
    for (clog2=0; value>0; clog2=clog2+1)
      value = value>>1;
  end
endfunction
