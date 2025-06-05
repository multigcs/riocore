import graphviz

from riocore import gpios
from riocore import components


class ConfigGraph:
    def __init__(self, parent):
        self.parent = parent
        self.map = None

    def png(self):
        try:
            self.gAll = graphviz.Digraph("G", format="svg")
            self.gAll.attr(rankdir="LR")
            self.gAll.attr(bgcolor="black")
            self.map = None

            num = 0
            fpga_name = f"{self.parent.config.get('boardcfg')}"

            gAll = graphviz.Digraph("G", format="png")
            gAll.attr(rankdir="LR")
            gAll.attr(bgcolor="black")

            lcports = []
            sports = []
            gpio_config = self.parent.config.get("gpios", [])
            gpio_map = {}
            gpio_ids = {}
            gpio_pinmapping = {}
            for gpio in gpio_config:
                gtype = gpio.get("type")
                if gtype not in gpio_ids:
                    gpio_ids[gtype] = 0
                if hasattr(gpios, f"gpio_{gtype}"):
                    ginstance = getattr(gpios, f"gpio_{gtype}")(gpio_ids[gtype], gpio)
                    gpio_pinmapping.update(ginstance.pinmapping())
                    mportsl = []
                    mportsr = []
                    for key, pin in ginstance.slotpins().items():
                        if pin["pin"]:
                            pinname = pin["pin"].replace(f"{ginstance.NAME}.", "")
                            gpio_map[pin["pin"]] = f"{ginstance.NAME}:{pinname}"
                            mportsl.append(key)
                            mportsr.append(f"<{pinname}>{pinname}")
                    label = f"{{ {{ {ginstance.NAME}\\nGPIO-Pins |   {{ {{ {' | '.join(mportsl)} }} | {{ {' | '.join(mportsr)} }} }} }} }}"
                    gAll.node(ginstance.NAME, shape="record", label=label, fontsize="11pt", style="rounded, filled", fillcolor="yellow")
            linuxcnc_config = self.parent.config.get("linuxcnc", {})
            for net in linuxcnc_config.get("net", []):
                net_source = net.get("source")
                net_target = net.get("target")
                net_source = gpio_pinmapping.get(net_source, net_source)
                net_target = gpio_pinmapping.get(net_target, net_target)
                if net_source and net_target:
                    if net_source in gpio_map:
                        hal_pin = net_target
                        gAll.edge(f"{gpio_map[net_source]}", f"hal:{hal_pin}", dir="forward", color="green")
                        lcports.append(f"<{hal_pin}>{hal_pin}")
                    elif net_target in gpio_map:
                        hal_pin = net_source
                        gAll.edge(f"{gpio_map[net_target]}", f"hal:{hal_pin}", dir="back", color="red")
                        lcports.append(f"<{hal_pin}>{hal_pin}")

            component_nums = {}
            for component in linuxcnc_config.get("components", []):
                comp_type = component.get("type")
                if comp_type not in component_nums:
                    component_nums[comp_type] = 0
                component["num"] = component_nums[comp_type]
                component_nums[comp_type] += 1
                if hasattr(components, f"comp_{comp_type}"):
                    cinstance = getattr(components, f"comp_{comp_type}")(component)
                    comp_pins = cinstance.setup.get("pins", {})
                    ports = [f"<{p.split(':')[0]}>{p.split(':')[0]}" for p in cinstance.PINS]
                    label = f"{{ {{ {'|'.join(ports)} }} | {{ {cinstance.TITLE} }} | {{ {'|'.join(cinstance.SIGNALS)} }} }}"
                    gAll.node(cinstance.PREFIX, shape="record", label=label, fontsize="11pt", style="rounded, filled", fillcolor="yellow")
                    for pin_name, pin_data in cinstance.PINDEFAULTS.items():
                        if pin_name in comp_pins:
                            comp_pin = gpio_pinmapping.get(comp_pins[pin_name], comp_pins[pin_name])
                            if comp_pin in gpio_map:
                                if pin_data["direction"] == "output":
                                    gAll.edge(gpio_map[comp_pin], f"{cinstance.PREFIX}:{pin_name}", dir="back", color="red")
                                else:
                                    gAll.edge(gpio_map[comp_pin], f"{cinstance.PREFIX}:{pin_name}", dir="forward", color="green")

            # show slots
            for slot in self.parent.slots:
                slot_name = slot.get("name")
                slot_pins = slot.get("pins", {})
                mportsl = []
                mportsr = []
                for pin_name, pin in slot_pins.items():
                    if isinstance(pin, dict):
                        pin = pin["pin"]
                    pin_id = f"{slot_name}_{pin_name}"
                    mportsl.append(f"<{pin}>{pin}")
                    mportsr.append(f"<{pin_id}>{pin_name}")

                label = f"{{ {{{' | '.join(mportsl)}}} | {slot_name} | {{{' | '.join(mportsr)}}} }}"
                sports.append(label)

            virtual_cons = {}
            expansion_cons = {}
            for plugin_instance in self.parent.plugins.plugin_instances:
                name = plugin_instance.plugin_setup.get("name", plugin_instance.title)
                title = plugin_instance.NAME
                if name:
                    title = f"{name} ({plugin_instance.NAME})"
                for pname in plugin_instance.expansion_outputs():
                    expansion_cons[pname] = title
                for pname in plugin_instance.expansion_inputs():
                    expansion_cons[pname] = title

                name = plugin_instance.plugin_setup.get("name", plugin_instance.title)
                title = plugin_instance.NAME
                if name:
                    title = f"{name} ({plugin_instance.NAME})"

                for pin_name, pin_defaults in plugin_instance.PINDEFAULTS.items():
                    pin_setup = plugin_instance.plugin_setup.get("pins", {}).get(pin_name, {})
                    direction = pin_defaults["direction"]
                    pin = pin_setup.get("pin")
                    if not pin:
                        continue

                    if pin.startswith("VIRT:"):
                        if direction == "input":
                            virtual_cons[pin] = (title, pin_name)

            joint_n = 0
            for plugin_instance in self.parent.plugins.plugin_instances:
                pports = []
                name = plugin_instance.plugin_setup.get("name", plugin_instance.title)
                title = plugin_instance.NAME
                if name:
                    title = f"{name} ({plugin_instance.NAME})"

                signalports = []
                for pin_name, pin_defaults in plugin_instance.PINDEFAULTS.items():
                    pin_setup = plugin_instance.plugin_setup.get("pins", {}).get(pin_name, {})
                    pin = pin_setup.get("pin")

                    if pin and pin.startswith("VIRT:") and pin_defaults["direction"] == "input":
                        signalports.append(f"<{pin_name}>{pin_name}")
                    else:
                        pports.append(f"<{pin_name}>{pin_name}")

                    if not pin_setup and pin_defaults.get("optional") is True:
                        continue
                    elif "pin" not in pin_setup and pin_defaults.get("optional") is True:
                        continue
                    elif not pin:
                        continue

                    if pin in self.parent.pinmapping_rev:
                        pin = self.parent.pinmapping_rev[pin]

                    con_dev = fpga_name
                    con_pin = pin

                    if pin in expansion_cons:
                        con_dev = expansion_cons[pin]
                        con_pin = pin.replace("[", "").replace("]", "")

                    if ":" in con_pin:
                        con_pin = con_pin.replace(":", "_")

                    if pin.startswith("VIRT:"):
                        if pin in virtual_cons:
                            if pin_defaults["direction"] == "output":
                                con_dev = virtual_cons[pin][0]
                                con_pin = virtual_cons[pin][1]
                            else:
                                continue

                    if pin_defaults["direction"] == "input":
                        modifiers = pin_setup.get("modifier", [])
                        color = "green"
                        arrow_dir = "forward"
                    else:
                        modifiers = pin_setup.get("modifier", [])
                        if modifiers:
                            modifiers = reversed(modifiers)
                        color = "red"
                        arrow_dir = "back"

                    if modifiers:
                        modifier_chain = []
                        for modifier_num, modifier in enumerate(modifiers):
                            modifier_type = modifier["type"]
                            modifier_chain.append(modifier_type)
                        modifier_label = f"{{ <l> | {' | '.join(modifier_chain)} | <r> }}"
                        gAll.edge(f"{con_dev}:{con_pin}", f"{name}_{pin_name}_{modifier_type}_{modifier_num}:l", dir=arrow_dir, color=color)
                        con_dev = f"{name}_{pin_name}_{modifier_type}_{modifier_num}"
                        con_pin = "r"
                        gAll.node(
                            f"{name}_{pin_name}_{modifier_type}_{modifier_num}",
                            shape="record",
                            label=modifier_label,
                            fontsize="11pt",
                            style="rounded, filled",
                            fillcolor="lightyellow",
                        )

                    if pin.startswith("VIRT:"):
                        color = "yellow"
                        gAll.edge(f"{con_dev}:{con_pin}", f"{title}:{pin_name}", dir=arrow_dir, color=color, label=pin.split(":")[-1], fontcolor="white", fontsize="11pt")
                    else:
                        gAll.edge(f"{con_dev}:{con_pin}", f"{title}:{pin_name}", dir=arrow_dir, color=color)

                    if ":" not in pin and pin not in self.parent.expansion_pins:
                        sports.append(f"<{pin}>{pin}")

                    num += 1

                if hasattr(plugin_instance, "cfggraph"):
                    (p_lcports, p_signalports) = plugin_instance.cfggraph(title, gAll)
                    lcports += p_lcports
                    signalports += p_signalports
                else:
                    for signal_name, signal_defaults in plugin_instance.SIGNALS.items():
                        signalports.append(f"<signal_{signal_name}>{signal_name}")
                        signal_direction = plugin_instance.SIGNALS.get(signal_name, {}).get("direction")
                        direction_mapping = {"input": "normal", "output": "back", "inout": "both"}
                        signal_config = plugin_instance.plugin_setup.get("signals", {}).get(signal_name)

                        net = None
                        function = None
                        if signal_config:
                            net = signal_config.get("net")
                            function = signal_config.get("function")
                            if function:
                                gAll.edge(f"{title}:signal_{signal_name}", f"hal:{function}", dir=direction_mapping.get(signal_direction, "none"), color="white", fontcolor="white")
                                lcports.append(f"<{function}>{function}")
                            if net:
                                gAll.edge(f"{title}:signal_{signal_name}", f"hal:{net}", dir=direction_mapping.get(signal_direction, "none"), color="white", fontcolor="white")
                                lcports.append(f"<{net}>{net}")

                        elif plugin_instance.plugin_setup.get("is_joint", False):
                            if signal_name == "position" and signal_direction == "input":
                                hal_pin = f"joint.{joint_n}.motor-pos-fb"
                                gAll.edge(f"{title}:signal_{signal_name}", f"hal:{hal_pin}", dir="normal", color="white", fontcolor="white")
                                lcports.append(f"<{hal_pin}>{hal_pin}")
                            elif signal_name == "position" and signal_direction == "output":
                                hal_pin = f"joint.{joint_n}.motor-pos-cmd"
                                gAll.edge(f"{title}:signal_{signal_name}", f"hal:{hal_pin}", dir="back", color="white", fontcolor="white")
                                lcports.append(f"<{hal_pin}>{hal_pin}")
                            elif signal_name == "velocity":
                                hal_pin = f"joint.{joint_n}.motor-pos-cmd"
                                gAll.edge(f"{title}:signal_{signal_name}", f"hal:{hal_pin}", dir="back", color="white", fontcolor="white")
                                lcports.append(f"<{hal_pin}>{hal_pin}")

                # expansion ports
                eports = []
                for pname in plugin_instance.expansion_outputs():
                    cpname = pname.replace("[", "").replace("]", "")
                    if pname.startswith("VARIN") or pname.startswith("VAROUT"):
                        pname = pname.split("_", 2)[-1]
                    eports.append(f"<{cpname}>{pname}")
                for pname in plugin_instance.expansion_inputs():
                    cpname = pname.replace("[", "").replace("]", "")
                    if pname.startswith("VARIN") or pname.startswith("VAROUT"):
                        pname = pname.split("_", 2)[-1]
                    eports.append(f"<{cpname}>{pname}")

                if eports:
                    label = f"{{ {{{' | '.join(pports)}}} | {title} | {{{' | '.join(eports)}}} }}"
                elif signalports:
                    label = f"{{ {{{' | '.join(pports)}}} | {title} | {{{' | '.join(signalports)}}} }}"
                else:
                    label = f"{{ {{{' | '.join(pports)}}} | {title} }}"

                gAll.node(
                    title,
                    shape="record",
                    label=label,
                    fontsize="11pt",
                    style="rounded, filled",
                    fillcolor="lightblue",
                    URL=f"instance:{name.replace(' ', '#')}",
                )

                if plugin_instance.plugin_setup.get("is_joint", False):
                    joint_n += 1

            for module_data in self.parent.config.get("modules", []):
                slot_name = module_data.get("slot")
                module_name = module_data.get("module")
                title = slot_name
                if module_name:
                    title = f"{module_name} ({title})"

                for plugin_instance in self.parent.modules[slot_name]["instances"]:
                    pports = []
                    name = plugin_instance.plugin_setup.get("name", plugin_instance.title)
                    title = plugin_instance.NAME
                    if name:
                        title = f"{name} ({plugin_instance.NAME})"
                    for pin_name, pin_defaults in plugin_instance.PINDEFAULTS.items():
                        pin_setup = plugin_instance.plugin_setup.get("pins", {}).get(pin_name, {})
                        if "pin_mapped" not in pin_setup:
                            continue

                        pin = f"{slot_name}_{pin_setup['pin_mapped']}"
                        con_dev = fpga_name
                        con_pin = pin

                        if pin and pin in self.parent.expansion_pins:
                            con_dev = "_".join(pin.split("_")[0:-1])
                            con_pin = pin.replace("[", "").replace("]", "")

                        if pin_defaults["direction"] == "input":
                            modifiers = pin_setup.get("modifier", [])
                            color = "green"
                            arrow_dir = "forward"
                        else:
                            modifiers = pin_setup.get("modifier", [])
                            if modifiers:
                                modifiers = reversed(modifiers)
                            color = "red"
                            arrow_dir = "back"

                        if modifiers:
                            modifier_chain = []
                            for modifier_num, modifier in enumerate(modifiers):
                                modifier_type = modifier["type"]
                                modifier_chain.append(modifier_type)
                            modifier_label = f"{{ <l> | {' | '.join(modifier_chain)} | <r> }}"
                            gAll.edge(f"{con_dev}:{con_pin}", f"{name}_{pin_name}_{modifier_type}_{modifier_num}:l", dir=arrow_dir, color=color)
                            con_dev = f"{name}_{pin_name}_{modifier_type}_{modifier_num}"
                            con_pin = "r"
                            gAll.node(
                                f"{name}_{pin_name}_{modifier_type}_{modifier_num}",
                                shape="record",
                                label=modifier_label,
                                fontsize="11pt",
                                style="rounded, filled",
                                fillcolor="lightyellow",
                            )

                        gAll.edge(f"{con_dev}:{con_pin}", f"{title}:{pin_name}", dir=arrow_dir, color=color)
                        pports.append(f"<{pin_name}>{pin_name}")

                    signalports = []
                    for signal_name, signal_defaults in plugin_instance.SIGNALS.items():
                        signal_config = plugin_instance.plugin_setup.get("signals", {}).get(signal_name)
                        signalports.append(f"<signal_{signal_name}>{signal_name}")
                        if signal_config:
                            net = signal_config.get("net")
                            function = signal_config.get("function")
                            signal_direction = plugin_instance.SIGNALS.get(signal_name, {}).get("direction")
                            direction_mapping = {"input": "forward", "output": "back", "inout": "both"}

                            if not net and not function and plugin_instance.plugin_setup.get("is_joint", False):
                                if signal_name == "position" and signal_direction == "input":
                                    hal_pin = f"joint.{joint_n}.motor-pos-fb"
                                    gAll.edge(f"{title}:signal_{signal_name}", f"hal:{hal_pin}", dir="normal", color="white", fontcolor="white")
                                    lcports.append(f"<{hal_pin}>{hal_pin}")
                                elif signal_name == "position" and signal_direction == "output":
                                    hal_pin = f"joint.{joint_n}.motor-pos-cmd"
                                    gAll.edge(f"{title}:signal_{signal_name}", f"hal:{hal_pin}", dir="back", color="white", fontcolor="white")
                                    lcports.append(f"<{hal_pin}>{hal_pin}")
                                elif signal_name == "velocity":
                                    hal_pin = f"joint.{joint_n}.motor-pos-cmd"
                                    gAll.edge(f"{title}:signal_{signal_name}", f"hal:{hal_pin}", dir="back", color="white", fontcolor="white")
                                    lcports.append(f"<{hal_pin}>{hal_pin}")

                            if function:
                                gAll.edge(f"{title}:signal_{signal_name}", f"hal:{function}", dir=direction_mapping.get(signal_direction, "none"), color="white", fontcolor="white")
                                lcports.append(f"<{function}>{function}")
                            if net:
                                gAll.edge(f"{title}:signal_{signal_name}", f"hal:{net}", dir=direction_mapping.get(signal_direction, "none"), color="white", fontcolor="white")
                                lcports.append(f"<{net}>{net}")

                    if signalports:
                        label = f"{{ {{{' | '.join(pports)}}} | {title} | {{{' | '.join(signalports)}}} }}"
                    else:
                        label = f"{{ {{{' | '.join(pports)}}} | {title} }}"
                    gAll.node(
                        title,
                        shape="record",
                        label=label,
                        fontsize="11pt",
                        style="rounded, filled",
                        fillcolor="lightblue",
                        URL=f"instance:{name.replace(' ', '#')}",
                    )

                    if plugin_instance.plugin_setup.get("is_joint", False):
                        joint_n += 1

            if sports:
                label = f"{{ {{ {fpga_name}\\nPhysical-Pins | {' | '.join(sports)}}} }}"
                gAll.node(f"{fpga_name}", shape="record", label=label, fontsize="11pt", style="rounded, filled", fillcolor="yellow")

            if lcports:
                label = f"{{ {{ LinuxCNC\\nHAL-Pins | {' | '.join(lcports)}}} }}"
                gAll.node(
                    "hal",
                    shape="record",
                    label=label,
                    fontsize="11pt",
                    style="rounded, filled",
                    fillcolor="lightgreen",
                )

            self.map = {}
            for line in gAll.pipe(format="imap").decode().split("\n"):
                if line.startswith("rect "):
                    parts = line.split()
                    instance = parts[1].split(":")[1].replace("#", " ")
                    begin = parts[2].split(",")
                    end = parts[3].split(",")
                    if instance not in self.map:
                        self.map[instance] = []
                    self.map[instance].append((int(begin[0]), int(begin[1]), int(end[0]), int(end[1])))

            return gAll.pipe()

        except Exception as error:
            print(f"ERROR(overview): {error}")

    def on_click(self, x, y):
        if self.map is None:
            return
        for instance, positions in self.map.items():
            for pos in positions:
                if x >= pos[0] and x <= pos[2] and y >= pos[1] and y <= pos[3]:
                    for plugin_instance in self.parent.plugins.plugin_instances:
                        name = plugin_instance.plugin_setup.get("name", plugin_instance.title)
                        if name == instance:
                            self.parent.gui_plugins.edit_plugin(plugin_instance, None, is_new=False)
                            return
                    for module_data in self.parent.config.get("modules", []):
                        slot_name = module_data.get("slot")
                        for plugin_instance in self.parent.modules[slot_name]["instances"]:
                            name = plugin_instance.plugin_setup.get("name", plugin_instance.title)
                            if name == instance:
                                self.parent.gui_plugins.edit_plugin(plugin_instance, None, is_new=False)
                                return
