import json
import os
import stat

from .cbase import cbase

riocore_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


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
    prefix = "rio"
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

    def __init__(self, project, instance):
        self.project = project
        self.instance = instance
        # self.prefix = instance.hal_prefix
        self.mqtt_path = os.path.join(self.project.config["output_path"], "MQTT", instance.instances_name)
        os.makedirs(self.mqtt_path, exist_ok=True)

        self.mqtt_makefile()
        self.mqtt_startscript()
        self.mqtt_page()
        self.nodered_template()

        output = self.mainc(autostart=True)
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
        output.append("""<html>
  <head>
    <title>RIO MQTT</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/paho-mqtt/1.0.1/mqttws31.js" type="text/javascript"></script>
  </head>
  <style>

  :root{
    --bg:#0e1117;
    --panel:#161b27;
    --panel-2:#1c2330;
    --border:#262d3a;
    --text:#e6edf3;
    --muted:#8b949e;
    --accent:#4f8cff;
    --accent-2:#22c55e;
    --warn:#f59e0b;
    --danger:#ef4444;
  }
  *{box-sizing:border-box;margin:0;padding:0}
  body{
    font-family:"Segoe UI",Inter,system-ui,-apple-system,Roboto,Arial,sans-serif;
    background:var(--bg);
    color:var(--text);
    min-height:100vh;
    padding:24px;
  }

  /* ---------- Header ---------- */
  header{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:16px;
    flex-wrap:wrap;
    margin-bottom:22px;
  }
  .brand{display:flex;align-items:center;gap:12px}
  .logo{
    width:40px;height:40px;border-radius:10px;
    background:linear-gradient(135deg,var(--accent),#8b5cf6);
    display:grid;place-items:center;font-weight:700;font-size:18px;color:#fff;
  }
  .brand h1{font-size:19px;font-weight:600;letter-spacing:.2px}
  .brand p{font-size:12.5px;color:var(--muted)}
  .head-actions{display:flex;align-items:center;gap:10px}
  .search{
    background:var(--panel);border:1px solid var(--border);
    color:var(--text);padding:9px 14px;border-radius:9px;font-size:13.5px;width:220px;outline:none;
  }
  .search:focus{border-color:var(--accent)}
  .btn{
    background:var(--accent);border:none;color:#fff;font-size:13.5px;font-weight:600;
    padding:9px 16px;border-radius:9px;cursor:pointer;transition:.2s;
  }
  .btn:hover{background:#3b78ec}
  .avatar{
    width:38px;height:38px;border-radius:50%;background:var(--panel-2);
    border:1px solid var(--border);display:grid;place-items:center;font-size:13px;font-weight:600;color:var(--muted);
  }

  /* ---------- Grid: 5 containers ---------- */
  .grid{
    display:grid;
    grid-template-columns:repeat(6,1fr);
    grid-template-areas:
      "a a b b c c"
      "d d d d e e";
    gap:9px;
  }
  .card{
    background:var(--panel);
    border:1px solid var(--border);
    border-radius:14px;
    padding:10px;
    border-color:#3741af;
    transition: border-color .2s, transform .2s;
  }
  .card: hover{border-color:#37414f;}

  .card h2{
    font-size:13px;
    text-transform:uppercase;
    letter-spacing:.8px;
    color:var(--muted);
    font-weight:600;
    margin-bottom:14px;
  }

  .stat{
    font-size:27px;
    font-weight:700;
    line-height:1.1;

    display: flex;
    justify-content: right;
    align-items: right;
   }
  .delta{font-size:12.5px;margin-top:6px;color:var(--accent-2)}
  .delta.down{color:var(--danger)}

  .bar-track{height:7px;background:var(--panel-2);border-radius:99px;overflow:hidden;margin-top:12px}
  .bar-fill{height:100%;border-radius:99px;background:linear-gradient(90deg,var(--accent),#8b5cf6)}

  /* chart */
  .chart{display:flex;align-items:flex-end;gap:10px;height:170px;margin-top:8px}
  .chart div{
    flex:1;border-radius:6px 6px 3px 3px;
    background:linear-gradient(180deg,var(--accent),#2a4b8d);
  }
  .chart-legend{display:flex;justify-content:space-between;font-size:11.5px;color:var(--muted);margin-top:10px}

  /* list */
  ul{list-style:none}
  li{
    display:flex;align-items:center;gap:10px;
    padding:10px 0;border-bottom:1px solid var(--border);font-size:13.5px;
  }
  li:last-child{border-bottom:none}
  .dot{width:8px;height:8px;border-radius:50%;flex:none}
  .t{color:var(--muted);margin-left:auto;font-size:11.5px}

  table{width:100%;border-collapse:collapse;font-size:13.5px}
  th{
    text-align:left;color:var(--muted);font-weight:600;font-size:11.5px;
    text-transform:uppercase;letter-spacing:.6px;padding:8px 10px;border-bottom:1px solid var(--border);
  }
  td{
    font-size:9px;
    padding:0px 0px;
    border-bottom:1px solid var(--border);

  }
  tr:last-child td{border-bottom:none}
  tbody tr:hover{background:var(--panel-2)}
  .tag{padding:3px 9px;border-radius:99px;font-size:11.5px;font-weight:600}
  .ok{background:rgba(34,197,94,.14);color:var(--accent-2)}
  .pending{background:rgba(245,158,11,.14);color:var(--warn)}
  .fail{background:rgba(239,68,68,.14);color:var(--danger)}

  footer{margin-top:22px;text-align:center;color:var(--muted);font-size:12.5px}

  @media(max-width:980px){
    .grid{grid-template-columns:repeat(2,1fr);
      grid-template-areas:"a b" "c c" "d d" "e e";}
  }
  @media(max-width:600px){
    body{padding:16px}
    .grid{grid-template-columns:1fr;grid-template-areas:"a" "b" "c" "d" "e";}
    .search{width:100%}
  }

  input[type=range] {
    width: 100%;
    margin: 5px 0px;
  }


.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #336;
  -webkit-transition: .4s;
  transition: .4s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  -webkit-transition: .4s;
  transition: .4s;
}

input:checked + .slider {
  background-color: #33F;
}

input:focus + .slider {
  box-shadow: 0 0 1px #2196F3;
}

input:checked + .slider:before {
  -webkit-transform: translateX(26px);
  -ms-transform: translateX(26px);
  transform: translateX(26px);
}

/* Rounded sliders */
.slider.round {
  border-radius: 34px;
}

.slider.round:before {
  border-radius: 50%;
}

.led-blue {
  width: 24px;
  height: 24px;
  opacity: 1.0;
  background-color: #24E0EE;
  border-radius: 50%;
  box-shadow: rgba(0, 0, 0, 0.2) 0 -1px 7px 1px, inset #006 0 -1px 9px, #3F8CFF 0 2px 14px;
}


  </style>
  <header>
    <div class="brand">
      <div class="logo">RIO</div>
      <div>
        <h1>RIO - MQTT</h1>
        <p>Overview</p>
      </div>
    </div>
    <div class="head-actions">
    </div>
  </header>

  <main class="grid">
""")

        for plugin_instance in self.project.plugin_instances:
            if self.instance.instances_name not in {plugin_instance.master, plugin_instance.gmaster}:
                continue
            signals = plugin_instance.signals()
            signal_found = False
            for signal_name, signal_config in signals.items():
                if signal_config.get("no_convert") is True:
                    continue
                if signal_config.get("expansion") is True:
                    continue
                signal_found = True
            if not signal_found:
                continue

            for signal_name, signal_config in signals.items():
                if signal_config.get("no_convert") is True:
                    continue
                if signal_config.get("expansion") is True:
                    continue
                virtual = signal_config.get("virtual")
                if virtual:
                    continue
                halname = signal_config["halname"]
                direction = signal_config["direction"]
                boolean = signal_config.get("bool")
                unit = signal_config.get("unit")
                vmin = signal_config.get("min", 0)
                vmax = signal_config.get("max", 1000)

                output.append('    <section class="card">')
                output.append(f"      <h2>{plugin_instance.instances_name} - {signal_name}</h2>")

                if direction == "output":
                    if boolean:
                        output.append('      <div class="stat">&nbsp;</div>')
                        output.append(f'      <div class="stat"><label class="switch"><input type="checkbox" id="{self.mqttname(halname)}_set" /><span class="slider round"></span></label></div>')
                    else:
                        output.append(f'      <div class="stat"><b id="{self.mqttname(halname)}">0</b>{unit or ""}</div>')
                        output.append(f'      <div class="range"><input width="100%" type="range" min="{vmin}" max="{vmax}" id="{self.mqttname(halname)}_set" value="0" /></div>')
                elif boolean:
                    output.append('      <div class="stat">&nbsp;</div>')
                    output.append(f'      <div class="stat"><div class="led-blue" id="{self.mqttname(halname)}"></div></div>')
                else:
                    output.append(f'      <div class="stat"><b id="{self.mqttname(halname)}">0</b>{unit or ""}</div>')
                    output.append(f'      <div class="bar-track"><div id="{self.mqttname(halname)}_p" class="bar-fill" style="width:68%"></div></div>')

                output.append("    </section>")

        output.append("")
        output.append('    <script type="text/javascript">')
        output.append('        var clientID = "ID-" + Math.round(Math.random() * 1000);')
        output.append('        var client = new Paho.MQTT.Client("127.0.0.1", 9001, clientID);')
        output.append("")

        for plugin_instance in self.project.plugin_instances:
            if self.instance.instances_name not in {plugin_instance.master, plugin_instance.gmaster}:
                continue
            signals = plugin_instance.signals()
            if not signals:
                continue
            for signal_name, signal_config in signals.items():
                if signal_config.get("no_convert") is True:
                    continue
                if signal_config.get("expansion") is True:
                    continue
                halname = signal_config["halname"]
                direction = signal_config["direction"]
                boolean = signal_config.get("bool")
                virtual = signal_config.get("virtual")
                if virtual:
                    continue
                if direction == "output":
                    vmin = signal_config.get("min", 0)
                    output.append(f'        document.getElementById("{self.mqttname(halname)}_set").addEventListener("change", publish, false);')
                    output.append(f'        document.getElementById("{self.mqttname(halname)}_set").addEventListener("input", publish, false);')
                    # if vmin < 0:
                    #    output.append(f'        document.getElementById("{self.mqttname(halname)}_zero").addEventListener("click", publish, false);')

        output.append("        client.connect({onSuccess:onConnect});")
        output.append("        client.onMessageArrived = onMessage;")
        output.append("")
        output.append("        function onConnect() {")
        output.append('            console.log("connected");')

        for plugin_instance in self.project.plugin_instances:
            if self.instance.instances_name not in {plugin_instance.master, plugin_instance.gmaster}:
                continue
            signals = plugin_instance.signals()
            if not signals:
                continue
            for signal_name, signal_config in signals.items():
                if signal_config.get("no_convert") is True:
                    continue
                if signal_config.get("expansion") is True:
                    continue
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
            var eid = this.attributes.id.value.replace("_zero", "");
            var topic = eid.replace("_set", "");
            element = document.getElementById(eid);
            var value = "0";
            if (element.attributes.type.value == "checkbox") {
                if (element.checked) {
                    value = "1";
                }
            } else {
                value = element.value;
            }
            console.log("publish", topic, value);

            fb_element = document.getElementById(topic);
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
            if self.instance.instances_name not in {plugin_instance.master, plugin_instance.gmaster}:
                continue
            signals = plugin_instance.signals()
            if not signals:
                continue
            for signal_name, signal_config in signals.items():
                if signal_config.get("no_convert") is True:
                    continue
                if signal_config.get("expansion") is True:
                    continue
                halname = signal_config["halname"]
                direction = signal_config["direction"]
                boolean = signal_config.get("bool")
                virtual = signal_config.get("virtual")
                if virtual:
                    continue
                if direction == "input":
                    output.append(f'            if (message.destinationName == "{self.mqttname(halname)}") {{')
                    fformat = signal_config.get("format")
                    if fformat and "." in fformat and fformat[-1] == "f":
                        digits = fformat[:-1].split(".")[-1].lstrip("0")
                        output.append(f'                document.getElementById("{self.mqttname(halname)}").innerHTML = parseFloat(message.payloadString).toFixed({digits});')
                    elif boolean:
                        output.append('                if (message.payloadString == "1") {')
                        output.append(f'                    document.getElementById("{self.mqttname(halname)}").style.opacity = "1.0";')
                        output.append(f'                    document.getElementById("{self.mqttname(halname)}").style.boxShadow = "rgba(0, 0, 0, 0.2) 0 -1px 7px 1px, inset #006 0 -1px 9px, #3F8CFF 0 2px 14px";')
                        output.append("                } else {")
                        output.append(f'                    document.getElementById("{self.mqttname(halname)}").style.opacity = "0.2";')
                        output.append(f'                    document.getElementById("{self.mqttname(halname)}").style.boxShadow = "";')

                        output.append("                }")
                    else:
                        output.append(f'                document.getElementById("{self.mqttname(halname)}").innerHTML = message.payloadString;')

                    if not boolean:
                        vmin = signal_config.get("min", 0)
                        vmax = signal_config.get("max", 1000)
                        scale = 100 / (vmax - vmin)
                        output.append(f'                document.getElementById("{self.mqttname(halname)}_p").style.width = ((parseFloat(message.payloadString) - {vmin}) * {scale}).toString() + "%";')

                    output.append("            }")
        output.append("        }")
        output.append("")
        output.append("    </script>")
        output.append("  </body>")
        output.append("</html>")
        output.append("")
        open(os.path.join(self.mqtt_path, "test.html"), "w").write("\n".join(output))

    def nodered_template(self):
        template = [
            {
                "id": "1a46187fa5abebc0",
                "type": "tab",
                "label": "RIO-MQTT",
                "disabled": False,
                "info": "",
                "env": [],
            }
        ]
        template.append(
            {
                "id": "0ae84448796161ae",
                "type": "mqtt-broker",
                "name": "",
                "broker": "192.168.10.23",
                "port": 1883,
                "clientid": "",
                "autoConnect": True,
                "usetls": False,
                "protocolVersion": 4,
                "keepalive": 60,
                "cleansession": True,
                "autoUnsubscribe": True,
                "birthTopic": "",
                "birthQos": "0",
                "birthRetain": "false",
                "birthPayload": "",
                "birthMsg": {},
                "closeTopic": "",
                "closeQos": "0",
                "closeRetain": "false",
                "closePayload": "",
                "closeMsg": {},
                "willTopic": "",
                "willQos": "0",
                "willRetain": "false",
                "willPayload": "",
                "willMsg": {},
                "userProps": "",
                "sessionExpiry": "",
            }
        )
        py_in = 200
        py_out = 200
        nid = 0x370FD489CAD2511E
        for plugin_instance in self.project.plugin_instances:
            if self.instance.instances_name not in {plugin_instance.master, plugin_instance.gmaster}:
                continue
            signals = plugin_instance.signals()
            if not signals:
                continue
            for signal_name, signal_config in signals.items():
                if signal_config.get("no_convert") is True:
                    continue
                if signal_config.get("expansion") is True:
                    continue
                halname = signal_config["halname"]
                direction = signal_config["direction"]
                virtual = signal_config.get("virtual")
                if virtual:
                    continue
                if direction == "input":
                    template.append(
                        {
                            "id": f"{nid:x}",
                            "type": "mqtt in",
                            "z": "1a46187fa5abebc0",
                            "name": "",
                            "topic": self.mqttname(halname),
                            "qos": "2",
                            "datatype": "auto-detect",
                            "broker": "0ae84448796161ae",
                            "nl": False,
                            "rap": True,
                            "rh": 0,
                            "inputs": 0,
                            "x": 400,
                            "y": py_in,
                            "wires": [],
                        }
                    )
                    py_in += 60
                else:
                    template.append(
                        {
                            "id": f"{nid:x}",
                            "type": "mqtt out",
                            "z": "1a46187fa5abebc0",
                            "name": "",
                            "topic": self.mqttname(halname),
                            "qos": "",
                            "retain": "",
                            "respTopic": "",
                            "contentType": "",
                            "userProps": "",
                            "correl": "",
                            "expiry": "",
                            "broker": "0ae84448796161ae",
                            "x": 2000,
                            "y": py_out,
                            "wires": [],
                        }
                    )
                    py_out += 60
                nid += 1
        open(os.path.join(self.mqtt_path, "node-red.json"), "w").write(json.dumps(template, indent=2))

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
            if self.instance.instances_name not in {plugin_instance.master, plugin_instance.gmaster}:
                continue
            for signal_name, signal_config in plugin_instance.signals().items():
                if signal_config.get("no_convert") is True:
                    continue
                if signal_config.get("expansion") is True:
                    continue
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
        output.append("    char tmp_str[64];")
        output.append("")
        output.append("    data = (data_t*)malloc(sizeof(data_t));")
        output.append("    register_signals();")
        output.append("    interface_init(argc, argv);")
        output.append("")

        for direction in ("input", "output"):
            mapping = {
                "input": "sub",
                "output": "pub",
            }
            output.append(f'    printf("{mapping.get(direction)}:\\n");')
            for plugin_instance in self.project.plugin_instances:
                if self.instance.instances_name not in {plugin_instance.master, plugin_instance.gmaster}:
                    continue
                if plugin_instance.TYPE == "frameio":
                    continue
                for signal_name, signal_config in plugin_instance.signals().items():
                    if signal_config.get("no_convert") is True:
                        continue
                    if signal_config.get("expansion") is True:
                        continue
                    halname = signal_config["halname"]
                    varname = signal_config["varname"]
                    boolean = signal_config.get("bool")
                    virtual = signal_config.get("virtual")
                    if virtual:
                        continue
                    if direction == signal_config["direction"]:
                        output.append(f'    printf("  {varname}\\n");')
            output.append('    printf("\\n");')

        output.append("")
        output.append("    MQTTClient client;")
        output.append("    MQTTClient_connectOptions conn_opts = MQTTClient_connectOptions_initializer;")
        output.append("    MQTTClient_message pubmsg = MQTTClient_message_initializer;")
        output.append("    MQTTClient_deliveryToken token;")
        output.append("    int rc;")
        output.append("")
        output.append("    const char* uri = (argc > 2) ? argv[2] : MQTT_ADDRESS;")
        output.append('    printf("Using MQTT-Server at %s\\n", uri);')
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
            if self.instance.instances_name not in {plugin_instance.master, plugin_instance.gmaster}:
                continue
            for signal_name, signal_config in plugin_instance.signals().items():
                if signal_config.get("no_convert") is True:
                    continue
                if signal_config.get("expansion") is True:
                    continue
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
        output.append("        rio_readwrite(NULL, 0);")
        for plugin_instance in self.project.plugin_instances:
            if self.instance.instances_name not in {plugin_instance.master, plugin_instance.gmaster}:
                continue
            if plugin_instance.TYPE == "frameio":
                continue
            for signal_name, signal_config in plugin_instance.signals().items():
                if signal_config.get("no_convert") is True:
                    continue
                if signal_config.get("expansion") is True:
                    continue
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
        output.append("        // 10ms interval")
        output.append("        rtapi_delay(10 * 1000000);")
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
        output.append("$DIRNAME/mqttbridge $@")
        output.append("")
        output.append("")
        os.makedirs(self.mqtt_path, exist_ok=True)
        target = os.path.join(self.mqtt_path, "start.sh")
        open(target, "w").write("\n".join(output))
        os.chmod(target, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

    def mqttname(self, halname):
        mqttname = halname.replace(".", "/").replace("-", "_")
        return f"{self.prefix}/{mqttname}"

    def vinit(self, vname, vtype, halstr=None, vdir="input", default=0):
        vtype = self.typemap.get(vtype, vtype)
        return f"    data->{vname} = ({vtype}*)malloc(sizeof({vtype}));\n    *data->{vname} = {default};"
