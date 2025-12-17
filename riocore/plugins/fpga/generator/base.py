class generator_base:
    def calc_buffersize(self, project):
        self.timestamp_size = 32
        self.header_size = 32
        self.input_size = 0
        self.output_size = 0
        self.interface_sizes = set()
        self.multiplexed_input = 0
        self.multiplexed_input_size = 0
        self.multiplexed_output = 0
        self.multiplexed_output_size = 0
        self.multiplexed_output_id = 0
        for plugin_instance in project.plugin_instances:
            if plugin_instance.master != self.instance.instances_name and plugin_instance.gmaster != self.instance.instances_name:
                continue
            for data_config in plugin_instance.interface_data().values():
                self.interface_sizes.add(data_config["size"])
                variable_size = data_config["size"]
                multiplexed = data_config.get("multiplexed", False)
                expansion = data_config.get("expansion", False)
                if expansion:
                    continue
                if data_config["direction"] == "input":
                    if not data_config.get("expansion"):
                        if multiplexed:
                            self.multiplexed_input += 1
                            self.multiplexed_input_size = (max(self.multiplexed_input_size, variable_size) + 7) // 8 * 8
                            self.multiplexed_input_size = max(self.multiplexed_input_size, 8)
                        else:
                            self.input_size += variable_size
                elif data_config["direction"] == "output":
                    if not data_config.get("expansion"):
                        if multiplexed:
                            self.multiplexed_output += 1
                            self.multiplexed_output_size = (max(self.multiplexed_output_size, variable_size) + 7) // 8 * 8
                            self.multiplexed_output_size = max(self.multiplexed_output_size, 8)
                        else:
                            self.output_size += variable_size

        if self.multiplexed_input:
            self.input_size += self.multiplexed_input_size + 8
        if self.multiplexed_output:
            self.output_size += self.multiplexed_output_size + 8

        self.input_size = self.input_size + self.header_size + self.timestamp_size
        self.output_size = self.output_size + self.header_size
        self.buffer_size = (max(self.input_size, self.output_size) + 7) // 8 * 8
        self.buffer_bytes = self.buffer_size // 8
        # self.config["buffer_size"] = self.buffer_size

        # log("# PC->FPGA", self.output_size)
        # log("# FPGA->PC", self.input_size)
        # log("# MAX", self.buffer_size)

    def calc_buffersize_sub(self, project, subname):
        self.header_size = 32
        self.sub_input_size = 0
        self.sub_output_size = 0
        self.sub_interface_sizes = set()
        self.sub_multiplexed_input = 0
        self.sub_multiplexed_input_size = 0
        self.sub_multiplexed_output = 0
        self.sub_multiplexed_output_size = 0
        self.sub_multiplexed_output_id = 0
        for plugin_instance in project.plugin_instances:
            if plugin_instance.gmaster != self.instance.instances_name or plugin_instance.master == plugin_instance.gmaster:
                continue
            if plugin_instance.master != subname:
                continue
            for data_config in plugin_instance.interface_data().values():
                self.sub_interface_sizes.add(data_config["size"])
                variable_size = data_config["size"]
                multiplexed = data_config.get("multiplexed", False)
                expansion = data_config.get("expansion", False)
                if expansion:
                    continue
                if data_config["direction"] == "input":
                    if not data_config.get("expansion"):
                        if multiplexed:
                            self.sub_multiplexed_input += 1
                            self.sub_multiplexed_input_size = (max(self.sub_multiplexed_input_size, variable_size) + 7) // 8 * 8
                            self.sub_multiplexed_input_size = max(self.sub_multiplexed_input_size, 8)
                        else:
                            self.sub_input_size += variable_size
                elif data_config["direction"] == "output":
                    if not data_config.get("expansion"):
                        if multiplexed:
                            self.sub_multiplexed_output += 1
                            self.sub_multiplexed_output_size = (max(self.sub_multiplexed_output_size, variable_size) + 7) // 8 * 8
                            self.sub_multiplexed_output_size = max(self.sub_multiplexed_output_size, 8)
                        else:
                            self.sub_output_size += variable_size

        if self.sub_multiplexed_input:
            self.sub_input_size += self.sub_multiplexed_input_size + 8
        if self.sub_multiplexed_output:
            self.sub_output_size += self.sub_multiplexed_output_size + 8

        self.sub_input_size = self.sub_input_size + self.header_size
        self.sub_output_size = self.sub_output_size + self.header_size
        self.sub_buffer_size = (max(self.sub_input_size, self.sub_output_size) + 7) // 8 * 8
        self.sub_buffer_bytes = self.sub_buffer_size // 8

    def get_interface_data(self, project):
        interface_data = []
        for size in sorted(self.interface_sizes, reverse=True):
            for plugin_instance in project.plugin_instances:
                if plugin_instance.master != self.instance.instances_name and plugin_instance.gmaster != self.instance.instances_name:
                    continue
                for data_name, data_config in plugin_instance.interface_data().items():
                    if data_config["size"] == size:
                        interface_data.append([size, plugin_instance, data_name, data_config])
        return interface_data
