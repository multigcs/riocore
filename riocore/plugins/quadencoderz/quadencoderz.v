
module quadencoderz
    #(
         parameter BITS = 32,
         parameter QUAD_TYPE = 0
     )
     (
         input clk,
         input a,
         input b,
         input z,
         input index_enable,
         output reg index_out = 0,
         output signed [BITS-1:0] position
     );
    reg [2:0] quadA_delayed = 0;
    reg [2:0] quadB_delayed = 0;
    reg [2:0] quadZ_delayed = 0;
    always @(posedge clk) quadA_delayed <= {quadA_delayed[1:0], a};
    always @(posedge clk) quadB_delayed <= {quadB_delayed[1:0], b};
    always @(posedge clk) quadZ_delayed <= {quadZ_delayed[1:0], z};
    wire count_enable = quadA_delayed[1] ^ quadA_delayed[2] ^ quadB_delayed[1] ^ quadB_delayed[2];
    wire count_direction = quadA_delayed[1] ^ quadB_delayed[2];
    reg signed [BITS-1:0] count = 0;
    reg index_wait = 0;
    assign position = $signed(count>>>QUAD_TYPE);
    always @(posedge clk) begin
        if (index_enable == 1 && index_out == 1 && quadZ_delayed == 1) begin
            index_out <= 0;
            count <= 0;
            index_wait <= 1;
        end else begin
            if (index_enable == 1 && index_wait == 0 && index_out == 0) begin
                index_out <= 1;
            end else if (index_enable == 0 && index_wait == 1) begin
                index_wait <= 0;
            end
            if (count_enable) begin
                if(count_direction) begin
                    count <= count + 1;
                end else begin
                    count <= count - 1;
                end
            end
        end

    end
endmodule
