# Home Assistant MQTT Discovery helper (optional, demo-friendly).
#
# The standard MTConnect MQTT topics carry full XML documents, which Home
# Assistant can't easily parse.  With HA_DISCOVERY enabled, the agent instead
# also:
#   * publishes retained discovery configs under <ha_prefix>/sensor/<node>/<k>/config
#     so HA auto-creates a Device with one sensor per value (no YAML needed), and
#   * publishes a small flat JSON state document the sensors read via value_json.
#
# This is additive; the standard MTConnect topics are still published.

import json

_LIN_UNIT = {"MILLIMETER": "mm", "INCH": "in", "CENTIMETER": "cm"}


def _lin(config):
    return _LIN_UNIT.get(config.linear_units, "mm")


def build_sensors(model, config):
    """Curated, demo-friendly sensor set derived from the machine model."""
    lin = _lin(config)
    sensors = [
        {"key": "execution", "name": "Execution", "icon": "mdi:cog-play"},
        {"key": "mode", "name": "Mode", "icon": "mdi:tune"},
        {"key": "estop", "name": "E-Stop", "icon": "mdi:alert-octagon"},
        {"key": "program", "name": "Program", "icon": "mdi:file-document-outline"},
        {"key": "toolnum", "name": "Tool", "icon": "mdi:screwdriver"},
        {"key": "pathfeed", "name": "Feed rate", "unit": lin + "/s",
         "icon": "mdi:speedometer", "num": True},
        {"key": "spdl_speed", "name": "Spindle", "unit": "RPM",
         "icon": "mdi:fan", "num": True},
    ]
    for a in model.axes:
        low = a.letter.lower()
        icon = "mdi:axis-%s-arrow" % low if low in ("x", "y", "z") else "mdi:axis-arrow"
        sensors.append({"key": "pos_%s" % low, "name": "%s position" % a.letter,
                        "unit": lin if a.kind == "LINEAR" else "°",
                        "icon": icon, "num": True})
    return sensors


def node_id(config):
    return "".join(c if (c.isalnum() or c in "-_") else "_" for c in config.uuid)


def discovery_payload(sensor, config, state_topic, avail_topic):
    payload = {
        "name": sensor["name"],
        "unique_id": "%s_%s" % (config.uuid, sensor["key"]),
        "state_topic": state_topic,
        "value_template": "{{ value_json.%s }}" % sensor["key"],
        "availability_topic": avail_topic,
        "device": {
            "identifiers": [config.uuid],
            "name": config.name,
            "manufacturer": "LinuxCNC",
            "model": "MTConnect",
        },
    }
    if sensor.get("icon"):
        payload["icon"] = sensor["icon"]
    if sensor.get("unit"):
        payload["unit_of_measurement"] = sensor["unit"]
    if sensor.get("num"):
        payload["state_class"] = "measurement"
    return payload


def state_json(values, sensors):
    """Flat JSON of the curated keys; skip missing/UNAVAILABLE/structured."""
    out = {}
    for s in sensors:
        v = values.get(s["key"])
        if v is None or v == "UNAVAILABLE" or isinstance(v, (dict, list)):
            continue
        out[s["key"]] = v
    return json.dumps(out)
