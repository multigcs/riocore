import os
import stat
from riocore.generator.cbase import cbase

riocore_path = os.path.dirname(os.path.dirname(__file__))


class mqttbridge(cbase):
    filename_functions = "mqtt_functions.c"
    rtapi_mode = False
    typemap = {
        "float": "float",
        "bool": "bool",
        "s32": "int32_t",
        "u32": "uint32_t",
    }
    printf = "printf"
    prefix = "/rio"
    header_list = [
        "MQTTClient.h",
        "time.h",
        "unistd.h",
        "stdint.h",
        "stdlib.h",
        "stdbool.h",
        "stdio.h",
        "string.h",
        "math.h",
        "sys/mman.h",
        "errno.h",
    ]
    module_info = {
        "AUTHOR": "Oliver Dippel",
        "DESCRIPTION": "Driver for RIO FPGA boards",
        "LICENSE": "GPL v2",
    }

    def __init__(self, project):
        self.project = project
        self.mqtt_path = os.path.join(self.project.config["output_path"], "MQTT")
        os.makedirs(self.mqtt_path, exist_ok=True)

        self.mqtt_makefile()
        self.mqtt_startscript()
        self.mqtt_page()

        output = self.mainc(project)
        output += self.mqtt_functions()

        open(os.path.join(self.mqtt_path, "mqttbridge.c"), "w").write("\n".join(output))

    def mqtt_makefile(self):
        output = []
        output.append("")
        output.append("all: mqttbridge")
        output.append("")
        output.append("mqttbridge: mqttbridge.c")
        output.append("	gcc -o mqttbridge mqttbridge.c -lpaho-mqtt3c")
        output.append("")
        output.append("clean:")
        output.append("	rm -rf mqttbridge")
        output.append("")
        open(os.path.join(self.mqtt_path, "Makefile"), "w").write("\n".join(output))

    def mqtt_page(self):
        output = []
        output.append("<html>")
        output.append("  <head>")
        output.append("    <title>RIO MQTT</title>")
        output.append('    <script src="https://cdnjs.cloudflare.com/ajax/libs/paho-mqtt/1.0.1/mqttws31.js" type="text/javascript"></script>')
        output.append("  </head>")
        output.append("  <style>")
        output.append("""
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}
.container {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    padding: 20px;
}

.item {
    background-color: #f4f4f4;
    padding: 20px;
    text-align: center;
    border: 1px solid #ccc;
}

.tooltip {
  position: relative;
  display: inline-block;
  border-bottom: 1px dotted black; /* If you want dots under the hoverable text */
}

/* Tooltip text */
.tooltip .tooltiptext {
  visibility: hidden;
  width: 120px;
  background-color: black;
  color: #fff;
  text-align: center;
  padding: 5px 0;
  border-radius: 6px;
 
  /* Position the tooltip text - see examples below! */
  position: absolute;
  z-index: 1;
}

/* Show the tooltip text when you mouse over the tooltip container */
.tooltip:hover .tooltiptext {
  visibility: visible;
}

""")

        output.append("  </style>")
        output.append("  <body>")

        output.append('    <div class="container">')

        for plugin_instance in self.project.plugin_instances:
            signals = plugin_instance.signals()
            if not signals:
                continue
            output.append('        <div class="item">')
            output.append(f"    <B>{plugin_instance.instances_name}</B>")
            output.append("    <table>")
            for signal_name, signal_config in signals.items():
                halname = signal_config["halname"]
                direction = signal_config["direction"]
                boolean = signal_config.get("bool")
                unit = signal_config.get("unit")
                description = signal_config.get("description")
                virtual = signal_config.get("virtual")
                if virtual:
                    continue
                if direction == "output":
                    vmin = signal_config.get("min", 0)
                    vmax = signal_config.get("max", 1000)
                    if boolean:
                        vmax = 1
                    output.append("      <tr>")
                    if description:
                        output.append(f'        <td><div class="tooltip">{signal_name}<span class="tooltiptext">{description}</span></div>:</td>')
                    else:
                        output.append(f"        <td>{signal_name}</td>")
                    if boolean:
                        output.append(f'        <td><input type="checkbox" id="{self.mqttname(halname)}" /></td>')
                    else:
                        output.append(f'        <td><b id="{self.mqttname(halname)}_fb">0</b></td>')
                        if unit:
                            output.append(f"        <td>{unit}</td>")
                        output.append(f'        <td><input type="range" min="{vmin}" max="{vmax}" id="{self.mqttname(halname)}" value="0" /></td>')
                    if vmin < 0:
                        output.append(
                            f'        <td><button onclick="document.getElementById(\'{self.mqttname(halname)}\').value = 0;" id="{self.mqttname(halname)}_zero" type="button">0</button></td>'
                        )
                    output.append("      </tr>")
                elif direction == "input":
                    output.append("      <tr>")
                    if description:
                        output.append(f'        <td><div class="tooltip">{signal_name}<span class="tooltiptext">{description}</span></div>:</td>')
                    else:
                        output.append(f"        <td>{signal_name}</td>")
                    output.append(f'        <td><b id="{self.mqttname(halname)}">0</b></td>')
                    if unit:
                        output.append(f"        <td>{unit}</td>")
                    output.append("      </tr>")
            output.append("    </table>")
            output.append("        </div>")

        output.append("    </div>")

        output.append("")
        output.append('    <script type="text/javascript">')
        output.append('        var clientID = "ID-" + Math.round(Math.random() * 1000);')
        output.append('        var client = new Paho.MQTT.Client("127.0.0.1", 9001, clientID);')
        output.append("")

        for plugin_instance in self.project.plugin_instances:
            signals = plugin_instance.signals()
            if not signals:
                continue
            for signal_name, signal_config in signals.items():
                halname = signal_config["halname"]
                direction = signal_config["direction"]
                boolean = signal_config.get("bool")
                virtual = signal_config.get("virtual")
                if virtual:
                    continue
                if direction == "output":
                    vmin = signal_config.get("min", 0)
                    vmax = signal_config.get("max", 1000)
                    output.append(f'        document.getElementById("{self.mqttname(halname)}").addEventListener("change", publish, false);')
                    output.append(f'        document.getElementById("{self.mqttname(halname)}").addEventListener("input", publish, false);')
                    if vmin < 0:
                        output.append(f'        document.getElementById("{self.mqttname(halname)}_zero").addEventListener("click", publish, false);')

        output.append("        client.connect({onSuccess:onConnect});")
        output.append("        client.onMessageArrived = onMessage;")
        output.append("")
        output.append("        function onConnect() {")
        output.append('            console.log("connected");')

        for plugin_instance in self.project.plugin_instances:
            signals = plugin_instance.signals()
            if not signals:
                continue
            for signal_name, signal_config in signals.items():
                halname = signal_config["halname"]
                direction = signal_config["direction"]
                boolean = signal_config.get("bool")
                virtual = signal_config.get("virtual")
                if virtual:
                    continue
                if direction == "input":
                    output.append(f'            client.subscribe("{self.mqttname(halname)}");')

        output.append('            console.log("connected");')
        output.append("        }")
        output.append("")
        output.append("""
        function publish() {
            var topic = this.attributes.id.value.replace("_zero", "");
            element = document.getElementById(topic);
            var value = "0";
            if (element.attributes.type.value == "checkbox") {
                if (element.checked) {
                    value = "1";
                }
            } else {
                value = element.value;
            }
            console.log("publish", topic, value);

            fb_element = document.getElementById(topic + "_fb");
            if (fb_element) {
                fb_element.innerHTML = value;
            }


            var message = new Paho.MQTT.Message(value);
            message.destinationName = topic;
            client.send(message);
        }
""")
        output.append("        function onMessage(message) {")
        output.append('            // console.log("msg", message.destinationName, message.payloadString);')

        for plugin_instance in self.project.plugin_instances:
            signals = plugin_instance.signals()
            if not signals:
                continue
            for signal_name, signal_config in signals.items():
                halname = signal_config["halname"]
                direction = signal_config["direction"]
                boolean = signal_config.get("bool")
                virtual = signal_config.get("virtual")
                if virtual:
                    continue
                if direction == "input":
                    output.append(f'            if (message.destinationName == "{self.mqttname(halname)}") {{')
                    output.append(f'                document.getElementById("{self.mqttname(halname)}").innerHTML = message.payloadString;')
                    output.append("            }")

        output.append("        }")
        output.append("")
        output.append("    </script>")
        output.append("  </body>")
        output.append("</html>")
        output.append("")
        open(os.path.join(self.mqtt_path, "test.html"), "w").write("\n".join(output))

    def mqtt_functions(self):
        output = []
        output.append("")
        output.append('#define MQTT_ADDRESS "127.0.0.1"')
        output.append("")
        output.append("volatile MQTTClient_deliveryToken deliveredtoken;")
        output.append("")
        output.append("void delivered(void *context, MQTTClient_deliveryToken dt) {")
        output.append('    printf("### Message with token value %d delivery confirmed\\n", dt);')
        output.append("    deliveredtoken = dt;")
        output.append("}")
        output.append("")
        output.append("int msgarrvd(void *context, char *topicName, int topicLen, MQTTClient_message *message) {")

        # output.append("    printf(\"### Message arrived\\n\");")
        # output.append("    printf(\"###      topic: %s\\n\", topicName);")
        # output.append("    printf(\"###      len: %i\\n\", message->payloadlen);")
        # output.append("    printf(\"###    message: %.*s\\n\", message->payloadlen, (char*)message->payload);")

        for plugin_instance in self.project.plugin_instances:
            for signal_name, signal_config in plugin_instance.signals().items():
                halname = signal_config["halname"]
                varname = signal_config["varname"]
                direction = signal_config["direction"]
                boolean = signal_config.get("bool")
                virtual = signal_config.get("virtual")
                if virtual:
                    continue
                if direction == "output":
                    output.append(f'    if (strlen(topicName) == {len(self.mqttname(halname))} && strcmp(topicName, "{self.mqttname(halname)}") == 0) {{')
                    if boolean:
                        output.append(f"        *data->{varname} = atoi((char*)message->payload);")
                    else:
                        output.append(f"        *data->{varname} = atof((char*)message->payload);")
                    output.append("    }")

        output.append("")

        output.append("    MQTTClient_freeMessage(&message);")
        output.append("    MQTTClient_free(topicName);")
        output.append("    return 1;")
        output.append("}")
        output.append("")
        output.append("void connlost(void *context, char *cause) {")
        output.append('    printf("\\n### Connection lost\\n");')
        output.append('    printf("###      cause: %s\\n", cause);')
        output.append("}")
        output.append("")

        output.append("int main(int argc, char **argv) {")
        output.append("    char tmp_str[20];")
        output.append("")
        output.append("    data = (data_t*)malloc(sizeof(data_t));")
        output.append("    register_signals();")
        output.append("    interface_init();")
        output.append("")

        output.append("")
        output.append("    MQTTClient client;")
        output.append("    MQTTClient_connectOptions conn_opts = MQTTClient_connectOptions_initializer;")
        output.append("    MQTTClient_message pubmsg = MQTTClient_message_initializer;")
        output.append("    MQTTClient_deliveryToken token;")
        output.append("    int rc;")
        output.append("")
        output.append("    const char* uri = (argc > 1) ? argv[1] : MQTT_ADDRESS;")
        output.append('    printf("Using server at %s\\n", uri);')
        output.append("")
        output.append("    if ((rc = MQTTClient_create(&client, uri, MODNAME,")
        output.append("        MQTTCLIENT_PERSISTENCE_NONE, NULL)) != MQTTCLIENT_SUCCESS)")
        output.append("    {")
        output.append('         printf("Failed to create client, return code %d\\n", rc);')
        output.append("         exit(EXIT_FAILURE);")
        output.append("    }")
        output.append("")

        output.append("    if ((rc = MQTTClient_setCallbacks(client, NULL, connlost, msgarrvd, delivered)) != MQTTCLIENT_SUCCESS) {")
        output.append('        printf("Failed to set callbacks, return code %d\\n", rc);')
        output.append("        rc = EXIT_FAILURE;")
        output.append("        exit(1);")
        output.append("    }")
        output.append("")

        output.append("    conn_opts.keepAliveInterval = 20;")
        output.append("    conn_opts.cleansession = 1;")
        output.append("    if ((rc = MQTTClient_connect(client, &conn_opts)) != MQTTCLIENT_SUCCESS) {")
        output.append('        printf("Failed to connect, return code %d\\n", rc);')
        output.append("        exit(EXIT_FAILURE);")
        output.append("    }")
        output.append("")

        for plugin_instance in self.project.plugin_instances:
            for signal_name, signal_config in plugin_instance.signals().items():
                halname = signal_config["halname"]
                varname = signal_config["varname"]
                direction = signal_config["direction"]
                boolean = signal_config.get("bool")
                virtual = signal_config.get("virtual")
                if virtual:
                    continue
                if direction == "output":
                    output.append(f'    if ((rc = MQTTClient_subscribe(client, "{self.mqttname(halname)}", 0)) != MQTTCLIENT_SUCCESS) {{')
                    output.append('    	printf("Failed to subscribe, return code %d\\n", rc);')
                    output.append("    	rc = EXIT_FAILURE;")
                    output.append("    }")
                    output.append("")

        output.append("")
        output.append("    while (1) {")
        output.append("        rio_readwrite();")
        for plugin_instance in self.project.plugin_instances:
            for signal_name, signal_config in plugin_instance.signals().items():
                halname = signal_config["halname"]
                varname = signal_config["varname"]
                direction = signal_config["direction"]
                boolean = signal_config.get("bool")
                virtual = signal_config.get("virtual")
                if virtual:
                    continue
                if direction == "input":
                    if boolean:
                        output.append(f'        sprintf(tmp_str, "%i", *data->{varname});')
                    else:
                        output.append(f'        sprintf(tmp_str, "%f", *data->{varname});')
                    output.append("        pubmsg.payload = tmp_str;")
                    output.append("        pubmsg.payloadlen = (int)strlen(tmp_str);")
                    output.append("        pubmsg.qos = 0;")
                    output.append("        pubmsg.retained = 0;")
                    output.append(f'        if ((rc = MQTTClient_publishMessage(client, "{self.mqttname(halname)}", &pubmsg, &token)) != MQTTCLIENT_SUCCESS) {{')
                    output.append('             printf("Failed to publish message, return code %d\\n", rc);')
                    output.append("             exit(EXIT_FAILURE);")
                    output.append("        }")
                    output.append("")
        output.append("")
        output.append("        rtapi_delay(100000000);")
        output.append("    }")
        output.append("")
        output.append("    if ((rc = MQTTClient_disconnect(client, 10000)) != MQTTCLIENT_SUCCESS) {")
        output.append('       printf("Failed to disconnect, return code %d\\n", rc);')
        output.append("    }")
        output.append("    MQTTClient_destroy(&client);")
        output.append("")
        output.append("    return 0;")
        output.append("}")
        output.append("")
        return output

    def mqtt_startscript(self):
        output = ["#!/bin/sh"]
        output.append("")
        output.append("set -e")
        output.append("set -x")
        output.append("")
        output.append('DIRNAME=`dirname "$0"`')
        output.append("")
        output.append('echo "compile package:"')
        output.append('(cd "$DIRNAME" && make clean all)')
        output.append("")
        output.append('echo "running mqttbridge:"')
        output.append("$DIRNAME/mqttbridge")
        output.append("")
        output.append("")
        os.makedirs(self.mqtt_path, exist_ok=True)
        target = os.path.join(self.mqtt_path, "start.sh")
        open(target, "w").write("\n".join(output))
        os.chmod(target, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

    def mqttname(self, halname):
        mqttname = halname.replace(".", "/").replace("-", "_")
        return f"{self.prefix}/{mqttname}"

    def vinit(self, vname, vtype, halstr=None, vdir="input"):
        vtype = self.typemap.get(vtype, vtype)
        return f"    data->{vname} = ({vtype}*)malloc(sizeof({vtype}));"
