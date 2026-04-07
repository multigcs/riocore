localparam FPGA_FAMILY = "GW5A-25A";
localparam FPGA_TYPE = "GW5A-LV25MG121NC1/I0";
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
