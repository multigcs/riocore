#!/usr/bin/env python3
#
#

import argparse
import json
import socket

parser = argparse.ArgumentParser()
parser.add_argument("--port", help="listen port", type=int, default=1000)
parser.add_argument("--name", help="component name", type=str, default="rmpg")
args = parser.parse_args()


try:
    import hal

    h = hal.component(args.name)
    h.newpin("axis.x.jog-counts", hal.HAL_S32, hal.HAL_OUT)
    h.newpin("axis.y.jog-counts", hal.HAL_S32, hal.HAL_OUT)
    h.newpin("axis.x.jog-scale", hal.HAL_FLOAT, hal.HAL_IN)
    h.newpin("axis.y.jog-scale", hal.HAL_FLOAT, hal.HAL_IN)
    h.ready()
    no_hal = False
except Exception:
    no_hal = True
    h = {}
    h["axis.x.jog-counts"] = 0
    h["axis.y.jog-counts"] = 0
    h["axis.x.jog-scale"] = 0.1
    h["axis.y.jog-scale"] = 0.1


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the socket to the port
server_address = ("0.0.0.0", args.port)
print(f"{args.name}: starting on port {args.port}")
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

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
                name = cmd["name"]
                if name == "version":
                    result = {"version": 0.1}
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
                connection.sendall(json.dumps(result).encode())
            else:
                break

    finally:
        print(f"{args.name}: close connection: {client_address}")
        connection.close()
