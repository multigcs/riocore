class i2c_device:
    options = {
        "info": "hd44780 over i2c",
        "description": "",
        "addresses": ["0x20", "0x21", "0x22", "0x23", "0x24", "0x25", "0x26", "0x27"],
        "config": {},
    }

    def __init__(self, setup, system_setup={}):
        self.system_setup = system_setup
        self.name = setup["name"]
        self.addr = setup["address"]
        self.INTERFACE = {}
        self.SIGNALS = {}
        self.INTERFACE[f"{self.name}_char"] = {
            "size": 16,
            "direction": "output",
        }
        self.INTERFACE[f"{self.name}_valid"] = {
            "size": 1,
            "direction": "input",
        }
        self.SIGNALS[f"{self.name}_char"] = {
            "direction": "output",
            "min": 0,
            "max": 65535,
        }
        self.SIGNALS[f"{self.name}_valid"] = {
            "direction": "input",
            "bool": True,
        }

        self.PARAMS = {}

        # commands
        LCD_CLEAR_DISPLAY = 0x01
        LCD_RETURN_HOME = 0x02
        LCD_ENTRY_MODE_SET = 0x04
        LCD_DISPLAY_CONTROL = 0x08
        LCD_CURSOR_SHIFT = 0x10
        LCD_FUNCTION_SET = 0x20
        LCD_SET_CGRAM_ADDR = 0x40
        LCD_SET_DDRAM_ADDR = 0x80

        # flags for display entry mode
        LCD_ENTRY_RIGHT = 0x00
        LCD_ENTRY_LEFT = 0x02
        LCD_ENTRY_SHIFT_INCREMENT = 0x01
        LCD_ENTRY_SHIFT_DECREMENT = 0x00

        # flags for display on/off control
        LCD_DISPLAY_ON = 0x04
        LCD_DISPLAY_OFF = 0x00
        LCD_CURSOR_ON = 0x02
        LCD_CURSOR_OFF = 0x00
        LCD_BLINK_ON = 0x01
        LCD_BLINK_OFF = 0x00

        # flags for display/cursor shift
        LCD_DISPLAY_MOVE = 0x08
        LCD_CURSOR_MOVE = 0x00
        LCD_MOVE_RIGHT = 0x04
        LCD_MOVE_LEFT = 0x00

        # flags for function set
        LCD_8BIT_MODE = 0x10
        LCD_4BIT_MODE = 0x00
        LCD_2_LINE = 0x08
        LCD_1_LINE = 0x00
        LCD_5x10DOTS = 0x04
        LCD_5x8DOTS = 0x00

        LCD_BACKLIGHT_ON = 0x08
        LCD_BACKLIGHT_OFF = 0x00

        self.EN = 1 << 2  # Enable bit
        self.RW = 1 << 1  # Read/Write bit
        self.RS = 1 << 3  # Register select bit

        ctrl = (1 << 3) | (0 << 2) | (0 << 1) | (0 << 0)
        ctrl_en = (1 << 3) | (1 << 2) | (0 << 1) | (0 << 0)

        dat = (1 << 3) | (0 << 2) | (0 << 1) | (1 << 0)
        dat_en = (1 << 3) | (1 << 2) | (0 << 1) | (1 << 0)

        def lcd_ctrl(cmd):
            ret = []
            ret.append(
                {
                    "mode": "write",
                    "value": f"8'd{(cmd>>4)}",
                    "bytes": 1,
                }
            )
            ret.append(
                {
                    "mode": "write",
                    "value": f"8'd{(cmd>>4)|self.EN}",
                    "bytes": 1,
                }
            )
            ret.append(
                {
                    "mode": "write",
                    "value": f"8'd{(cmd>>4)}",
                    "bytes": 1,
                }
            )
            ret.append(
                {
                    "mode": "write",
                    "value": f"8'd{(cmd&0x0f)}",
                    "bytes": 1,
                }
            )
            ret.append(
                {
                    "mode": "write",
                    "value": f"8'd{(cmd&0x0f)|self.EN}",
                    "bytes": 1,
                }
            )
            ret.append(
                {
                    "mode": "write",
                    "value": f"8'd{(cmd&0x0f)}",
                    "bytes": 1,
                }
            )
            ret.append(
                {
                    "mode": "delay",
                    "ms": 2,
                }
            )
            self.INITS += ret

        self.rows = 4
        self.cols = 20
        self.row_starts = [0x00, 0x40, 0x00 + self.cols, 0x40 + self.cols]
        self.row = 0
        self.col = 0

        self.INITS = [
            {
                "mode": "delay",
                "ms": 20,
            },
            {
                "mode": "write",
                "value": f"{{4'd{0x03}, 4'd{ctrl}}}",
                "bytes": 1,
            },
            {
                "mode": "write",
                "value": f"{{4'd{0x03}, 4'd{ctrl_en}}}",
                "bytes": 1,
            },
            {
                "mode": "write",
                "value": f"{{4'd{0x03}, 4'd{ctrl}}}",
                "bytes": 1,
            },
            {
                "mode": "delay",
                "ms": 5,
            },
            {
                "mode": "write",
                "value": f"{{4'd{0x03}, 4'd{ctrl_en}}}",
                "bytes": 1,
            },
            {
                "mode": "write",
                "value": f"{{4'd{0x03}, 4'd{ctrl}}}",
                "bytes": 1,
            },
            {
                "mode": "delay",
                "ms": 1,
            },
            {
                "mode": "write",
                "value": f"{{4'd{0x03}, 4'd{ctrl_en}}}",
                "bytes": 1,
            },
            {
                "mode": "write",
                "value": f"{{4'd{0x03}, 4'd{ctrl}}}",
                "bytes": 1,
            },
            {
                "mode": "delay",
                "ms": 1,
            },
        ]

        self.bl = LCD_BACKLIGHT_ON

        if self.rows > 1:
            lcd_ctrl(LCD_FUNCTION_SET | LCD_4BIT_MODE | LCD_2_LINE | LCD_5x8DOTS | self.bl)  # 4bit
        else:
            lcd_ctrl(LCD_FUNCTION_SET | LCD_4BIT_MODE | LCD_1_LINE | LCD_5x8DOTS | self.bl)  # 4bit

        lcd_ctrl(LCD_ENTRY_MODE_SET | LCD_ENTRY_LEFT | LCD_ENTRY_SHIFT_DECREMENT)
        lcd_ctrl(LCD_DISPLAY_CONTROL | LCD_DISPLAY_OFF | LCD_CURSOR_OFF | LCD_BLINK_OFF)
        lcd_ctrl(LCD_CLEAR_DISPLAY)
        lcd_ctrl(LCD_RETURN_HOME)
        lcd_ctrl(LCD_DISPLAY_CONTROL | LCD_DISPLAY_ON | LCD_CURSOR_OFF | LCD_BLINK_OFF)

        self.INITS.append(
            {
                "mode": "delay",
                "ms": 2,
            }
        )

        self.STEPS = [
            {
                "mode": "lcd",
                "var": f"{self.name}_char",
                "bytes": 2,
            },
        ]

    def convert(self, signal_name, signal_setup, value):
        if signal_name.endswith("_valid"):
            return value

        text = [
            f"1 A={value:>5} y={value:>5} xx",
            f"2 B={value:>5} y={value:>5} xx",
            f"3 C={value:>5} y={value:>5} xx",
            f"4 D={value:>5} y={value:>5} xx",
        ]

        addr = self.row_starts[self.row] + self.col
        ch = text[self.row][self.col]
        value = (addr << 8) | (int(ch.encode()[0]))

        print(self.row, self.col, f"0x{addr:x}", ch)

        if self.col < 20 - 1:
            self.col += 1
        else:
            self.col = 0
            if self.row < 4 - 1:
                self.row += 1
            else:
                self.row = 0
        return value
