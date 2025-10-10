import json

config = {
    "name": "Parport",
    "description": "PC with parallel port",
    "comment": "",
    "url": "",
    "type": "parport",
    "slots": [
        {"name": "PORT0", "comment": "", "default": "", "pins": {}},
        {"name": "PORT1", "comment": "", "default": "", "pins": {}},
    ],
}


mode_outputs = {
    "in": [1, 14, 16, 17],
    "out": [1, 2, 3, 4, 5, 6, 7, 8, 9, 14, 16, 17],
    "x": [2, 3, 4, 5, 6, 7, 8, 9],
}
diff = 26.1

for port_n in range(2):
    for n in range(17):
        pname = f"P{n + 1}"

        px = 57
        py = n * diff + 88 + (port_n * 491)
        if n > 12:
            px += diff
            py -= 13 * diff
            py += diff / 2

        comments = []
        outs = 0
        ins = 0
        for mode in mode_outputs:
            if n + 1 in mode_outputs[mode]:
                comments.append(f"{mode}:out")
                outs += 1
            else:
                comments.append(f"{mode}:in")
                ins += 1

        direction = "all"
        if outs == 3:
            direction = "output"
            comments = []
        if ins == 3:
            direction = "input"
            comments = []
        config["slots"][port_n]["pins"][pname] = {"pin": f"{port_n}:{(n + 1)}", "comment": "|".join(comments), "pos": [px, py], "direction": direction}

print(json.dumps(config, indent=4))
