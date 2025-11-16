localparam FPGA_FAMILY = "Cyclone 10 LP";
localparam FPGA_TYPE = "10CL025YU256C8G";
localparam TOOLCHAIN = "quartus";


// replacement for $clog2
function integer clog2;
  input integer value;
  begin
    value = value-1;
    for (clog2=0; value>0; clog2=clog2+1)
      value = value>>1;
  end
endfunction
