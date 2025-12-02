#!/usr/bin/env python3
#
# Source: https://gist.github.com/ciniml/e02f4cc9b00f30d950cd2a787a1ea8d3
#

import sys

input_path = sys.argv[1]
output_path = sys.argv[2]

with open(input_path, "r") as input_file:
    with open(output_path, "wb") as output_file:
        for line in iter(input_file.readline, ""):  # type: str
            line = line.strip()
            if line.startswith("//"):
                continue
            buffer = bytearray(1)
            for byte_index in range(0, len(line), 8):
                value = 0
                for bit_index in range(8):
                    bit = line[byte_index + bit_index]
                    value = (value << 1) | (1 if bit == "1" else 0)
                buffer[0] = value
                output_file.write(buffer)
