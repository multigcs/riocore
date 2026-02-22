
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
    "bitout0": {
      "bit": 0,
    },
    "bitout1": {
      "bit": 0,
    },
    "gpioout0": {
      "bit": 0,
    },
    "gpioout1": {
      "bit": 0,
    },
    "gpioout2": {
      "bit": 0,
    },
    "gpioout3": {
      "bit": 0,
    },
    "gpioout4": {
      "bit": 0,
    },
    "gpioout5": {
      "bit": 0,
    },
    "gpioout6": {
      "bit": 0,
    },
    "gpioout7": {
      "bit": 0,
    },
    "gpioout8": {
      "bit": 0,
    },
    "gpioout9": {
      "bit": 0,
    },
  },

  set_tx: function (rio_tx) {
    data = Buffer.alloc(37, 0);
    RX_HEADER = Buffer.from("74697277", "hex").readInt32LE(0);
    VAROUT32_STEPDIR0_VELOCITY = rio_tx["stepdir0"]["velocity"];
    VAROUT1_STEPDIR0_ENABLE = rio_tx["stepdir0"]["enable"];
    VAROUT32_STEPDIR1_VELOCITY = rio_tx["stepdir1"]["velocity"];
    VAROUT1_STEPDIR1_ENABLE = rio_tx["stepdir1"]["enable"];
    VAROUT32_STEPDIR2_VELOCITY = rio_tx["stepdir2"]["velocity"];
    VAROUT1_STEPDIR2_ENABLE = rio_tx["stepdir2"]["enable"];
    VAROUT1_BITOUT0_BIT = rio_tx["bitout0"]["bit"];
    VAROUT1_BITOUT1_BIT = rio_tx["bitout1"]["bit"];
    VAROUT1_GPIOOUT0_BIT = rio_tx["gpioout0"]["bit"];
    VAROUT1_GPIOOUT1_BIT = rio_tx["gpioout1"]["bit"];
    VAROUT1_GPIOOUT2_BIT = rio_tx["gpioout2"]["bit"];
    VAROUT1_GPIOOUT3_BIT = rio_tx["gpioout3"]["bit"];
    VAROUT1_GPIOOUT4_BIT = rio_tx["gpioout4"]["bit"];
    VAROUT1_GPIOOUT5_BIT = rio_tx["gpioout5"]["bit"];
    VAROUT1_GPIOOUT6_BIT = rio_tx["gpioout6"]["bit"];
    VAROUT1_GPIOOUT7_BIT = rio_tx["gpioout7"]["bit"];
    VAROUT1_GPIOOUT8_BIT = rio_tx["gpioout8"]["bit"];
    VAROUT1_GPIOOUT9_BIT = rio_tx["gpioout9"]["bit"];

    data.writeInt32LE(RX_HEADER, 0);
    data.writeInt32LE(VAROUT32_STEPDIR0_VELOCITY, 4);
    data.writeInt32LE(VAROUT32_STEPDIR1_VELOCITY, 8);
    data.writeInt32LE(VAROUT32_STEPDIR2_VELOCITY, 12);
    if (VAROUT1_STEPDIR0_ENABLE) {
        data[16] |= (1<<7);
    }
    if (VAROUT1_STEPDIR1_ENABLE) {
        data[16] |= (1<<6);
    }
    if (VAROUT1_STEPDIR2_ENABLE) {
        data[16] |= (1<<5);
    }
    if (VAROUT1_BITOUT0_BIT) {
        data[16] |= (1<<4);
    }
    if (VAROUT1_BITOUT1_BIT) {
        data[16] |= (1<<3);
    }
    if (VAROUT1_GPIOOUT0_BIT) {
        data[16] |= (1<<2);
    }
    if (VAROUT1_GPIOOUT1_BIT) {
        data[16] |= (1<<1);
    }
    if (VAROUT1_GPIOOUT2_BIT) {
        data[16] |= (1<<0);
    }
    if (VAROUT1_GPIOOUT3_BIT) {
        data[17] |= (1<<7);
    }
    if (VAROUT1_GPIOOUT4_BIT) {
        data[17] |= (1<<6);
    }
    if (VAROUT1_GPIOOUT5_BIT) {
        data[17] |= (1<<5);
    }
    if (VAROUT1_GPIOOUT6_BIT) {
        data[17] |= (1<<4);
    }
    if (VAROUT1_GPIOOUT7_BIT) {
        data[17] |= (1<<3);
    }
    if (VAROUT1_GPIOOUT8_BIT) {
        data[17] |= (1<<2);
    }
    if (VAROUT1_GPIOOUT9_BIT) {
        data[17] |= (1<<1);
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
    VARIN32_ENCODER0_POSITION = data.readInt32LE(20);
    VARIN32_ENCODER1_POSITION = data.readInt32LE(24);
    VARIN32_ENCODER2_POSITION = data.readInt32LE(28);
    VARIN32_ENCODER3_POSITION = data.readInt32LE(32);
    if ((data[36] & (1<<7)) != 0) {
        VARIN1_BITIN0_BIT = 1;
    } else {
        VARIN1_BITIN0_BIT = 0;
    }
    if ((data[36] & (1<<6)) != 0) {
        VARIN1_BITIN1_BIT = 1;
    } else {
        VARIN1_BITIN1_BIT = 0;
    }
    if ((data[36] & (1<<5)) != 0) {
        VARIN1_BITIN2_BIT = 1;
    } else {
        VARIN1_BITIN2_BIT = 0;
    }
    if ((data[36] & (1<<4)) != 0) {
        VARIN1_BITIN3_BIT = 1;
    } else {
        VARIN1_BITIN3_BIT = 0;
    }
    if ((data[36] & (1<<3)) != 0) {
        VARIN1_BITIN4_BIT = 1;
    } else {
        VARIN1_BITIN4_BIT = 0;
    }
    if ((data[36] & (1<<2)) != 0) {
        VARIN1_BITIN5_BIT = 1;
    } else {
        VARIN1_BITIN5_BIT = 0;
    }
    if ((data[36] & (1<<1)) != 0) {
        VARIN1_GPIOIN0_BIT = 1;
    } else {
        VARIN1_GPIOIN0_BIT = 0;
    }
    if ((data[36] & (1<<0)) != 0) {
        VARIN1_GPIOIN1_BIT = 1;
    } else {
        VARIN1_GPIOIN1_BIT = 0;
    }

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
      "encoder0": {
        "position": VARIN32_ENCODER0_POSITION,
      },
      "encoder1": {
        "position": VARIN32_ENCODER1_POSITION,
      },
      "encoder2": {
        "position": VARIN32_ENCODER2_POSITION,
      },
      "encoder3": {
        "position": VARIN32_ENCODER3_POSITION,
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
      "bitin3": {
        "bit": VARIN1_BITIN3_BIT,
      },
      "bitin4": {
        "bit": VARIN1_BITIN4_BIT,
      },
      "bitin5": {
        "bit": VARIN1_BITIN5_BIT,
      },
      "gpioin0": {
        "bit": VARIN1_GPIOIN0_BIT,
      },
      "gpioin1": {
        "bit": VARIN1_GPIOIN1_BIT,
      },
    };

    return input;
  }
};
