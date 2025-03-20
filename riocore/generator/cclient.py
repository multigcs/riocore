import os


def riocore_h(project, folder):
    sysclk_speed = project.config["speed"]
    ip = "192.168.10.194"
    port = 2390
    for plugin_instance in project.plugin_instances:
        if plugin_instance.TYPE == "interface":
            ip = plugin_instance.plugin_setup.get("ip", plugin_instance.option_default("ip", ip))
            port = plugin_instance.plugin_setup.get("port", plugin_instance.option_default("port", port))

    ip = project.config["jdata"].get("ip", ip)
    port = project.config["jdata"].get("port", port)
    dst_port = project.config["jdata"].get("dst_port", port)
    src_port = project.config["jdata"].get("src_port", str(int(port) + 1))

    output = []
    output.append("#include <stdio.h>")
    output.append("#include <unistd.h>")
    output.append("#include <stdint.h>")
    output.append("#include <stdbool.h>")
    output.append("#include <string.h>")
    output.append("#include <time.h>")
    output.append("")
    output.append(f"#define CLOCK_SPEED {sysclk_speed}")
    output.append(f"#define BUFFER_SIZE {project.buffer_size // 8} // {project.buffer_size} bits")
    if port and ip:
        output.append(f'#define UDP_IP "{ip}"')
        output.append(f"#define SRC_PORT {dst_port}")
        output.append(f"#define DST_PORT {src_port}")
        output.append("")

    output.append("void read_rxbuffer(uint8_t *rxBuffer);")
    output.append("void write_txbuffer(uint8_t *txBuffer);")
    output.append("")

    output.append("extern uint8_t rxBuffer[BUFFER_SIZE];")
    output.append("extern uint8_t txBuffer[BUFFER_SIZE];")

    if project.multiplexed_input:
        output.append("extern float MULTIPLEXER_INPUT_VALUE;")
        output.append("extern uint8_t MULTIPLEXER_INPUT_ID;")
    if project.multiplexed_output:
        output.append("extern float MULTIPLEXER_OUTPUT_VALUE;")
        output.append("extern uint8_t MULTIPLEXER_OUTPUT_ID;")

    for plugin_instance in project.plugin_instances:
        for data_name, data_config in plugin_instance.interface_data().items():
            if not data_config.get("expansion"):
                variable_name = data_config["variable"]
                variable_size = data_config["size"]
                variable_bytesize = variable_size // 8
                if plugin_instance.TYPE == "frameio":
                    output.append(f"extern uint8_t {variable_name}[{variable_bytesize}];")
                elif variable_size > 1:
                    variable_size_align = 8
                    for isize in (8, 16, 32, 64):
                        variable_size_align = isize
                        if isize >= variable_size:
                            break
                    output.append(f"extern int{variable_size_align}_t {variable_name};")
                else:
                    output.append(f"extern uint8_t {variable_name};")
    output.append("")

    open(os.path.join(folder, "riocore.h"), "w").write("\n".join(output))


def riocore_c(project, folder):
    output = []
    output.append("")
    output.append("#include <stdio.h>")
    output.append("#include <unistd.h>")
    output.append("#include <stdint.h>")
    output.append("#include <stdbool.h>")
    output.append("#include <string.h>")
    output.append("#include <time.h>")
    output.append("#include <riocore.h>")
    output.append("")

    buffer_size_bytes = project.buffer_size // 8
    buffer_init = ["0"] * buffer_size_bytes
    output.append(f"uint8_t rxBuffer[BUFFER_SIZE] = {{{', '.join(buffer_init)}}};")
    output.append(f"uint8_t txBuffer[BUFFER_SIZE] = {{{', '.join(buffer_init)}}};")

    if project.multiplexed_output:
        output.append("float MULTIPLEXER_INPUT_VALUE;")
        output.append("uint8_t MULTIPLEXER_INPUT_ID;")
    if project.multiplexed_input:
        output.append("float MULTIPLEXER_OUTPUT_VALUE;")
        output.append("uint8_t MULTIPLEXER_OUTPUT_ID;")

    for plugin_instance in project.plugin_instances:
        for data_name, data_config in plugin_instance.interface_data().items():
            if not data_config.get("expansion"):
                variable_name = data_config["variable"]
                variable_size = data_config["size"]
                multiplexed = data_config.get("multiplexed", False)
                variable_bytesize = variable_size // 8
                if plugin_instance.TYPE == "frameio":
                    output.append(f"uint8_t {variable_name}[{variable_bytesize}];")
                elif variable_size > 1:
                    variable_size_align = 8
                    for isize in (8, 16, 32, 64):
                        variable_size_align = isize
                        if isize >= variable_size:
                            break
                    output.append(f"int{variable_size_align}_t {variable_name} = 0;")
                else:
                    output.append(f"uint8_t {variable_name} = 0;")
    output.append("")
    output.append("")

    output.append("// PC -> MC")
    output.append("void read_rxbuffer(uint8_t *rxBuffer) {")
    input_pos = project.buffer_size

    variable_size = 32
    byte_start, byte_size, bit_offset = project.get_bype_pos(input_pos, variable_size)
    byte_start = project.buffer_bytes - 1 - byte_start
    output.append(f"    // memcpy(&header, &rxBuffer[{byte_start - (byte_size - 1)}], {byte_size}) // {input_pos};")
    input_pos -= variable_size

    if project.multiplexed_output:
        variable_size = project.multiplexed_output_size
        byte_start, byte_size, bit_offset = project.get_bype_pos(input_pos, variable_size)
        byte_start = project.buffer_bytes - 1 - byte_start
        output.append(f"    memcpy(&MULTIPLEXER_OUTPUT_VALUE, &rxBuffer[{byte_start - (byte_size - 1)}], {byte_size});")
        input_pos -= variable_size
        variable_size = 8
        byte_start, byte_size, bit_offset = project.get_bype_pos(input_pos, variable_size)
        byte_start = project.buffer_bytes - 1 - byte_start
        output.append(f"    memcpy(&MULTIPLEXER_OUTPUT_ID, &rxBuffer[{byte_start - (byte_size - 1)}], {byte_size});")
        input_pos -= variable_size

    for size, plugin_instance, data_name, data_config in project.get_interface_data():
        multiplexed = data_config.get("multiplexed", False)
        expansion = data_config.get("expansion", False)
        if multiplexed or expansion:
            continue
        variable_name = data_config["variable"]
        variable_size = data_config["size"]
        if data_config["direction"] == "output":
            byte_start, byte_size, bit_offset = project.get_bype_pos(input_pos, variable_size)
            byte_start = project.buffer_bytes - 1 - byte_start
            if variable_size > 1:
                output.append(f"    memcpy(&{variable_name}, &rxBuffer[{byte_start - (byte_size - 1)}], {byte_size}); // {input_pos}")
            else:
                output.append(f"    if ((rxBuffer[{byte_start}] & (1<<{bit_offset})) == 0) {{")
                output.append(f"        {variable_name} = 0;")
                output.append("    } else {")
                output.append(f"        {variable_name} = 1;")
                output.append("    }")
            input_pos -= variable_size

    output.append("}")
    output.append("")

    output.append("// MC -> PC")
    output.append("void write_txbuffer(uint8_t *txBuffer) {")
    output_pos = project.buffer_size

    output.append("    int n = 0;")
    output.append("    for (n = 0; n < BUFFER_SIZE; n++) {")
    output.append("        txBuffer[n] = 0;")
    output.append("    }")

    # header
    output.append("    txBuffer[0] = 97;")
    output.append("    txBuffer[1] = 116;")
    output.append("    txBuffer[2] = 97;")
    output.append("    txBuffer[3] = 100;")

    output_pos -= 32
    # timestamp
    output_pos -= 32

    if project.multiplexed_input:
        variable_size = project.multiplexed_input_size
        byte_start, byte_size, bit_offset = project.get_bype_pos(output_pos, variable_size)
        byte_start = project.buffer_bytes - 1 - byte_start
        output.append(f"    memcpy(&txBuffer[{byte_start - (byte_size - 1)}], &MULTIPLEXER_OUTPUT_VALUE, {byte_size}); // {output_pos}")
        output_pos -= variable_size
        variable_size = 8
        byte_start, byte_size, bit_offset = project.get_bype_pos(output_pos, variable_size)
        byte_start = project.buffer_bytes - 1 - byte_start
        output.append(f"    memcpy(&txBuffer[{byte_start - (byte_size - 1)}], &MULTIPLEXER_OUTPUT_ID, {byte_size}); // {output_pos}")
        output_pos -= variable_size

    for size, plugin_instance, data_name, data_config in project.get_interface_data():
        multiplexed = data_config.get("multiplexed", False)
        expansion = data_config.get("expansion", False)
        if multiplexed or expansion:
            continue
        variable_name = data_config["variable"]
        variable_size = data_config["size"]
        if data_config["direction"] == "input":
            byte_start, byte_size, bit_offset = project.get_bype_pos(output_pos, variable_size)
            byte_start = project.buffer_bytes - 1 - byte_start
            if variable_size > 1:
                output.append(f"    memcpy(&txBuffer[{byte_start - (byte_size - 1)}], &{variable_name}, {byte_size}); // {output_pos}")
            else:
                output.append(f"    txBuffer[{byte_start}] |= ({variable_name}<<{bit_offset}); // {output_pos}")
            output_pos -= variable_size

    output.append("")
    output.append("}")
    output.append("")
    open(os.path.join(folder, "riocore.c"), "w").write("\n".join(output))
