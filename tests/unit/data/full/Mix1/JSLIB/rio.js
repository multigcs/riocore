
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
    "bitout0": {
      "bit": 0,
    },
  },

  set_tx: function (rio_tx) {
    data = Buffer.alloc(17, 0);
    RX_HEADER = Buffer.from("74697277", "hex").readInt32LE(0);
    VAROUT32_STEPDIR0_VELOCITY = rio_tx["stepdir0"]["velocity"];
    VAROUT1_STEPDIR0_ENABLE = rio_tx["stepdir0"]["enable"];
    VAROUT32_STEPDIR1_VELOCITY = rio_tx["stepdir1"]["velocity"];
    VAROUT1_STEPDIR1_ENABLE = rio_tx["stepdir1"]["enable"];
    VAROUT1_BITOUT0_BIT = rio_tx["bitout0"]["bit"];

    data.writeInt32LE(RX_HEADER, 0);
    data.writeInt32LE(VAROUT32_STEPDIR0_VELOCITY, 4);
    data.writeInt32LE(VAROUT32_STEPDIR1_VELOCITY, 8);
    if (VAROUT1_STEPDIR0_ENABLE) {
        data[12] |= (1<<7);
    }
    if (VAROUT1_STEPDIR1_ENABLE) {
        data[12] |= (1<<6);
    }
    if (VAROUT1_BITOUT0_BIT) {
        data[12] |= (1<<5);
    }
    return data;
  },

  get_rx: function (data) {
    // read buffer
    TX_HEADER = data.readInt32LE(0);
    TITMESTAMP = data.readInt32LE(4);
    VARIN32_STEPDIR0_POSITION = data.readInt32LE(8);
    VARIN32_STEPDIR1_POSITION = data.readInt32LE(12);
    if ((data[16] & (1<<7)) != 0) {
        VARIN1_BITIN0_BIT = 1;
    } else {
        VARIN1_BITIN0_BIT = 0;
    }

    input = {
      "stepdir0": {
        "position": VARIN32_STEPDIR0_POSITION,
      },
      "stepdir1": {
        "position": VARIN32_STEPDIR1_POSITION,
      },
      "bitin0": {
        "bit": VARIN1_BITIN0_BIT,
      },
    };

    return input;
  }
};
