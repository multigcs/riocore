
module.exports = {
  output: {
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
    "board0_wled": {
      "0_green": 0,
      "0_blue": 0,
      "0_red": 0,
    },
  },

  set_tx: function (rio_tx) {
    data = Buffer.alloc(20, 0);
    RX_HEADER = Buffer.from("74697277", "hex").readInt32LE(0);
    VAROUT32_STEPDIR0_VELOCITY = rio_tx["stepdir0"]["velocity"];
    VAROUT1_STEPDIR0_ENABLE = rio_tx["stepdir0"]["enable"];
    VAROUT32_STEPDIR1_VELOCITY = rio_tx["stepdir1"]["velocity"];
    VAROUT1_STEPDIR1_ENABLE = rio_tx["stepdir1"]["enable"];
    VAROUT32_STEPDIR2_VELOCITY = rio_tx["stepdir2"]["velocity"];
    VAROUT1_STEPDIR2_ENABLE = rio_tx["stepdir2"]["enable"];
    VAROUT1_BOARD0_WLED_0_GREEN = rio_tx["board0_wled"]["0_green"];
    VAROUT1_BOARD0_WLED_0_BLUE = rio_tx["board0_wled"]["0_blue"];
    VAROUT1_BOARD0_WLED_0_RED = rio_tx["board0_wled"]["0_red"];

    data.writeInt32LE(RX_HEADER, 0);
    data.writeInt32LE(VAROUT32_STEPDIR0_VELOCITY, 4);
    data.writeInt32LE(VAROUT32_STEPDIR1_VELOCITY, 8);
    data.writeInt32LE(VAROUT32_STEPDIR2_VELOCITY, 12);
    if (VAROUT1_BOARD0_WLED_0_GREEN) {
        data[16] |= (1<<7);
    }
    if (VAROUT1_BOARD0_WLED_0_BLUE) {
        data[16] |= (1<<6);
    }
    if (VAROUT1_BOARD0_WLED_0_RED) {
        data[16] |= (1<<5);
    }
    if (VAROUT1_STEPDIR0_ENABLE) {
        data[16] |= (1<<4);
    }
    if (VAROUT1_STEPDIR1_ENABLE) {
        data[16] |= (1<<3);
    }
    if (VAROUT1_STEPDIR2_ENABLE) {
        data[16] |= (1<<2);
    }
    return data;
  },

  get_rx: function (data) {
    // read buffer
    TX_HEADER = data.readInt32LE(0);
    TITMESTAMP = data.readInt32LE(4);
    VARIN32_STEPDIR0_POSITION = data.readInt32LE(8);
    VARIN32_STEPDIR1_POSITION = data.readInt32LE(12);
    VARIN32_STEPDIR2_POSITION = data.readInt32LE(16);

    input = {
      "stepdir0": {
        "position": VARIN32_STEPDIR0_POSITION,
      },
      "stepdir1": {
        "position": VARIN32_STEPDIR1_POSITION,
      },
      "stepdir2": {
        "position": VARIN32_STEPDIR2_POSITION,
      },
    };

    return input;
  }
};
