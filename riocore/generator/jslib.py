import os
import json
import stat
from riocore.generator.cbase import cbase

riocore_path = os.path.dirname(os.path.dirname(__file__))


class jslib:
    def __init__(self, project):
        self.project = project
        self.mqtt_path = os.path.join(self.project.config["output_path"], "JSLIB")
        os.makedirs(self.mqtt_path, exist_ok=True)

        self.iface_in = []
        self.iface_out = []
        output_pos = self.project.buffer_size

        variable_name = "header_rx"
        size = 32
        for bit_num in range(0, size, 8):
            output_pos -= 8
        self.iface_out.append(["RX_HEADER", size])
        self.iface_in.append(["TX_HEADER", size])
        self.iface_in.append(["TITMESTAMP", size])

        rx_dict = {}
        tx_dict = {}

        if self.project.multiplexed_input:
            variable_name = "MULTIPLEXED_INPUT_VALUE"
            size = self.project.multiplexed_input_size
            self.iface_in.append([variable_name, size])
            variable_name = "MULTIPLEXED_INPUT_ID"
            size = 8
            self.iface_in.append([variable_name, size])

        if self.project.multiplexed_output:
            variable_name = "MULTIPLEXED_OUTPUT_VALUE"
            size = self.project.multiplexed_output_size
            for bit_num in range(0, size, 8):
                output_pos -= 8
            self.iface_out.append([variable_name, size])
            variable_name = "MULTIPLEXED_OUTPUT_ID"
            size = 8
            for bit_num in range(0, size, 8):
                output_pos -= 8
            self.iface_out.append([variable_name, size])

        for size, plugin_instance, data_name, data_config in self.project.get_interface_data():
            multiplexed = data_config.get("multiplexed", False)
            if multiplexed:
                continue
            variable_name = data_config["variable"]

            if data_config["direction"] == "input":
                if not data_config.get("expansion"):
                    self.iface_in.append([variable_name, size])

                    if plugin_instance.instances_name not in rx_dict:
                        rx_dict[plugin_instance.instances_name] = {}
                    rx_dict[plugin_instance.instances_name][data_name] = variable_name

            elif data_config["direction"] == "output":
                if not data_config.get("expansion"):
                    if size >= 8:
                        for bit_num in range(0, size, 8):
                            output_pos -= 8
                    elif size > 1:
                        output_pos -= size
                    else:
                        output_pos -= 1
                    self.iface_out.append([variable_name, size])

                    if plugin_instance.instances_name not in tx_dict:
                        tx_dict[plugin_instance.instances_name] = {}
                    tx_dict[plugin_instance.instances_name][data_name] = variable_name

        output = ["#!/usr/bin/env node"]

        output.append("const dgram = require('node:dgram');")
        output.append("const { Buffer } = require('node:buffer');")
        output.append("const server = dgram.createSocket('udp4');")
        output.append("")
        output.append("server.on('error', (err) => {")
        output.append("    console.error(`server error:\n${err.stack}`);")
        output.append("    server.close();")
        output.append("});")
        output.append("")
        output.append("server.on('listening', () => {")
        output.append("    const address = server.address();")
        output.append("    console.log(`server listening ${address.address}:${address.port}`);")
        output.append("});")
        output.append("")

        output.append("function get_rx(data) {")
        output.append("    // read buffer")
        pos = 0
        for data in self.iface_in:
            name = data[0]
            size = data[1]
            byte_pos = pos // 8
            bit_offset = pos - (byte_pos * 8)
            if size in {8}:
                func = "readUInt8"
                output.append(f"    {name} = data.{func}({byte_pos});")
            elif size in {16, 32, 64}:
                func = f"readInt{size}LE"
                output.append(f"    {name} = data.{func}({byte_pos});")
            else:
                output.append(f"    if ((data[{byte_pos}] & (1<<{7 - bit_offset})) != 0) {{")
                output.append(f"        {name} = 1;")
                output.append("    } else {")
                output.append(f"        {name} = 0;")
                output.append("    }")
            pos += size
        output.append("")

        output.append("    // build dict")
        output.append("    rio_rx = {};")
        for plugin, values in rx_dict.items():
            output.append(f'    rio_rx["{plugin}"] = {{}};')
        for plugin, values in rx_dict.items():
            for key, value in values.items():
                output.append(f'    rio_rx["{plugin}"]["{key}"] = {value};')
        output.append("    return rio_rx;")
        output.append("}")
        output.append("")

        output.append("server.on('message', (msg, rinfo) => {")
        output.append("    console.log(`server got: ${msg} from ${rinfo.address}:${rinfo.port}`);")
        output.append("    data = msg.slice()")
        output.append("    console.log(data);")
        output.append("    rio_rx = get_rx(data);")
        for plugin, values in rx_dict.items():
            for key, value in values.items():
                output.append(f'    console.log("{plugin}.{key} = ", rio_rx["{plugin}"]["{key}"]);')
        output.append("});")
        output.append("")

        output.append("server.bind(2391);")
        output.append('const message = Buffer.from("7469727700000000000000000000000000000000000000000000000000000", "hex")')
        output.append("server.send(message, 2390, '127.0.0.1', (err) => {")
        output.append("    //server.close();")
        output.append("});")
        output.append("")

        open(os.path.join(self.mqtt_path, "rio.js"), "w").write("\n".join(output))
