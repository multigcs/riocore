
module.exports = {
  output: {
    "pwmout0": {
      "dty": 0,
      "enable": 0,
    },
    "stepdir0": {
      "velocity": 0,
      "enable": 0,
    },
    "bitout0": {
      "bit": 0,
    },
    "bitout1": {
      "bit": 0,
    },
  },

  set_tx: function (rio_tx) {
    data = Buffer.alloc(13, 0);
    RX_HEADER = Buffer.from("74697277", "hex").readInt32LE(0);
    VAROUT32_PWMOUT0_DTY = rio_tx["pwmout0"]["dty"];
    VAROUT1_PWMOUT0_ENABLE = rio_tx["pwmout0"]["enable"];
    VAROUT32_STEPDIR0_VELOCITY = rio_tx["stepdir0"]["velocity"];
    VAROUT1_STEPDIR0_ENABLE = rio_tx["stepdir0"]["enable"];
    VAROUT1_BITOUT0_BIT = rio_tx["bitout0"]["bit"];
    VAROUT1_BITOUT1_BIT = rio_tx["bitout1"]["bit"];

    data.writeInt32LE(RX_HEADER, 0);
    data.writeInt32LE(VAROUT32_PWMOUT0_DTY, 4);
    data.writeInt32LE(VAROUT32_STEPDIR0_VELOCITY, 8);
    if (VAROUT1_BITOUT0_BIT) {
        data[12] |= (1<<7);
    }
    if (VAROUT1_BITOUT1_BIT) {
        data[12] |= (1<<6);
    }
    if (VAROUT1_PWMOUT0_ENABLE) {
        data[12] |= (1<<5);
    }
    if (VAROUT1_STEPDIR0_ENABLE) {
        data[12] |= (1<<4);
    }
    return data;
  },

  get_rx: function (data) {
    // read buffer
    TX_HEADER = data.readInt32LE(0);
    TITMESTAMP = data.readInt32LE(4);
    VARIN32_STEPDIR0_POSITION = data.readInt32LE(8);
    if ((data[12] & (1<<7)) != 0) {
        VARIN1_BITIN0_BIT = 1;
    } else {
        VARIN1_BITIN0_BIT = 0;
    }

    input = {
      "stepdir0": {
        "position": VARIN32_STEPDIR0_POSITION,
      },
      "bitin0": {
        "bit": VARIN1_BITIN0_BIT,
      },
    };

    return input;
  }
};
