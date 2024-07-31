//----------------------------------------------------------------------
//   Licensed under the Apache License, Version 2.0 (the
//   "License"); you may not use this file except in
//   compliance with the License.  You may obtain a copy of
//   the License at
//
//       http://www.apache.org/licenses/LICENSE-2.0
//
//   Unless required by applicable law or agreed to in
//   writing, software distributed under the License is
//   distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
//   CONDITIONS OF ANY KIND, either express or implied.  See
//   the License for the specific language governing
//   permissions and limitations under the License.
//----------------------------------------------------------------------
//----------------------------------------------------------------------
// Author          : LAKKA
// Mail            : Ja_P_S@outlook.com
// File            : udp.sv
//----------------------------------------------------------------------
// Creation Date   : 06.05.2023
//----------------------------------------------------------------------
//

/* verilator lint_off WIDTHTRUNC */
/* verilator lint_off WIDTHEXPAND */
/* verilator lint_off WIDTHCONCAT */
/* verilator lint_off COMBDLY */

module udp (
	clk1m,
	rst,
	clk50m,
	ready,
	netrmii_clk50m,
	netrmii_rx_crs,
	netrmii_mdc,
	netrmii_txen,
	netrmii_mdio,
	netrmii_txd,
	netrmii_rxd,
	phyrst,
	rx_head_o,
	rx_head_av_o,
	rx_data_o,
	rx_data_av_o,
	rx_head_rdy_i,
	rx_data_rdy_i,
	tx_ip_i,
	tx_src_port_i,
	tx_dst_port_i,
	tx_req_i,
	tx_data_i,
	tx_data_av_i,
	tx_req_rdy_o,
	tx_data_rdy_o
);
	parameter [31:0] ip_adr = 32'd0;
	parameter [47:0] mac_adr = 48'd0;
	parameter signed [31:0] arp_refresh_interval = 100000000;
	parameter signed [31:0] arp_max_life_time = 500000000;
	parameter [71:0] arp_head = 72'h080600010800060400;
	input clk1m;
	input rst;
	output wire clk50m;
	output wire ready;
	input netrmii_clk50m;
	input netrmii_rx_crs;
	output wire netrmii_mdc;
	output wire netrmii_txen;
	inout netrmii_mdio;
	output wire [1:0] netrmii_txd;
	input [1:0] netrmii_rxd;
	output wire phyrst;
	output reg [31:0] rx_head_o;
	output reg rx_head_av_o;
	output reg [7:0] rx_data_o;
	output reg rx_data_av_o;
	input wire rx_head_rdy_i;
	input wire rx_data_rdy_i;
	input wire [31:0] tx_ip_i;
	input wire [15:0] tx_src_port_i;
	input wire [15:0] tx_dst_port_i;
	input wire tx_req_i;
	input wire [7:0] tx_data_i;
	input wire tx_data_av_i;
	output reg tx_req_rdy_o;
	output reg tx_data_rdy_o;
	reg rphyrst;
	assign netrmii_mdc = clk1m;
	reg phy_rdy;
	reg SMI_trg;
	wire SMI_ack;
	wire SMI_ready;
	reg SMI_rw;
	reg [4:0] SMI_adr;
	wire [15:0] SMI_data;
	reg [15:0] SMI_wdata;
	reg signed [7:0] SMI_status;
	assign ready = phy_rdy;
	always @(posedge clk1m or negedge rst)
		if (rst == 1'b0) begin
			phy_rdy <= 1'b0;
			rphyrst <= 1'b0;
			SMI_trg <= 1'b0;
			SMI_adr <= 5'd1;
			SMI_rw <= 1'b1;
			SMI_status <= 0;
		end
		else begin
			rphyrst <= 1'b1;
			if (phy_rdy == 1'b0) begin
				SMI_trg <= 1'b1;
				if (SMI_ack && SMI_ready)
					case (SMI_status)
						0: begin
							SMI_adr <= 5'd31;
							SMI_wdata <= 16'h0007;
							SMI_rw <= 1'b0;
							SMI_status <= 1;
						end
						1: begin
							SMI_adr <= 5'd16;
							SMI_wdata <= 16'h0ffe;
							SMI_status <= 2;
						end
						2: begin
							SMI_rw <= 1'b1;
							SMI_status <= 3;
						end
						3: begin
							SMI_adr <= 5'd31;
							SMI_wdata <= 16'h0000;
							SMI_rw <= 1'b0;
							SMI_status <= 4;
						end
						4: begin
							SMI_adr <= 5'd1;
							SMI_rw <= 1'b1;
							SMI_status <= 5;
						end
						5:
							if (SMI_data[2]) begin
								phy_rdy <= 1'b1;
								SMI_trg <= 1'b0;
							end
					endcase
			end
		end
	SMI_ct ct(
		.clk(clk1m),
		.rst(rphyrst),
		.rw(SMI_rw),
		.trg(SMI_trg),
		.ready(SMI_ready),
		.ack(SMI_ack),
		.phy_adr(5'd1),
		.reg_adr(SMI_adr),
		.data(SMI_wdata),
		.smi_data(SMI_data),
		.mdio(netrmii_mdio)
	);
	assign phyrst = rphyrst;
	assign clk50m = netrmii_clk50m;
	reg arp_rpy_fin;
	reg signed [7:0] rx_state;
	reg signed [7:0] cnt;
	reg [7:0] rx_data_s;
	wire crs;
	assign crs = netrmii_rx_crs;
	wire [1:0] rxd;
	assign rxd = netrmii_rxd;
	reg signed [7:0] rx_cnt;
	reg signed [7:0] tick;
	reg fifo_in;
	reg [7:0] fifo_d;
	always @(*) begin
		fifo_in <= (tick == 0) && (rx_state == 3);
		fifo_d <= rx_data_s;
	end
	reg fifo_drop;
	always @(posedge clk50m or negedge phy_rdy)
		if (phy_rdy == 1'b0)
			cnt <= 0;
		else begin
			if (crs) begin
				tick <= tick + 8'd1;
				if (tick == 3)
					tick <= 0;
			end
			rx_cnt <= 0;
			fifo_drop <= 1'b0;
			case (rx_state)
				0: rx_state <= 1;
				1:
					if (rx_data_s[7:0] == 8'h55)
						rx_state <= 2;
				2: begin
					tick <= 1;
					if (rx_data_s == 8'h55)
						rx_cnt <= rx_cnt + 8'd1;
					else if ((rx_data_s == 8'hd5) && (rx_cnt > 26)) begin
						rx_state <= 3;
						tick <= 1;
					end
					else
						rx_state <= 0;
				end
				3:
					if (crs == 1'b0)
						fifo_drop <= 1'b1;
			endcase
			if (crs == 1'b0) begin
				rx_state <= 0;
				rx_data_s <= 8'b00xxxxxx;
			end
			if (crs)
				rx_data_s <= {rxd, rx_data_s[7:2]};
		end
	wire [7:0] rx_data_gd;
	wire rx_data_rdy;
	wire rx_data_fin;
	reg signed [15:0] rx_data_byte_cnt;
	reg signed [7:0] ethernet_resolve_status;
	reg [47:0] rx_info_buf;
	reg [47:0] rx_src_mac;
	wire [15:0] rx_type;
	reg [2:0] arp_request;
	reg [1:0] arp_list;
	reg signed [31:0] arp_life_time [1:0];
	reg [47:0] arp_mac_0;
	reg [47:0] arp_mac_1;
	reg [31:0] arp_ip_0;
	reg [31:0] arp_ip_1;
	reg [1:0] arp_clean;
	reg signed [15:0] head_len;
	reg [17:0] checksum;
	reg [31:0] src_ip;
	reg [31:0] dst_ip;
	reg [15:0] src_port;
	reg [15:0] dst_port;
	reg [15:0] idf;
	reg [15:0] udp_len;
	reg signed [15:0] rx_head_fifo_head_int;
	reg signed [15:0] rx_head_fifo_head;
	reg signed [15:0] rx_head_fifo_tail = 0;
	reg [31:0] rx_head_fifo [127:0];
	reg [31:0] rx_head_data_i_port;
	reg rx_head_data_i_en;
	reg [7:0] rx_head_data_i_adr;
	task rx_head_fifo_push;
		input [31:0] data;
		begin
			rx_head_data_i_port <= data;
			rx_head_data_i_en <= 1'b1;
			rx_head_data_i_adr <= rx_head_fifo_head_int[7:0];
			rx_head_fifo_head_int <= rx_head_fifo_head_int + 16'd1;
			if (rx_head_fifo_head_int == 127)
				rx_head_fifo_head_int <= 0;
		end
	endtask
	reg signed [15:0] rx_data_fifo_head_int;
	reg signed [15:0] rx_data_fifo_head;
	reg signed [15:0] rx_data_fifo_tail = 0;
	reg [7:0] rx_data_fifo [8191:0];
	reg [7:0] rx_data_fifo_i_port;
	reg rx_data_fifo_i_en;
	reg [12:0] rx_data_fifo_i_adr;
	task rx_data_fifo_push;
		input [7:0] data;
		begin
			rx_data_fifo_i_port <= data;
			rx_data_fifo_i_en <= 1'b1;
			rx_data_fifo_i_adr <= rx_data_fifo_head_int[12:0];
			rx_data_fifo_head_int <= rx_data_fifo_head_int + 16'd1;
			if (rx_data_fifo_head_int == 8191)
				rx_data_fifo_head_int <= 0;
		end
	endtask
	reg rx_fin;
	always @(posedge clk50m or negedge phy_rdy)
		if (phy_rdy == 1'b0) begin
			ethernet_resolve_status <= 0;
			rx_head_fifo_head <= 0;
			rx_head_fifo_head_int <= 0;
			rx_data_fifo_head <= 0;
			rx_data_fifo_head_int <= 0;
			arp_list <= 2'b00;
		end
		else begin
			if (arp_list[0] == 1'b1) begin
				if (arp_life_time[0] != 0)
					arp_life_time[0] <= arp_life_time[0] - 1;
				else
					arp_list[0] <= 1'b0;
			end
			else
				arp_life_time[0] <= arp_max_life_time;
			if (arp_list[1] == 1'b1) begin
				if (arp_life_time[1] != 0)
					arp_life_time[1] <= arp_life_time[1] - 1;
				else
					arp_list[1] <= 1'b0;
			end
			else
				arp_life_time[1] <= arp_max_life_time;
			if (arp_clean[1])
				arp_list[1] <= 1'b0;
			if (arp_clean[0])
				arp_list[0] <= 1'b0;
			if (rx_head_data_i_en)
				rx_head_fifo[rx_head_data_i_adr] <= rx_head_data_i_port;
			rx_head_data_i_en <= 1'b0;
			if (rx_data_fifo_i_en)
				rx_data_fifo[rx_data_fifo_i_adr] <= rx_data_fifo_i_port;
			rx_data_fifo_i_en <= 1'b0;
			rx_fin <= rx_data_fin;
			if (rx_data_byte_cnt[0] == 1'b0)
				checksum <= ({2'b00, checksum[15:0]} + {2'b00, rx_info_buf[15:0]}) + {15'd0, checksum[17:16]};
			if (rx_data_byte_cnt == 14)
				checksum <= 0;
			if ((arp_request > 3) && arp_rpy_fin)
				arp_request <= 0;
			rx_data_byte_cnt <= rx_data_byte_cnt + 8'd1;
			rx_info_buf <= {rx_info_buf[39:0], rx_data_gd};
			case (ethernet_resolve_status)
				0:
					if (rx_data_byte_cnt == 6) begin
						if ((rx_info_buf == mac_adr) || (rx_info_buf == 48'hffffffffffff))
							ethernet_resolve_status <= 1;
						else
							ethernet_resolve_status <= 100;
					end
				1: begin
					rx_head_fifo_head_int <= rx_head_fifo_head;
					rx_data_fifo_head_int <= rx_data_fifo_head;
					if (rx_data_byte_cnt == 12)
						rx_src_mac <= rx_info_buf;
					if (rx_data_byte_cnt == 14) begin
						ethernet_resolve_status <= 100;
						if (rx_info_buf[15:0] == 16'h0800)
							ethernet_resolve_status <= 20;
						if (rx_info_buf[15:0] == 16'h0806)
							ethernet_resolve_status <= 30;
					end
				end
				20: begin
					if ((((rx_data_fifo_tail + 127) - rx_data_fifo_head_int) % 128) < 4)
						ethernet_resolve_status <= 100;
					if ((((rx_data_fifo_tail + 8191) - rx_data_fifo_head_int) % 8192) < 1600)
						ethernet_resolve_status <= 100;
					if (rx_data_byte_cnt == 20) begin
						if (rx_info_buf[47:44] != 4'd4)
							ethernet_resolve_status <= 100;
						head_len <= rx_info_buf[43:40] * 4;
						idf <= rx_info_buf[15:0];
					end
					if (rx_data_byte_cnt == 26) begin
						if (rx_info_buf[23:16] != 8'h11)
							ethernet_resolve_status <= 100;
					end
					if (rx_data_byte_cnt == 30)
						src_ip <= rx_info_buf[31:0];
					if (rx_data_byte_cnt == (head_len + 14)) begin
						ethernet_resolve_status <= 21;
						if (rx_data_byte_cnt != 34)
							checksum <= (((src_ip[15:0] + src_ip[31:16]) + dst_ip[15:0]) + dst_ip[31:16]) + 16'h0011;
						else
							checksum <= (((src_ip[15:0] + src_ip[31:16]) + rx_info_buf[15:0]) + rx_info_buf[31:16]) + 16'h0011;
					end
					if (rx_data_byte_cnt == 34) begin
						if ((rx_info_buf[31:0] != ip_adr) && (rx_info_buf[31:0] != 32'hffffffff))
							ethernet_resolve_status <= 100;
						dst_ip <= rx_info_buf[31:0];
						if ((((checksum[17:0] + {2'd0, rx_info_buf[15:0]}) != 18'h0ffff) && ((checksum[17:0] + {2'd0, rx_info_buf[15:0]}) != 18'h1fffe)) && ((checksum[17:0] + {2'd0, rx_info_buf[15:0]}) != 18'h2fffd))
							ethernet_resolve_status <= 100;
					end
				end
				21: begin
					if (rx_data_byte_cnt == (head_len + 18))
						rx_head_fifo_push(src_ip);
					if (rx_data_byte_cnt == (head_len + 19))
						rx_head_fifo_push(dst_ip);
					if (rx_data_byte_cnt == (head_len + 21))
						rx_head_fifo_push({src_port, dst_port});
					if (rx_data_byte_cnt == (head_len + 22))
						rx_head_fifo_push({idf, udp_len - 8});
					if (rx_data_byte_cnt == (head_len + 20)) begin
						src_port <= rx_info_buf[47:32];
						dst_port <= rx_info_buf[31:16];
						udp_len <= rx_info_buf[15:0];
					end
					if ((rx_data_byte_cnt > (head_len + 22)) && (udp_len != 8))
						rx_data_fifo_push(rx_info_buf[7:0]);
					if (rx_data_byte_cnt == ((head_len + 14) + udp_len)) begin
						if (rx_data_byte_cnt[0] == 1'b1) begin
							if (((((checksum[17:0] + {2'd0, rx_info_buf[7:0], 8'd0}) + udp_len) != 18'h0ffff) && (((checksum[17:0] + {2'd0, rx_info_buf[7:0], 8'd0}) + udp_len) != 18'h1fffe)) && (((checksum[17:0] + {2'd0, rx_info_buf[7:0], 8'd0}) + udp_len) != 18'h2fffd))
								ethernet_resolve_status <= 100;
							else begin
								ethernet_resolve_status <= 29;
								rx_head_fifo_head <= rx_head_fifo_head_int;
								if (udp_len != 8)
									rx_data_fifo_head <= (rx_data_fifo_head_int == 8191 ? 16'd0 : rx_data_fifo_head_int + 16'd1);
							end
						end
						else if (((((checksum[17:0] + {2'd0, rx_info_buf[15:0]}) + udp_len) != 18'h0ffff) && (((checksum[17:0] + {2'd0, rx_info_buf[15:0]}) + udp_len) != 18'h1fffe)) && (((checksum[17:0] + {2'd0, rx_info_buf[15:0]}) + udp_len) != 18'h2fffd))
							ethernet_resolve_status <= 100;
						else begin
							ethernet_resolve_status <= 29;
							rx_head_fifo_head <= rx_head_fifo_head_int;
							if (udp_len != 8)
								rx_data_fifo_head <= (rx_data_fifo_head_int == 8191 ? 16'd0 : rx_data_fifo_head_int + 16'd1);
						end
					end
				end
				29:
					;
				30:
					if (rx_data_byte_cnt == 20) begin
						if (rx_info_buf == 48'h000108000604)
							ethernet_resolve_status <= 31;
						else
							ethernet_resolve_status <= 100;
					end
				31: begin
					if (rx_data_byte_cnt == 22) begin
						if ((rx_info_buf[15:0] == 16'h0001) && (arp_request == 0)) begin
							arp_request <= 2;
							if (arp_list[1] && (arp_mac_1 == rx_src_mac))
								arp_request <= 3;
						end
					end
					if (rx_data_byte_cnt == 32) begin
						if ((rx_src_mac != arp_mac_0) && (rx_src_mac != arp_mac_1)) begin
							arp_mac_1 <= arp_mac_0;
							arp_ip_1 <= arp_ip_0;
							arp_list[1] <= arp_list[0];
							arp_life_time[1] <= arp_life_time[0];
							arp_mac_0 <= rx_src_mac;
							arp_ip_0 <= rx_info_buf[31:0];
							arp_list[0] <= 1'b1;
							arp_life_time[0] <= arp_max_life_time;
						end
						if (rx_src_mac == arp_mac_0) begin
							arp_ip_0 <= rx_info_buf[31:0];
							arp_list[0] <= 1'b1;
							arp_life_time[0] <= arp_max_life_time;
						end
						if (rx_src_mac == arp_mac_1) begin
							arp_ip_1 <= rx_info_buf[31:0];
							arp_list[1] <= 1'b1;
							arp_life_time[1] <= arp_max_life_time;
						end
					end
					if (rx_data_byte_cnt == 42) begin
						if ((rx_info_buf[31:0] == ip_adr) && (arp_request >= 2))
							arp_request <= arp_request + 3'd2;
						else
							arp_request <= 0;
					end
				end
			endcase
			if (rx_data_rdy == 1'b0)
				rx_data_byte_cnt <= 0;
			if (rx_fin)
				ethernet_resolve_status <= 0;
		end
	reg read_head;
	reg read_data;
	always @(*) begin
		read_head <= rx_head_rdy_i && rx_head_av_o;
		read_data <= rx_data_rdy_i && rx_data_av_o;
	end
	always @(posedge clk50m or negedge phy_rdy)
		if (phy_rdy == 1'b0) begin
			rx_head_fifo_tail <= 0;
			rx_data_fifo_tail <= 0;
			rx_head_av_o <= 1'b0;
			rx_data_av_o <= 1'b0;
		end
		else begin
			rx_head_av_o <= rx_head_fifo_head != rx_head_fifo_tail;
			if (read_head)
				rx_head_av_o <= rx_head_fifo_head != ((rx_head_fifo_tail + 1) % 128);
			if (read_head)
				rx_head_fifo_tail <= (rx_head_fifo_tail + 1) % 16'd128;
			rx_head_o <= rx_head_fifo[rx_head_fifo_tail];
			if (read_head)
				rx_head_o <= rx_head_fifo[(rx_head_fifo_tail + 1) % 128];
			rx_data_av_o <= rx_data_fifo_head != rx_data_fifo_tail;
			if (read_data)
				rx_data_av_o <= rx_data_fifo_head != ((rx_data_fifo_tail + 1) % 8192);
			if (read_data)
				rx_data_fifo_tail <= (rx_data_fifo_tail + 1) % 16'd8192;
			rx_data_o <= rx_data_fifo[rx_data_fifo_tail];
			if (read_data)
				rx_data_o <= rx_data_fifo[(rx_data_fifo_tail + 1) % 8192];
		end
	CRC_check crc(
		.clk(clk50m),
		.rst(phy_rdy),
		.data(fifo_d),
		.av(fifo_in),
		.stp(fifo_drop),
		.data_gd(rx_data_gd),
		.rdy(rx_data_rdy),
		.fin(rx_data_fin)
	);
	reg test_tx_en;
	reg [7:0] test_data;
	reg signed [7:0] arp_rpy_stauts;
	reg signed [15:0] arp_rpy_cnt;
	wire tx_bz;
	wire tx_av;
	tx_ct ctct(
		.clk(clk50m),
		.rst(phy_rdy),
		.data(test_data),
		.tx_en(test_tx_en),
		.tx_bz(tx_bz),
		.tx_av(tx_av),
		.p_txd(netrmii_txd),
		.p_txen(netrmii_txen)
	);
	reg [15:0] sendport = 16'h1234;
	wire [47:0] tar_mac_buf;
	wire [31:0] tar_ip_buf;
	reg [15:0] len_buf;
	reg [31:0] tx_head_fifo [63:0];
	reg signed [15:0] tx_head_fifo_head = 0;
	reg signed [15:0] tx_head_fifo_tail = 0;
	wire [31:0] tx_head_data_i_port;
	reg [31:0] tx_head_data_o_port;
	wire tx_head_data_i_en;
	wire [6:0] tx_head_data_i_adr;
	reg [7:0] tx_data_fifo [8191:0];
	reg signed [15:0] tx_data_fifo_head = 0;
	reg signed [15:0] tx_data_fifo_tail = 0;
	wire [7:0] tx_data_data_i_port;
	reg [7:0] tx_data_data_o_port;
	wire tx_data_data_i_en;
	wire [12:0] tx_data_data_i_adr;
	always @(posedge clk50m) begin
		tx_head_data_o_port <= tx_head_fifo[tx_head_fifo_tail];
		tx_data_data_o_port <= tx_data_fifo[tx_data_fifo_tail];
	end
	wire signed [31:0] tick_wt_cnt;
	reg signed [31:0] base_tick = 250000000;
	reg [343:0] data_rom = 344'h63357933346236346576464405cc941500393094a30f0fa8c0100fa8c0616311400040f337290000450008;
	reg arp_lst_refresh;
	reg signed [31:0] arp_refresh_cnt;
	reg [31:0] arp_target_ip;
	reg [47:0] arp_target_mac;
	reg signed [31:0] longdelay;
	always @(posedge clk50m or negedge phy_rdy)
		if (phy_rdy == 1'b0) begin
			arp_refresh_cnt <= 0;
			arp_rpy_stauts <= 0;
			arp_clean <= 2'b00;
			tx_head_fifo_tail <= 0;
			tx_data_fifo_tail <= 0;
		end
		else begin
			arp_rpy_fin <= 1'b0;
			test_tx_en <= 1'b0;
			arp_rpy_cnt <= arp_rpy_cnt + 16'd1;
			arp_clean <= 2'b00;
			case (arp_rpy_stauts)
				0:
					if (arp_request > 3) begin
						arp_rpy_stauts <= 1;
						arp_rpy_cnt <= 0;
					end
					else if (tx_head_fifo_head != tx_head_fifo_tail) begin
						arp_rpy_cnt <= 0;
						arp_target_ip <= tx_head_data_o_port;
						arp_rpy_stauts <= 2;
						longdelay <= 50000;
						if ((tx_head_data_o_port == arp_ip_0) && arp_list[0]) begin
							tx_head_fifo_tail <= (tx_head_fifo_tail + 1) % 16'd64;
							arp_target_mac <= arp_mac_0;
							arp_rpy_stauts <= 3;
						end
						if ((tx_head_data_o_port == arp_ip_1) && arp_list[1]) begin
							tx_head_fifo_tail <= (tx_head_fifo_tail + 1) % 16'd64;
							arp_target_mac <= arp_mac_1;
							arp_rpy_stauts <= 3;
						end
						if (tx_head_data_o_port == 32'hffffffff) begin
							tx_head_fifo_tail <= (tx_head_fifo_tail + 1) % 16'd64;
							arp_target_mac <= 48'hffffffffffff;
							arp_rpy_stauts <= 3;
						end
					end
					else begin
						arp_refresh_cnt <= arp_refresh_cnt + 1;
						if (arp_refresh_cnt >= arp_refresh_interval) begin
							arp_refresh_cnt <= 0;
							if (arp_list != 2'b00) begin
								arp_rpy_stauts <= 2;
								arp_rpy_cnt <= 0;
							end
							if (arp_list == 2'b11) begin
								arp_lst_refresh <= ~arp_lst_refresh;
								arp_clean[~arp_lst_refresh] <= 1'b1;
								if (arp_lst_refresh == 0)
									arp_target_ip <= arp_ip_1;
								else
									arp_target_ip <= arp_ip_0;
							end
							if (arp_list == 2'b10) begin
								arp_clean[1] <= 1'b1;
								arp_target_ip <= arp_ip_1;
							end
							if (arp_list == 2'b01) begin
								arp_clean[0] <= 1'b1;
								arp_target_ip <= arp_ip_0;
							end
						end
					end
				1: begin
					test_tx_en <= 1'b1;
					if (arp_rpy_cnt < 6)
						test_data <= (arp_request == 4 ? arp_mac_0[(5 - arp_rpy_cnt) * 8+:8] : arp_mac_1[(5 - arp_rpy_cnt) * 8+:8]);
					if ((arp_rpy_cnt >= 6) && (arp_rpy_cnt < 12))
						test_data <= mac_adr[(11 - arp_rpy_cnt) * 8+:8];
					if ((arp_rpy_cnt >= 12) && (arp_rpy_cnt < 21))
						test_data <= arp_head[(20 - arp_rpy_cnt) * 8+:8];
					if (arp_rpy_cnt == 21)
						test_data <= 8'h02;
					if ((arp_rpy_cnt >= 22) && (arp_rpy_cnt < 28))
						test_data <= mac_adr[(27 - arp_rpy_cnt) * 8+:8];
					if ((arp_rpy_cnt >= 28) && (arp_rpy_cnt < 32))
						test_data <= ip_adr[(31 - arp_rpy_cnt) * 8+:8];
					if ((arp_rpy_cnt >= 32) && (arp_rpy_cnt < 38))
						test_data <= (arp_request == 4 ? arp_mac_0[(37 - arp_rpy_cnt) * 8+:8] : arp_mac_1[(37 - arp_rpy_cnt) * 8+:8]);
					if ((arp_rpy_cnt >= 38) && (arp_rpy_cnt < 42))
						test_data <= (arp_request == 4 ? arp_ip_0[(41 - arp_rpy_cnt) * 8+:8] : arp_ip_1[(41 - arp_rpy_cnt) * 8+:8]);
					if (arp_rpy_cnt == 42)
						arp_rpy_fin <= 1'b1;
					if (arp_rpy_cnt >= 42)
						test_tx_en <= 1'b0;
					if (arp_rpy_cnt == 46)
						arp_rpy_stauts <= 10;
				end
				2: begin
					test_tx_en <= 1'b1;
					if (arp_rpy_cnt < 6)
						test_data <= 8'hff;
					if ((arp_rpy_cnt >= 6) && (arp_rpy_cnt < 12))
						test_data <= mac_adr[(11 - arp_rpy_cnt) * 8+:8];
					if ((arp_rpy_cnt >= 12) && (arp_rpy_cnt < 21))
						test_data <= arp_head[(20 - arp_rpy_cnt) * 8+:8];
					if (arp_rpy_cnt == 21)
						test_data <= 8'h01;
					if ((arp_rpy_cnt >= 22) && (arp_rpy_cnt < 28))
						test_data <= mac_adr[(27 - arp_rpy_cnt) * 8+:8];
					if ((arp_rpy_cnt >= 28) && (arp_rpy_cnt < 32))
						test_data <= ip_adr[(31 - arp_rpy_cnt) * 8+:8];
					if ((arp_rpy_cnt >= 32) && (arp_rpy_cnt < 38))
						test_data <= 8'h00;
					if ((arp_rpy_cnt >= 38) && (arp_rpy_cnt < 42))
						test_data <= arp_target_ip[(41 - arp_rpy_cnt) * 8+:8];
					if (arp_rpy_cnt == 42)
						arp_rpy_fin <= 1'b1;
					if (arp_rpy_cnt >= 42)
						test_tx_en <= 1'b0;
					if (arp_rpy_cnt == 46)
						arp_rpy_stauts <= 10;
				end
				3: begin
					if (arp_rpy_cnt == 1) begin
						tx_head_fifo_tail <= (tx_head_fifo_tail + 1) % 16'd64;
						len_buf <= tx_head_data_o_port[15:0];
					end
					test_tx_en <= 1'b1;
					if (arp_rpy_cnt < 6)
						test_data <= arp_target_mac[(5 - arp_rpy_cnt) * 8+:8];
					if ((arp_rpy_cnt >= 6) && (arp_rpy_cnt < 12))
						test_data <= mac_adr[(11 - arp_rpy_cnt) * 8+:8];
					if ((arp_rpy_cnt >= 12) && (arp_rpy_cnt < len_buf))
						test_data <= tx_data_data_o_port;
					if ((arp_rpy_cnt >= 11) && (arp_rpy_cnt < (len_buf - 1)))
						tx_data_fifo_tail <= (tx_data_fifo_tail + 1) % 16'd8192;
					if (arp_rpy_cnt == (len_buf - 1))
						arp_rpy_stauts <= 10;
				end
				10: begin
					if (longdelay)
						longdelay <= longdelay - 1;
					if ((tx_bz == 1'b0) && (longdelay == 0))
						arp_rpy_stauts <= 0;
				end
			endcase
		end
	wire [31:0] ob_head_o;
	wire [7:0] ob_data_o;
	wire ob_head_en;
	wire ob_data_en;
	wire ob_fin;
	wire ob_busy;
	wire ob_full;
	reg signed [15:0] head_cnt;
	reg signed [15:0] data_cnt;
	udp_generator #(.ip_adr(ip_adr)) udp_gen(
		.clk(clk50m),
		.rst(phy_rdy),
		.data(tx_data_i),
		.tx_en(tx_data_av_i),
		.req(tx_req_i),
		.ip_adr_i(tx_ip_i),
		.src_port(tx_src_port_i),
		.dst_port(tx_dst_port_i),
		.head_o(ob_head_o),
		.data_o(ob_data_o),
		.head_en(ob_head_en),
		.data_en(ob_data_en),
		.fin(ob_fin),
		.busy(ob_busy),
		.full(ob_full)
	);
	always @(*) begin
		tx_req_rdy_o <= ~ob_busy;
		tx_data_rdy_o <= ~ob_full;
	end
	always @(posedge clk50m or negedge phy_rdy)
		if (phy_rdy == 0) begin
			head_cnt <= 0;
			data_cnt <= 0;
			tx_data_fifo_head <= 0;
			tx_head_fifo_head <= 0;
		end
		else begin
			if (ob_head_en)
				head_cnt <= head_cnt + 16'd1;
			if (ob_data_en)
				data_cnt <= data_cnt + 16'd1;
			if (ob_fin) begin
				head_cnt <= 0;
				data_cnt <= 0;
				tx_data_fifo_head <= (tx_data_fifo_head + data_cnt) % 16'd8192;
				tx_head_fifo_head <= (tx_head_fifo_head + head_cnt) % 16'd64;
			end
			if (ob_data_en)
				tx_data_fifo[(tx_data_fifo_head + data_cnt) % 8192] <= ob_data_o;
			if (ob_head_en)
				tx_head_fifo[(tx_head_fifo_head + head_cnt) % 64] <= ob_head_o;
		end
endmodule
module SMI_ct (
	clk,
	rst,
	rw,
	trg,
	phy_adr,
	reg_adr,
	data,
	ready,
	ack,
	smi_data,
	mdio
);
	input clk;
	input rst;
	input rw;
	input trg;
	input [4:0] phy_adr;
	input [4:0] reg_adr;
	input [15:0] data;
	output reg ready;
	output reg ack;
	output reg [15:0] smi_data;
	inout wire mdio;
	reg signed [7:0] ct;
	reg rmdio;
	reg [31:0] tx_data;
	reg [15:0] rx_data;
	assign mdio = (rmdio ? 1'bz : 1'b0);
	always @(*) smi_data <= rx_data;
	always @(posedge clk or negedge rst)
		if (rst == 1'b0) begin
			ct <= 0;
			ready <= 1'b0;
			ack <= 1'b0;
			rmdio <= 1'b1;
		end
		else begin
			ct <= ct + 8'd1;
			if ((ct == 0) && (trg == 1'b0))
				ct <= 0;
			if ((ct == 0) && (trg == 1'b1)) begin
				ready <= 1'b0;
				ack <= 1'b0;
			end
			if (ct == 64)
				ready <= 1'b1;
			if ((trg == 1'b1) && (ready == 1'b1))
				ready <= 1'b0;
			rmdio <= 1'b1;
			if ((ct == 4) && (trg == 1'b1))
				tx_data <= {2'b01, (rw ? 2'b10 : 2'b01), phy_adr, reg_adr, (rw ? 2'b11 : 2'b10), (rw ? 16'hffff : data)};
			if (ct > 31) begin
				rmdio <= tx_data[31];
				tx_data <= {tx_data[30:0], 1'b1};
			end
			if ((ct == 48) && (mdio == 1'b0))
				ack <= 1'b1;
			if (ct > 48)
				rx_data <= {rx_data[14:0], mdio};
		end
endmodule
module CRC_check (
	clk,
	rst,
	data,
	av,
	stp,
	data_gd,
	rdy,
	fin
);
	input clk;
	input rst;
	input [7:0] data;
	input av;
	input stp;
	output reg [7:0] data_gd;
	output reg rdy;
	output reg fin;
	reg [7:0] buffer [2047:0];
	reg [31:0] crc;
	wire [31:0] crc_next;
	wire [7:0] data_i;
	assign data_i = {data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]};
	assign crc_next[0] = ((crc[24] ^ crc[30]) ^ data_i[0]) ^ data_i[6];
	assign crc_next[1] = ((((((crc[24] ^ crc[25]) ^ crc[30]) ^ crc[31]) ^ data_i[0]) ^ data_i[1]) ^ data_i[6]) ^ data_i[7];
	assign crc_next[2] = ((((((((crc[24] ^ crc[25]) ^ crc[26]) ^ crc[30]) ^ crc[31]) ^ data_i[0]) ^ data_i[1]) ^ data_i[2]) ^ data_i[6]) ^ data_i[7];
	assign crc_next[3] = ((((((crc[25] ^ crc[26]) ^ crc[27]) ^ crc[31]) ^ data_i[1]) ^ data_i[2]) ^ data_i[3]) ^ data_i[7];
	assign crc_next[4] = ((((((((crc[24] ^ crc[26]) ^ crc[27]) ^ crc[28]) ^ crc[30]) ^ data_i[0]) ^ data_i[2]) ^ data_i[3]) ^ data_i[4]) ^ data_i[6];
	assign crc_next[5] = ((((((((((((crc[24] ^ crc[25]) ^ crc[27]) ^ crc[28]) ^ crc[29]) ^ crc[30]) ^ crc[31]) ^ data_i[0]) ^ data_i[1]) ^ data_i[3]) ^ data_i[4]) ^ data_i[5]) ^ data_i[6]) ^ data_i[7];
	assign crc_next[6] = ((((((((((crc[25] ^ crc[26]) ^ crc[28]) ^ crc[29]) ^ crc[30]) ^ crc[31]) ^ data_i[1]) ^ data_i[2]) ^ data_i[4]) ^ data_i[5]) ^ data_i[6]) ^ data_i[7];
	assign crc_next[7] = ((((((((crc[24] ^ crc[26]) ^ crc[27]) ^ crc[29]) ^ crc[31]) ^ data_i[0]) ^ data_i[2]) ^ data_i[3]) ^ data_i[5]) ^ data_i[7];
	assign crc_next[8] = (((((((crc[0] ^ crc[24]) ^ crc[25]) ^ crc[27]) ^ crc[28]) ^ data_i[0]) ^ data_i[1]) ^ data_i[3]) ^ data_i[4];
	assign crc_next[9] = (((((((crc[1] ^ crc[25]) ^ crc[26]) ^ crc[28]) ^ crc[29]) ^ data_i[1]) ^ data_i[2]) ^ data_i[4]) ^ data_i[5];
	assign crc_next[10] = (((((((crc[2] ^ crc[24]) ^ crc[26]) ^ crc[27]) ^ crc[29]) ^ data_i[0]) ^ data_i[2]) ^ data_i[3]) ^ data_i[5];
	assign crc_next[11] = (((((((crc[3] ^ crc[24]) ^ crc[25]) ^ crc[27]) ^ crc[28]) ^ data_i[0]) ^ data_i[1]) ^ data_i[3]) ^ data_i[4];
	assign crc_next[12] = (((((((((((crc[4] ^ crc[24]) ^ crc[25]) ^ crc[26]) ^ crc[28]) ^ crc[29]) ^ crc[30]) ^ data_i[0]) ^ data_i[1]) ^ data_i[2]) ^ data_i[4]) ^ data_i[5]) ^ data_i[6];
	assign crc_next[13] = (((((((((((crc[5] ^ crc[25]) ^ crc[26]) ^ crc[27]) ^ crc[29]) ^ crc[30]) ^ crc[31]) ^ data_i[1]) ^ data_i[2]) ^ data_i[3]) ^ data_i[5]) ^ data_i[6]) ^ data_i[7];
	assign crc_next[14] = (((((((((crc[6] ^ crc[26]) ^ crc[27]) ^ crc[28]) ^ crc[30]) ^ crc[31]) ^ data_i[2]) ^ data_i[3]) ^ data_i[4]) ^ data_i[6]) ^ data_i[7];
	assign crc_next[15] = (((((((crc[7] ^ crc[27]) ^ crc[28]) ^ crc[29]) ^ crc[31]) ^ data_i[3]) ^ data_i[4]) ^ data_i[5]) ^ data_i[7];
	assign crc_next[16] = (((((crc[8] ^ crc[24]) ^ crc[28]) ^ crc[29]) ^ data_i[0]) ^ data_i[4]) ^ data_i[5];
	assign crc_next[17] = (((((crc[9] ^ crc[25]) ^ crc[29]) ^ crc[30]) ^ data_i[1]) ^ data_i[5]) ^ data_i[6];
	assign crc_next[18] = (((((crc[10] ^ crc[26]) ^ crc[30]) ^ crc[31]) ^ data_i[2]) ^ data_i[6]) ^ data_i[7];
	assign crc_next[19] = (((crc[11] ^ crc[27]) ^ crc[31]) ^ data_i[3]) ^ data_i[7];
	assign crc_next[20] = (crc[12] ^ crc[28]) ^ data_i[4];
	assign crc_next[21] = (crc[13] ^ crc[29]) ^ data_i[5];
	assign crc_next[22] = (crc[14] ^ crc[24]) ^ data_i[0];
	assign crc_next[23] = (((((crc[15] ^ crc[24]) ^ crc[25]) ^ crc[30]) ^ data_i[0]) ^ data_i[1]) ^ data_i[6];
	assign crc_next[24] = (((((crc[16] ^ crc[25]) ^ crc[26]) ^ crc[31]) ^ data_i[1]) ^ data_i[2]) ^ data_i[7];
	assign crc_next[25] = (((crc[17] ^ crc[26]) ^ crc[27]) ^ data_i[2]) ^ data_i[3];
	assign crc_next[26] = (((((((crc[18] ^ crc[24]) ^ crc[27]) ^ crc[28]) ^ crc[30]) ^ data_i[0]) ^ data_i[3]) ^ data_i[4]) ^ data_i[6];
	assign crc_next[27] = (((((((crc[19] ^ crc[25]) ^ crc[28]) ^ crc[29]) ^ crc[31]) ^ data_i[1]) ^ data_i[4]) ^ data_i[5]) ^ data_i[7];
	assign crc_next[28] = (((((crc[20] ^ crc[26]) ^ crc[29]) ^ crc[30]) ^ data_i[2]) ^ data_i[5]) ^ data_i[6];
	assign crc_next[29] = (((((crc[21] ^ crc[27]) ^ crc[30]) ^ crc[31]) ^ data_i[3]) ^ data_i[6]) ^ data_i[7];
	assign crc_next[30] = (((crc[22] ^ crc[28]) ^ crc[31]) ^ data_i[4]) ^ data_i[7];
	assign crc_next[31] = (crc[23] ^ crc[29]) ^ data_i[5];
	reg signed [15:0] begin_ptr;
	reg signed [15:0] end_ptr;
	reg sendout;
	reg [7:0] bdata_gd;
	reg brdy;
	reg bfin;
	always @(posedge clk or negedge rst)
		if (rst == 1'b0) begin
			begin_ptr <= 0;
			end_ptr <= 0;
			rdy <= 1'b0;
			fin <= 1'b0;
			brdy <= 1'b0;
			bfin <= 1'b0;
			sendout <= 1'b0;
			crc <= 32'hffffffff;
		end
		else begin
			data_gd <= bdata_gd;
			rdy <= brdy;
			fin <= bfin;
			bdata_gd <= buffer[begin_ptr];
			brdy <= 1'b0;
			bfin <= 1'b0;
			if (sendout) begin
				brdy <= 1'b1;
				if (begin_ptr == end_ptr) begin
					sendout <= 1'b0;
					bfin <= 1'b1;
				end
				else begin
					begin_ptr <= begin_ptr + 16'd1;
					if (begin_ptr == 2047)
						begin_ptr <= 0;
				end
			end
			if (stp) begin
				if (crc == 32'hc704dd7b) begin
					sendout <= 1'b1;
					end_ptr <= (end_ptr + 16'd2043) % 16'd2048;
				end
				else
					begin_ptr <= end_ptr;
				crc <= 32'hffffffff;
			end
			else if (av) begin
				buffer[end_ptr] <= data;
				end_ptr <= end_ptr + 16'd1;
				if (end_ptr == 2047)
					end_ptr <= 0;
				crc <= crc_next;
			end
		end
endmodule
module tx_ct (
	clk,
	rst,
	data,
	tx_en,
	tx_av,
	tx_bz,
	p_txd,
	p_txen
);
	input clk;
	input rst;
	input [7:0] data;
	input tx_en;
	output reg tx_av;
	output reg tx_bz;
	output reg [1:0] p_txd;
	output reg p_txen;
	reg [7:0] buffer [2047:0];
	reg signed [15:0] begin_ptr;
	reg signed [15:0] end_ptr;
	reg [7:0] buffer_out;
	reg signed [7:0] send_status;
	reg signed [7:0] tick;
	reg signed [15:0] send_cnt;
	reg int_en;
	reg [31:0] crc;
	wire [31:0] crc_next;
	reg crc_ct;
	reg [7:0] crc_in;
	wire [7:0] data_i;
	assign data_i = {crc_in[0], crc_in[1], crc_in[2], crc_in[3], crc_in[4], crc_in[5], crc_in[6], crc_in[7]};
	assign crc_next[0] = ((crc[24] ^ crc[30]) ^ data_i[0]) ^ data_i[6];
	assign crc_next[1] = ((((((crc[24] ^ crc[25]) ^ crc[30]) ^ crc[31]) ^ data_i[0]) ^ data_i[1]) ^ data_i[6]) ^ data_i[7];
	assign crc_next[2] = ((((((((crc[24] ^ crc[25]) ^ crc[26]) ^ crc[30]) ^ crc[31]) ^ data_i[0]) ^ data_i[1]) ^ data_i[2]) ^ data_i[6]) ^ data_i[7];
	assign crc_next[3] = ((((((crc[25] ^ crc[26]) ^ crc[27]) ^ crc[31]) ^ data_i[1]) ^ data_i[2]) ^ data_i[3]) ^ data_i[7];
	assign crc_next[4] = ((((((((crc[24] ^ crc[26]) ^ crc[27]) ^ crc[28]) ^ crc[30]) ^ data_i[0]) ^ data_i[2]) ^ data_i[3]) ^ data_i[4]) ^ data_i[6];
	assign crc_next[5] = ((((((((((((crc[24] ^ crc[25]) ^ crc[27]) ^ crc[28]) ^ crc[29]) ^ crc[30]) ^ crc[31]) ^ data_i[0]) ^ data_i[1]) ^ data_i[3]) ^ data_i[4]) ^ data_i[5]) ^ data_i[6]) ^ data_i[7];
	assign crc_next[6] = ((((((((((crc[25] ^ crc[26]) ^ crc[28]) ^ crc[29]) ^ crc[30]) ^ crc[31]) ^ data_i[1]) ^ data_i[2]) ^ data_i[4]) ^ data_i[5]) ^ data_i[6]) ^ data_i[7];
	assign crc_next[7] = ((((((((crc[24] ^ crc[26]) ^ crc[27]) ^ crc[29]) ^ crc[31]) ^ data_i[0]) ^ data_i[2]) ^ data_i[3]) ^ data_i[5]) ^ data_i[7];
	assign crc_next[8] = (((((((crc[0] ^ crc[24]) ^ crc[25]) ^ crc[27]) ^ crc[28]) ^ data_i[0]) ^ data_i[1]) ^ data_i[3]) ^ data_i[4];
	assign crc_next[9] = (((((((crc[1] ^ crc[25]) ^ crc[26]) ^ crc[28]) ^ crc[29]) ^ data_i[1]) ^ data_i[2]) ^ data_i[4]) ^ data_i[5];
	assign crc_next[10] = (((((((crc[2] ^ crc[24]) ^ crc[26]) ^ crc[27]) ^ crc[29]) ^ data_i[0]) ^ data_i[2]) ^ data_i[3]) ^ data_i[5];
	assign crc_next[11] = (((((((crc[3] ^ crc[24]) ^ crc[25]) ^ crc[27]) ^ crc[28]) ^ data_i[0]) ^ data_i[1]) ^ data_i[3]) ^ data_i[4];
	assign crc_next[12] = (((((((((((crc[4] ^ crc[24]) ^ crc[25]) ^ crc[26]) ^ crc[28]) ^ crc[29]) ^ crc[30]) ^ data_i[0]) ^ data_i[1]) ^ data_i[2]) ^ data_i[4]) ^ data_i[5]) ^ data_i[6];
	assign crc_next[13] = (((((((((((crc[5] ^ crc[25]) ^ crc[26]) ^ crc[27]) ^ crc[29]) ^ crc[30]) ^ crc[31]) ^ data_i[1]) ^ data_i[2]) ^ data_i[3]) ^ data_i[5]) ^ data_i[6]) ^ data_i[7];
	assign crc_next[14] = (((((((((crc[6] ^ crc[26]) ^ crc[27]) ^ crc[28]) ^ crc[30]) ^ crc[31]) ^ data_i[2]) ^ data_i[3]) ^ data_i[4]) ^ data_i[6]) ^ data_i[7];
	assign crc_next[15] = (((((((crc[7] ^ crc[27]) ^ crc[28]) ^ crc[29]) ^ crc[31]) ^ data_i[3]) ^ data_i[4]) ^ data_i[5]) ^ data_i[7];
	assign crc_next[16] = (((((crc[8] ^ crc[24]) ^ crc[28]) ^ crc[29]) ^ data_i[0]) ^ data_i[4]) ^ data_i[5];
	assign crc_next[17] = (((((crc[9] ^ crc[25]) ^ crc[29]) ^ crc[30]) ^ data_i[1]) ^ data_i[5]) ^ data_i[6];
	assign crc_next[18] = (((((crc[10] ^ crc[26]) ^ crc[30]) ^ crc[31]) ^ data_i[2]) ^ data_i[6]) ^ data_i[7];
	assign crc_next[19] = (((crc[11] ^ crc[27]) ^ crc[31]) ^ data_i[3]) ^ data_i[7];
	assign crc_next[20] = (crc[12] ^ crc[28]) ^ data_i[4];
	assign crc_next[21] = (crc[13] ^ crc[29]) ^ data_i[5];
	assign crc_next[22] = (crc[14] ^ crc[24]) ^ data_i[0];
	assign crc_next[23] = (((((crc[15] ^ crc[24]) ^ crc[25]) ^ crc[30]) ^ data_i[0]) ^ data_i[1]) ^ data_i[6];
	assign crc_next[24] = (((((crc[16] ^ crc[25]) ^ crc[26]) ^ crc[31]) ^ data_i[1]) ^ data_i[2]) ^ data_i[7];
	assign crc_next[25] = (((crc[17] ^ crc[26]) ^ crc[27]) ^ data_i[2]) ^ data_i[3];
	assign crc_next[26] = (((((((crc[18] ^ crc[24]) ^ crc[27]) ^ crc[28]) ^ crc[30]) ^ data_i[0]) ^ data_i[3]) ^ data_i[4]) ^ data_i[6];
	assign crc_next[27] = (((((((crc[19] ^ crc[25]) ^ crc[28]) ^ crc[29]) ^ crc[31]) ^ data_i[1]) ^ data_i[4]) ^ data_i[5]) ^ data_i[7];
	assign crc_next[28] = (((((crc[20] ^ crc[26]) ^ crc[29]) ^ crc[30]) ^ data_i[2]) ^ data_i[5]) ^ data_i[6];
	assign crc_next[29] = (((((crc[21] ^ crc[27]) ^ crc[30]) ^ crc[31]) ^ data_i[3]) ^ data_i[6]) ^ data_i[7];
	assign crc_next[30] = (((crc[22] ^ crc[28]) ^ crc[31]) ^ data_i[4]) ^ data_i[7];
	assign crc_next[31] = (crc[23] ^ crc[29]) ^ data_i[5];
	reg [7:0] crc_buffer;
	always @(*) begin
		tx_av <= (((end_ptr + 2047) - begin_ptr) % 2048) > 63;
		int_en <= tx_av && tx_en;
		if (crc_ct)
			crc_in <= buffer_out;
		else
			crc_in <= 8'b00000000;
		tx_bz <= send_status != 0;
	end
	always @(posedge clk or negedge rst)
		if (rst == 1'b0) begin
			begin_ptr <= 0;
			end_ptr <= 0;
			send_status <= 0;
		end
		else begin
			p_txen <= 1'b0;
			tick <= tick + 8'd1;
			if (tick == 3)
				tick <= 0;
			if (int_en) begin
				buffer[begin_ptr] <= data;
				begin_ptr <= begin_ptr + 16'd1;
				if (begin_ptr == 2047)
					begin_ptr <= 0;
			end
			case (send_status)
				0:
					if (begin_ptr != end_ptr) begin
						send_status <= 1;
						send_cnt <= 0;
						crc <= 32'hffffffff;
					end
				1: begin
					send_cnt <= send_cnt + 8'd1;
					p_txd <= 2'b01;
					p_txen <= 1'b1;
					if (send_cnt == 31) begin
						p_txd <= 2'b11;
						send_status <= 2;
						send_cnt <= 0;
						tick <= 0;
						crc_ct <= 1'b1;
					end
				end
				2: begin
					if (tick == 0)
						crc <= crc_next;
					buffer_out <= {2'bxx, buffer_out[7:2]};
					p_txd <= buffer_out[1:0];
					p_txen <= 1'b1;
					if (tick == 2) begin
						end_ptr <= end_ptr + 16'd1;
						if (end_ptr == 2047)
							end_ptr <= 0;
					end
					if ((tick == 3) && (send_cnt < 96))
						send_cnt <= send_cnt + 8'd1;
					if ((tick == 3) && (((end_ptr - begin_ptr) % 2048) == 0)) begin
						crc_ct <= 1'b0;
						if (send_cnt < 63)
							send_status <= 3;
						else begin
							send_status <= 4;
							send_cnt <= 0;
							crc_buffer <= ~{crc[24], crc[25], crc[26], crc[27], crc[28], crc[29], crc[30], crc[31]};
							crc <= {crc[23:0], 8'hxx};
						end
					end
				end
				3: begin
					if (tick == 0)
						crc <= crc_next;
					p_txd <= 0;
					p_txen <= 1'b1;
					if (tick == 3) begin
						send_cnt <= send_cnt + 8'd1;
						if (send_cnt == 63) begin
							send_status <= 4;
							send_cnt <= 0;
							crc_buffer <= ~{crc[24], crc[25], crc[26], crc[27], crc[28], crc[29], crc[30], crc[31]};
							crc <= {crc[23:0], 8'hxx};
						end
					end
				end
				4: begin
					p_txd <= crc_buffer[1:0];
					crc_buffer <= {2'bxx, crc_buffer[7:2]};
					p_txen <= 1'b1;
					if (tick == 3) begin
						crc_buffer <= ~{crc[24], crc[25], crc[26], crc[27], crc[28], crc[29], crc[30], crc[31]};
						crc <= {crc[23:0], 8'hxx};
						send_cnt <= send_cnt + 8'd1;
						if (send_cnt == 3) begin
							send_status <= 5;
							send_cnt <= 0;
						end
					end
				end
				5: begin
					p_txd <= 2'bxx;
					p_txen <= 1'b0;
					if (tick == 3)
						send_status <= 0;
				end
			endcase
			if (tick == 3)
				buffer_out <= buffer[end_ptr];
		end
endmodule
module udp_generator (
	clk,
	rst,
	data,
	tx_en,
	req,
	ip_adr_i,
	src_port,
	dst_port,
	head_o,
	data_o,
	head_en,
	data_en,
	fin,
	busy,
	full
);
	parameter [31:0] ip_adr = 32'd0;
	parameter [31:0] udp_head_p1 = 32'h08004500;
	parameter [31:0] udp_head_p2 = 32'h40004011;

	input clk;
	input rst;
	input [7:0] data;
	input tx_en;
	input req;
	input [31:0] ip_adr_i;
	input [15:0] src_port;
	input [15:0] dst_port;
	output reg [31:0] head_o;
	output reg [7:0] data_o;
	output reg head_en;
	output reg data_en;
	output reg fin;
	output reg busy;
	output reg full;
	reg [7:0] buffer [2047:0];
	reg signed [15:0] begin_ptr;
	reg signed [15:0] end_ptr;
	reg [7:0] buffer_port_i;
	reg [7:0] buffer_port_o;
	reg buffer_wr;
	reg signed [7:0] udp_gen_status;
	reg signed [15:0] udp_gen_cnt;
	reg [17:0] checksum;
	reg [17:0] head_checksum;
	reg [15:0] send_checksum;
	reg [15:0] send_head_checksum;
	reg [7:0] lst_in;
	reg [15:0] sendlen;
	reg [31:0] local_ip;
	reg [31:0] local_src_port;
	reg [31:0] local_dst_port;
	reg [15:0] pack_num;
	reg [15:0] head_len;
	reg [15:0] udp_len;

	always @(*) begin
		head_len <= 16'd28 + sendlen[15:0];
		udp_len <= 16'd8 + sendlen[15:0];
		send_checksum <= 16'hffef - checksum[15:0];
		if (checksum[15:0] > 16'hffef)
			send_checksum <= (16'hffef - 16'd1) - checksum[15:0];
		send_head_checksum <= 16'h0000 - head_checksum[15:0];
	end

	function automatic [17:0] sv2v_cast_18;
		input reg [17:0] inp;
		sv2v_cast_18 = inp;
	endfunction

	always @(posedge clk or negedge rst)
		if (rst == 0) begin
			begin_ptr <= 0;
			end_ptr <= 0;
			head_en <= 1'b0;
			data_en <= 1'b0;
			fin <= 1'b0;
			buffer_wr <= 1'b0;
			udp_gen_status <= 0;
			checksum <= 18'h00000;
			head_checksum <= 18'h00000;
			sendlen <= 0;
			full <= 0;
		end
		else begin
			buffer_wr <= 1'b0;
			if (buffer_wr && !full)
				buffer[end_ptr] <= buffer_port_i;
			buffer_port_o <= buffer[begin_ptr];
			full <= (((end_ptr + 2048) - begin_ptr) % 2048) > 1920;
			head_en <= 1'b0;
			data_en <= 1'b0;
			fin <= 1'b0;
			busy <= (udp_gen_status != 0) || req;
			udp_gen_cnt <= udp_gen_cnt + 16'd1;
			if (tx_en) begin
				lst_in <= data;
				buffer_wr <= 1'b1;
				buffer_port_i <= data;
				end_ptr <= (end_ptr + 1) % 16'd2048;
				sendlen <= sendlen + 16'd1;
				if (sendlen[0] == 1'b1)
					checksum <= ({2'b00, checksum[15:0]} + {lst_in, data}) + {16'd0, checksum[17:16]};
			end
			case (udp_gen_status)
				0:
					if (req) begin
						udp_gen_status <= 1;
						udp_gen_cnt <= 0;
						local_ip <= ip_adr_i;
						local_src_port <= src_port;
						local_dst_port <= dst_port;
						pack_num <= pack_num + 16'd1;
						head_checksum <= 18'h0c512;
					end
				1: begin
					if (udp_gen_cnt == 0)
						checksum <= ((({2'b00, checksum[15:0]} + {16'd0, checksum[17:16]}) + {2'b00, sendlen}) + {2'b00, sendlen}) + 18'h00011;
					if (udp_gen_cnt == 1)
						checksum <= (({2'b00, checksum[15:0]} + {16'd0, checksum[17:16]}) + {2'b00, ip_adr[31:16]}) + {2'b00, ip_adr[15:0]};
					if (udp_gen_cnt == 2)
						checksum <= (({2'b00, checksum[15:0]} + {16'd0, checksum[17:16]}) + {2'b00, local_ip[31:16]}) + {2'b00, local_ip[15:0]};
					if (udp_gen_cnt == 3)
						checksum <= sv2v_cast_18((({2'b00, checksum[15:0]} + {16'd0, checksum[17:16]}) + {2'b00, local_src_port}) + {2'b00, local_dst_port});
					if (udp_gen_cnt == 4) begin
						if (sendlen[0] == 1'b1)
							checksum <= ({2'b00, checksum[15:0]} + {16'd0, checksum[17:16]}) + {lst_in, 8'd0};
					end
					if (udp_gen_cnt == 5)
						checksum <= {2'b00, checksum[15:0]} + {16'd0, checksum[17:16]};
					if (udp_gen_cnt == 6)
						checksum <= {2'b00, checksum[15:0]} + {16'd0, checksum[17:16]};
					if (udp_gen_cnt == 7)
						checksum <= {2'b00, checksum[15:0]} + {16'd0, checksum[17:16]};
					if (udp_gen_cnt == 0)
						head_checksum <= ({2'b00, head_checksum[15:0]} + {16'd0, head_checksum[17:16]}) + {2'b00, pack_num};
					if (udp_gen_cnt == 1)
						head_checksum <= ({2'b00, head_checksum[15:0]} + {16'd0, head_checksum[17:16]}) + {2'b00, head_len};
					if (udp_gen_cnt == 2)
						head_checksum <= (({2'b00, head_checksum[15:0]} + {16'd0, head_checksum[17:16]}) + {2'b00, local_ip[31:16]}) + {2'b00, local_ip[15:0]};
					if (udp_gen_cnt == 3)
						head_checksum <= (({2'b00, head_checksum[15:0]} + {16'd0, head_checksum[17:16]}) + {2'b00, ip_adr[31:16]}) + {2'b00, ip_adr[15:0]};
					if (udp_gen_cnt == 4)
						head_checksum <= {2'b00, head_checksum[15:0]} + {16'd0, head_checksum[17:16]};
					if (udp_gen_cnt == 5)
						head_checksum <= {2'b00, head_checksum[15:0]} + {16'd0, head_checksum[17:16]};
					if (udp_gen_cnt == 6)
						head_checksum <= {2'b00, head_checksum[15:0]} + {16'd0, head_checksum[17:16]};
					if (udp_gen_cnt == 7)
						head_checksum <= {2'b00, head_checksum[15:0]} + {16'd0, head_checksum[17:16]};
					if (udp_gen_cnt == 0) begin
						head_en <= 1'b1;
						head_o <= local_ip;
					end
					if (udp_gen_cnt == 1) begin
						head_en <= 1'b1;
						head_o <= head_len + 14;
					end
					data_en <= 1'b1;
					if (udp_gen_cnt < 4)
						data_o <= udp_head_p1[(3 - udp_gen_cnt) * 8+:8];
					if ((udp_gen_cnt >= 4) && (udp_gen_cnt < 6))
						data_o <= head_len[(5 - udp_gen_cnt) * 8+:8];
					if ((udp_gen_cnt >= 6) && (udp_gen_cnt < 8))
						data_o <= pack_num[(7 - udp_gen_cnt) * 8+:8];
					if ((udp_gen_cnt >= 8) && (udp_gen_cnt < 12))
						data_o <= udp_head_p2[(11 - udp_gen_cnt) * 8+:8];
					if ((udp_gen_cnt >= 12) && (udp_gen_cnt < 14))
						data_o <= send_head_checksum[(13 - udp_gen_cnt) * 8+:8];
					if ((udp_gen_cnt >= 14) && (udp_gen_cnt < 18))
						data_o <= ip_adr[(17 - udp_gen_cnt) * 8+:8];
					if ((udp_gen_cnt >= 18) && (udp_gen_cnt < 22))
						data_o <= local_ip[(21 - udp_gen_cnt) * 8+:8];
					if ((udp_gen_cnt >= 22) && (udp_gen_cnt < 24))
						data_o <= local_src_port[(23 - udp_gen_cnt) * 8+:8];
					if ((udp_gen_cnt >= 24) && (udp_gen_cnt < 26))
						data_o <= local_dst_port[(25 - udp_gen_cnt) * 8+:8];
					if ((udp_gen_cnt >= 26) && (udp_gen_cnt < 28))
						data_o <= udp_len[(27 - udp_gen_cnt) * 8+:8];
					if ((udp_gen_cnt >= 28) && (udp_gen_cnt < 30))
						data_o <= send_checksum[(29 - udp_gen_cnt) * 8+:8];
					if (udp_gen_cnt >= 30)
						data_o <= buffer_port_o;
					if ((udp_gen_cnt >= 28) && (udp_gen_cnt < (28 + sendlen)))
						begin_ptr <= (begin_ptr + 1) % 16'd2048;
					if (udp_gen_cnt == (29 + sendlen)) begin
						udp_gen_status <= 2;
						sendlen <= 0;
					end
				end
				2: begin
					fin <= 1'b1;
					udp_gen_status <= 0;
					checksum <= 18'h00000;
				end
			endcase
		end
endmodule
