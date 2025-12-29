import os
from .base import generator_base


class jslib(generator_base):
    def __init__(self, project, instance):
        self.project = project
        self.instance = instance
        self.prefix = instance.hal_prefix
        self.mqtt_path = os.path.join(self.project.config["output_path"], "JSLIB", instance.instances_name)
        os.makedirs(self.mqtt_path, exist_ok=True)

        self.iface_in = []
        self.iface_out = []
        self.calc_buffersize(self.project)
        input_pos = self.buffer_size_in

        variable_name = "header_rx"
        size = 32
        for bit_num in range(0, size, 8):
            input_pos -= 8
        self.iface_out.append(["RX_HEADER", size])
        self.iface_in.append(["TX_HEADER", size])
        self.iface_in.append(["TITMESTAMP", size])

        self.rx_dict = {}
        self.tx_dict = {}

        if self.multiplexed_input:
            variable_name = "MULTIPLEXED_INPUT_VALUE"
            size = self.multiplexed_input_size
            self.iface_in.append([variable_name, size])
            variable_name = "MULTIPLEXED_INPUT_ID"
            size = 8
            self.iface_in.append([variable_name, size])

        if self.multiplexed_output:
            variable_name = "MULTIPLEXED_OUTPUT_VALUE"
            size = self.project.multiplexed_output_size
            for bit_num in range(0, size, 8):
                input_pos -= 8
            self.iface_out.append([variable_name, size])
            variable_name = "MULTIPLEXED_OUTPUT_ID"
            size = 8
            for bit_num in range(0, size, 8):
                input_pos -= 8
            self.iface_out.append([variable_name, size])

        for size, plugin_instance, data_name, data_config in self.get_interface_data(self.project):
            multiplexed = data_config.get("multiplexed", False)
            if multiplexed:
                continue
            variable_name = data_config["variable"]

            if data_config["direction"] == "input":
                if not data_config.get("expansion"):
                    self.iface_in.append([variable_name, size])

                    if plugin_instance.instances_name not in self.rx_dict:
                        self.rx_dict[plugin_instance.instances_name] = {}
                    self.rx_dict[plugin_instance.instances_name][data_name] = variable_name

            elif data_config["direction"] == "output":
                if not data_config.get("expansion"):
                    if size >= 8:
                        for bit_num in range(0, size, 8):
                            input_pos -= 8
                    elif size > 1:
                        input_pos -= size
                    else:
                        input_pos -= 1
                    self.iface_out.append([variable_name, size])

                    if plugin_instance.instances_name not in self.tx_dict:
                        self.tx_dict[plugin_instance.instances_name] = {}
                    self.tx_dict[plugin_instance.instances_name][data_name] = variable_name

        # self.byte_size = self.buffer_size // 8

        self.rio_js()
        self.client_js()

    def rio_js(self):
        output = [""]
        output.append("module.exports = {")
        output.append("  output: {")
        for plugin, values in self.tx_dict.items():
            output.append(f'    "{plugin}": {{')
            for key, value in values.items():
                output.append(f'      "{key}": 0,')
            output.append("    },")
        output.append("  },")
        output.append("")

        output.append("  set_tx: function (rio_tx) {")
        output.append(f"    data = Buffer.alloc({self.buffer_size_out // 8}, 0);")
        output.append('    RX_HEADER = Buffer.from("74697277", "hex").readInt32LE(0);')
        for plugin, values in self.tx_dict.items():
            for key, value in values.items():
                output.append(f'    {value} = rio_tx["{plugin}"]["{key}"];')
        output.append("")
        pos = 0
        for data in self.iface_out:
            name = data[0]
            size = data[1]
            byte_pos = pos // 8
            bit_offset = pos - (byte_pos * 8)
            if size in {8}:
                func = "writeUInt8"
                output.append(f"    data.{func}({name}, {byte_pos});")
            elif size in {16, 32, 64}:
                func = f"writeInt{size}LE"
                output.append(f"    data.{func}({name}, {byte_pos});")
            else:
                output.append(f"    if ({name}) {{")
                output.append(f"        data[{byte_pos}] |= (1<<{7 - bit_offset});")
                output.append("    }")
            pos += size
        output.append("    return data;")
        output.append("  },")
        output.append("")

        output.append("  get_rx: function (data) {")
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

        output.append("    input = {")
        for plugin, values in self.rx_dict.items():
            output.append(f'      "{plugin}": {{')
            for key, value in values.items():
                output.append(f'        "{key}": {value},')
            output.append("      },")
        output.append("    };")
        output.append("")

        output.append("    return input;")
        output.append("  }")
        output.append("};")
        output.append("")

        open(os.path.join(self.mqtt_path, "rio.js"), "w").write("\n".join(output))

    def client_js(self):
        http_support = True

        output = ["#!/usr/bin/env node"]
        output.append("")
        output.append("")
        if http_support:
            output.append("var http = require('http');")
            output.append("var url = require('url');")
            output.append("")
        output.append("const rio = require('./rio');")
        output.append("const dgram = require('node:dgram');")
        output.append("const { Buffer } = require('node:buffer');")
        output.append("")
        if http_support:
            output.append("HTTP_PORT = 8080;")
        output.append("SOURCE_PORT = 2391;")
        output.append("TARGET_PORT = 2390;")
        output.append("TARGET_IP = '127.0.0.1';")
        output.append("")
        if http_support:
            output.append("rio_rx = {};")
            output.append("")
        output.append("const server = dgram.createSocket('udp4');")
        output.append("")
        output.append("server.on('error', (err) => {")
        output.append("    console.error(`server error:\n${err.stack}`);")
        output.append("    server.close();")
        output.append("});")
        output.append("")
        output.append("server.on('listening', () => {")
        output.append("    const address = server.address();")
        if not http_support:
            output.append("    console.log(`server listening ${address.address}:${address.port}`);")
        output.append("});")
        output.append("")

        output.append("server.on('message', (msg, rinfo) => {")
        if not http_support:
            output.append("    console.log(`server got: ${msg} from ${rinfo.address}:${rinfo.port}`);")
        output.append("    data = msg.slice()")
        if not http_support:
            output.append("    console.log(data);")
        output.append("    rio_rx = rio.get_rx(data);")
        if not http_support:
            for plugin, values in self.rx_dict.items():
                for key, value in values.items():
                    output.append(f'    console.log("{plugin}.{key} = ", rio_rx["{plugin}"]["{key}"]);')
        output.append("});")
        output.append("")
        output.append("function send() {")
        if not http_support:
            for plugin, values in self.tx_dict.items():
                for key, value in values.items():
                    output.append(f'    rio.output["{plugin}"]["{key}"] = 0;')
            output.append("")
        output.append("    message = rio.set_tx(rio.output);")
        if not http_support:
            output.append("    console.log(message);")
        output.append("    server.send(message, TARGET_PORT, TARGET_IP, (err) => {")
        if not http_support:
            output.append('        console.log("send ok");')
        output.append("    });")
        output.append("}")
        output.append("")

        output.append("server.bind(SOURCE_PORT);")
        output.append("")

        output.append("var timer = setInterval(function () {")
        output.append("    send();")
        output.append("}, 10);")
        output.append("")

        if http_support:
            output.append("console.log(`http server listening ${HTTP_PORT}`);")
            output.append("")
            for plugin, values in self.tx_dict.items():
                for key, value in values.items():
                    output.append(f'rio.output["{plugin}"]["{key}"] = 0;')
            output.append("")
            output.append("http.createServer(function (req, res) {")
            output.append("    var q = url.parse(req.url, true);")
            output.append('    var filename = "." + q.pathname;')
            output.append("    res.writeHead(200, {'Content-Type': 'text/html'});")
            output.append("")

            for plugin, values in self.tx_dict.items():
                for key, value in values.items():
                    output.append(f'    if ("{plugin}.{key}" in q.query) {{')
                    output.append(f'        rio.output["{plugin}"]["{key}"] = parseInt(q.query["{plugin}.{key}"]);')
                    output.append("    }")
            output.append("")

            output.append("    res.write(\"<form action='/'>\");")
            for plugin, values in self.tx_dict.items():
                for key, value in values.items():
                    output.append(f"    res.write(\"{plugin}.{key}: <input type='text' id='{plugin}.{key}' name='{plugin}.{key}' value='\" + String(rio.output[\"{plugin}\"][\"{key}\"]) + \"'><br/>\");")
            output.append("    res.write(\"  <input type='submit' value='Submit'>\");")
            output.append('    res.write("</form>");')
            output.append("")

            for plugin, values in self.rx_dict.items():
                for key, value in values.items():
                    output.append(f'    res.write("{plugin}.{key} = ");')
                    output.append(f'    res.write(String(rio_rx["{plugin}"]["{key}"]));')
                    output.append('    res.write("<br/>");')
            output.append("")
            output.append("    res.end();")
            output.append("}).listen(HTTP_PORT);")
            output.append("")

        output.append("")

        open(os.path.join(self.mqtt_path, "client.js"), "w").write("\n".join(output))
