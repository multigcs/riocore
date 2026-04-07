#!/usr/bin/env python3
#
#

import argparse
import json
import socket

import linuxcnc

parser = argparse.ArgumentParser()
parser.add_argument("--port", help="listen port", type=int, default=1000)
parser.add_argument("--name", help="component name", type=str, default="rmpg")
args = parser.parse_args()


try:
    import hal

    h = hal.component(args.name)
    h.newpin("axis.x.jog-counts", hal.HAL_S32, hal.HAL_OUT)
    h.newpin("axis.y.jog-counts", hal.HAL_S32, hal.HAL_OUT)
    h.newpin("axis.z.jog-counts", hal.HAL_S32, hal.HAL_OUT)
    h.newpin("axis.x.jog-scale", hal.HAL_FLOAT, hal.HAL_IN)
    h.newpin("axis.y.jog-scale", hal.HAL_FLOAT, hal.HAL_IN)
    h.newpin("axis.z.jog-scale", hal.HAL_FLOAT, hal.HAL_IN)
    for overwrite in ("feed-override", "rapid-override", "spindle.0.override", "max-velocity"):
        h.newpin(f"{overwrite}.counts", hal.HAL_S32, hal.HAL_OUT)
        h.newpin(f"{overwrite}.value", hal.HAL_FLOAT, hal.HAL_IN)
    h.newpin("sw1", hal.HAL_BIT, hal.HAL_OUT)
    h.newpin("sw1-not", hal.HAL_BIT, hal.HAL_OUT)

    h.ready()
    no_hal = False

    # http://linuxcnc.org/docs/master/html/de/config/python-interface.html
    s = linuxcnc.stat()
    c = linuxcnc.command()

except Exception:
    no_hal = True
    h = {}
    h["axis.x.jog-counts"] = 0
    h["axis.y.jog-counts"] = 0
    h["axis.z.jog-counts"] = 0
    h["axis.x.jog-scale"] = 0.1
    h["axis.y.jog-scale"] = 0.1
    h["axis.z.jog-scale"] = 0.1
    for overwrite in ("feed-override", "rapid-override", "spindle.0.override", "max-velocity"):
        h[f"{overwrite}.counts"] = 0
        h[f"{overwrite}.value"] = 50.0
    h["sw1"] = 0
    h["sw1-not"] = 1


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the socket to the port
server_address = ("0.0.0.0", args.port)
print(f"{args.name}: starting on port {args.port}")
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)


def ok_for_mdi():
    # return not s.estop and s.enabled and (s.homed.count(1) == s.joints) and (s.interp_state == linuxcnc.INTERP_IDLE)
    return not s.estop and s.enabled and (s.interp_state == linuxcnc.INTERP_IDLE)


while True:
    # Wait for a connection

    connection, client_address = sock.accept()
    try:
        print(f"{args.name}: connection from {client_address}")
        while True:
            data = connection.recv(12000)
            if data:
                cmd = json.loads(data.decode())
                result = {"error": "unknown"}
                name = cmd.get("name", "")
                if name == "version":
                    result = {"version": 0.1}
                elif name == "mdi":
                    s.poll()
                    gcode = cmd["gcode"]
                    print("#gcode", gcode)

                    if ok_for_mdi():
                        c.mode(linuxcnc.MODE_MDI)
                        c.wait_complete()
                        c.mdi(gcode)
                        result = {"succes": "ok"}
                    else:
                        print("#mdi not ready")
                        result = {"error": "mdi not ready"}

                elif name == "read":
                    result = h.getpins()
                elif name == "write":
                    data = cmd["data"]
                    result = {}
                    halpins = h.getpins()
                    for key, value in data.items():
                        if key in halpins:
                            if type(value) is type(h[key]):
                                h[key] = value
                            else:
                                result["error"] = "wrong type"
                        else:
                            result["error"] = "unknown halpin"
                    result = h.getpins()
                connection.sendall(json.dumps(result).encode())
            else:
                break

    finally:
        print(f"{args.name}: close connection: {client_address}")
        connection.close()
