import math


table_len = 64


for n in range(table_len):
    # val = round(127 * math.sin(2 * n * math.pi / table_len) + 127, 0)
    val = 127 * math.sin(2 * n * math.pi / table_len) + 127
    print(f"        sine_tbl[{n}] = {int(val)};")
