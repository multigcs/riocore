# Optional MQTT transport following the standard MTConnect MQTT binding.
#
# Publishes the standard MTConnect response documents to the standard topics:
#   <prefix>/Probe/<uuid>              (retained)
#   <prefix>/Current/<uuid>           (at the sample interval)
#   <prefix>/Sample/<uuid>            (when new observations arrive)
#   <prefix>/Asset/<uuid>/<assetId>   (retained, on asset change)
#
# Reuses paho-mqtt, already used by src/hal/user_comps/mqtt-publisher.py.
# Works with both paho-mqtt 1.x and 2.x.

import json

from . import ha as ha_mod


class MqttAgent:
    def __init__(self, agent, broker="localhost", port=1883, prefix="MTConnect",
                 username=None, password=None, client_id="linuxcnc-mtconnect",
                 ha_discovery=False, ha_prefix="homeassistant"):
        try:
            import paho.mqtt.client as mqtt
        except ModuleNotFoundError:
            print("error: Missing Python module paho.mqtt.")
            print("error: Arch: 'sudo pacman -S python-paho-mqtt'; "
                  "Debian: 'sudo apt install python3-paho-mqtt'.")
            raise
        self.agent = agent
        self.prefix = prefix.rstrip("/")
        self.uuid = agent.config.uuid
        self._last_sample_seq = 1
        self._last_asset_sig = None

        self.ha = ha_discovery
        self.ha_prefix = ha_prefix.rstrip("/")
        self._ha_state_topic = "%s/ha/%s/state" % (self.prefix, self.uuid)
        self._ha_avail_topic = "%s/ha/%s/availability" % (self.prefix, self.uuid)
        self._ha_sensors = (ha_mod.build_sensors(agent.model, agent.config)
                            if self.ha else [])

        # paho 2.x requires an explicit callback API version; 1.x has no such arg.
        try:
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1,
                                      client_id=client_id)
        except AttributeError:
            self.client = mqtt.Client(client_id=client_id)
        if username:
            self.client.username_pw_set(username, password)
        if self.ha:  # Last Will so HA marks the device unavailable if we vanish
            self.client.will_set(self._ha_avail_topic, "offline", retain=True)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.connect_async(broker, port, keepalive=60)
        self.client.loop_start()
        print("info: MQTT connecting to %s:%d as '%s' (prefix '%s')"
              % (broker, port, username or "anonymous", self.prefix))

    def _topic(self, kind, suffix=None):
        base = "%s/%s/%s" % (self.prefix, kind, self.uuid)
        return "%s/%s" % (base, suffix) if suffix else base

    def _on_connect(self, client, userdata, flags, rc, *args):
        if rc == 0:
            print("info: MQTT connected; publishing retained Probe to %s"
                  % self._topic("Probe"))
            self.publish_probe()
            self.publish_assets()
            if self.ha:
                self._publish_ha_discovery()
                self.client.publish(self._ha_avail_topic, "online", retain=True)
                self.publish_ha()
                print("info: HA MQTT discovery published under %s/sensor/%s/*"
                      % (self.ha_prefix, ha_mod.node_id(self.agent.config)))
        else:
            hint = {1: "unacceptable protocol version", 2: "identifier rejected",
                    3: "broker unavailable", 4: "bad username or password",
                    5: "not authorized (anonymous refused / bad credentials)"}
            print("error: MQTT connect failed (rc=%s: %s)"
                  % (rc, hint.get(int(rc) if str(rc).isdigit() else -1, "see broker log")))

    def _on_disconnect(self, client, userdata, rc, *args):
        print("warning: MQTT disconnected (rc=%s)" % rc)

    def publish_probe(self):
        self.client.publish(self._topic("Probe"), self.agent.probe_document(),
                            retain=True)

    def publish_current(self):
        self.client.publish(self._topic("Current"), self.agent.current_document())

    def publish_sample(self):
        first, nxt = self.agent.buffer.first_sequence, self.agent.buffer.next_sequence
        if nxt <= self._last_sample_seq:
            return
        start = max(self._last_sample_seq, first)
        self.client.publish(self._topic("Sample"),
                            self.agent.sample_document(start, nxt - start))
        self._last_sample_seq = nxt

    def publish_assets(self):
        assets = self.agent.source.tool_assets()
        sig = tuple((a.asset_id, a.pocket, a.in_spindle) for a in assets)
        if sig == self._last_asset_sig:
            return
        self._last_asset_sig = sig
        doc = self.agent.assets_document()
        for asset in assets:
            self.client.publish(self._topic("Asset", asset.asset_id), doc,
                                retain=True)

    def _publish_ha_discovery(self):
        node = ha_mod.node_id(self.agent.config)
        for s in self._ha_sensors:
            topic = "%s/sensor/%s/%s/config" % (self.ha_prefix, node, s["key"])
            payload = ha_mod.discovery_payload(s, self.agent.config,
                                               self._ha_state_topic, self._ha_avail_topic)
            self.client.publish(topic, json.dumps(payload), retain=True)

    def publish_ha(self):
        if not self.ha:
            return
        self.client.publish(self._ha_state_topic,
                            ha_mod.state_json(self.agent.latest_values(), self._ha_sensors),
                            retain=True)

    def stop(self):
        if self.ha:
            self.client.publish(self._ha_avail_topic, "offline", retain=True)
        self.client.loop_stop()
        self.client.disconnect()
