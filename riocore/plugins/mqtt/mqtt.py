#!/usr/bin/env python3
#
#

import argparse
import sys

import hal
import paho.mqtt.client as mqtt


def main(args):
    h = hal.component(args.name)
    for part in args.config.split(","):
        _topic, vtype, pin = part.split(":")
        if vtype == "float":
            h.newpin(pin, hal.HAL_FLOAT, hal.HAL_OUT)
        elif vtype == "bit":
            h.newpin(pin, hal.HAL_BIT, hal.HAL_OUT)
    h.ready()

    def on_connect(mqttc, obj, flags, reason_code):
        if reason_code == 0:
            print("MQTT: connected")
        else:
            print(f"MQTT: error {reason_code}")

    def on_message(mqttc, obj, msg):
        for part in args.config.split(","):
            topic, vtype, pin = part.strip().split(":")
            if topic == msg.topic:
                if vtype == "float":
                    h[pin] = float(msg.payload.decode())
                elif vtype == "bit":
                    h[pin] = bool(msg.payload.decode())

    mqttc = mqtt.Client()
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.connect(args.server, args.port, 60)

    for part in args.config.split(","):
        topic, _vtype, _pin = part.strip().split(":")
        mqttc.subscribe(topic)

    mqttc.loop_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", help="instance-name", type=str, default="mqtt")
    parser.add_argument("-s", "--server", help="mqtt server", type=str, default="localhost")
    parser.add_argument("-p", "--port", help="mqtt port", type=int, default=1883)
    parser.add_argument("-c", "--config", help="config string", type=str, default="")
    args = parser.parse_args()

    try:
        main(args)
    except KeyboardInterrupt:
        print("exiting mqtt.py")
        sys.exit(130)
