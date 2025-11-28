
module.exports = {
  output: {
    "modbus0": {
      "txdata": 0,
    },
    "stepdir0": {
      "velocity": 0,
      "enable": 0,
    },
    "stepdir1": {
      "velocity": 0,
      "enable": 0,
    },
    "stepdir2": {
      "velocity": 0,
      "enable": 0,
    },
    "fpga0_wled": {
      "0_green": 0,
      "0_blue": 0,
      "0_red": 0,
    },
    "bitout0": {
      "bit": 0,
    },
  },

  set_tx: function (rio_tx) {
    data = Buffer.alloc(40, 0);
    RX_HEADER = Buffer.from("74697277", "hex").readInt32LE(0);
    VAROUT128_MODBUS0_TXDATA = rio_tx["modbus0"]["txdata"];
    VAROUT32_STEPDIR0_VELOCITY = rio_tx["stepdir0"]["velocity"];
    VAROUT1_STEPDIR0_ENABLE = rio_tx["stepdir0"]["enable"];
    VAROUT32_STEPDIR1_VELOCITY = rio_tx["stepdir1"]["velocity"];
    VAROUT1_STEPDIR1_ENABLE = rio_tx["stepdir1"]["enable"];
    VAROUT32_STEPDIR2_VELOCITY = rio_tx["stepdir2"]["velocity"];
    VAROUT1_STEPDIR2_ENABLE = rio_tx["stepdir2"]["enable"];
    VAROUT1_FPGA0_WLED_0_GREEN = rio_tx["fpga0_wled"]["0_green"];
    VAROUT1_FPGA0_WLED_0_BLUE = rio_tx["fpga0_wled"]["0_blue"];
    VAROUT1_FPGA0_WLED_0_RED = rio_tx["fpga0_wled"]["0_red"];
    VAROUT1_BITOUT0_BIT = rio_tx["bitout0"]["bit"];

    data.writeInt32LE(RX_HEADER, 0);
    if (VAROUT128_MODBUS0_TXDATA) {
        data[4] |= (1<<7);
    }
    data.writeInt32LE(VAROUT32_STEPDIR0_VELOCITY, 20);
    data.writeInt32LE(VAROUT32_STEPDIR1_VELOCITY, 24);
    data.writeInt32LE(VAROUT32_STEPDIR2_VELOCITY, 28);
    if (VAROUT1_STEPDIR0_ENABLE) {
        data[32] |= (1<<7);
    }
    if (VAROUT1_STEPDIR1_ENABLE) {
        data[32] |= (1<<6);
    }
    if (VAROUT1_STEPDIR2_ENABLE) {
        data[32] |= (1<<5);
    }
    if (VAROUT1_FPGA0_WLED_0_GREEN) {
        data[32] |= (1<<4);
    }
    if (VAROUT1_FPGA0_WLED_0_BLUE) {
        data[32] |= (1<<3);
    }
    if (VAROUT1_FPGA0_WLED_0_RED) {
        data[32] |= (1<<2);
    }
    if (VAROUT1_BITOUT0_BIT) {
        data[32] |= (1<<1);
    }
    return data;
  },

  get_rx: function (data) {
    // read buffer
    TX_HEADER = data.readInt32LE(0);
    TITMESTAMP = data.readInt32LE(4);
    MULTIPLEXED_INPUT_VALUE = data.readInt16LE(8);
    MULTIPLEXED_INPUT_ID = data.readUInt8(10);
    if ((data[11] & (1<<7)) != 0) {
        VARIN128_MODBUS0_RXDATA = 1;
    } else {
        VARIN128_MODBUS0_RXDATA = 0;
    }
    VARIN32_STEPDIR0_POSITION = data.readInt32LE(27);
    VARIN32_STEPDIR1_POSITION = data.readInt32LE(31);
    VARIN32_STEPDIR2_POSITION = data.readInt32LE(35);
    if ((data[39] & (1<<7)) != 0) {
        VARIN1_BITIN0_BIT = 1;
    } else {
        VARIN1_BITIN0_BIT = 0;
    }
    if ((data[39] & (1<<6)) != 0) {
        VARIN1_BITIN1_BIT = 1;
    } else {
        VARIN1_BITIN1_BIT = 0;
    }
    if ((data[39] & (1<<5)) != 0) {
        VARIN1_BITIN2_BIT = 1;
    } else {
        VARIN1_BITIN2_BIT = 0;
    }

    input = {
      "modbus0": {
        "rxdata": VARIN128_MODBUS0_RXDATA,
      },
      "stepdir0": {
        "position": VARIN32_STEPDIR0_POSITION,
      },
      "stepdir1": {
        "position": VARIN32_STEPDIR1_POSITION,
      },
      "stepdir2": {
        "position": VARIN32_STEPDIR2_POSITION,
      },
      "bitin0": {
        "bit": VARIN1_BITIN0_BIT,
      },
      "bitin1": {
        "bit": VARIN1_BITIN1_BIT,
      },
      "bitin2": {
        "bit": VARIN1_BITIN2_BIT,
      },
    };

    return input;
  }
};
