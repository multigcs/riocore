
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
    "pwmout0": {
      "dty": 0,
      "enable": 0,
    },
    "bitout0": {
      "bit": 0,
    },
    "bitout1": {
      "bit": 0,
    },
    "ledscale0": {
      "bit": 0,
    },
    "ledscale1": {
      "bit": 0,
    },
    "ledscale2": {
      "bit": 0,
    },
    "selectedx": {
      "bit": 0,
    },
    "selectedy": {
      "bit": 0,
    },
    "selectedz": {
      "bit": 0,
    },
  },

  set_tx: function (rio_tx) {
    data = Buffer.alloc(28, 0);
    RX_HEADER = Buffer.from("74697277", "hex").readInt32LE(0);
    VAROUT32_STEPDIR0_VELOCITY = rio_tx["stepdir0"]["velocity"];
    VAROUT1_STEPDIR0_ENABLE = rio_tx["stepdir0"]["enable"];
    VAROUT32_STEPDIR1_VELOCITY = rio_tx["stepdir1"]["velocity"];
    VAROUT1_STEPDIR1_ENABLE = rio_tx["stepdir1"]["enable"];
    VAROUT32_STEPDIR2_VELOCITY = rio_tx["stepdir2"]["velocity"];
    VAROUT1_STEPDIR2_ENABLE = rio_tx["stepdir2"]["enable"];
    VAROUT16_PWMOUT0_DTY = rio_tx["pwmout0"]["dty"];
    VAROUT1_PWMOUT0_ENABLE = rio_tx["pwmout0"]["enable"];
    VAROUT1_BITOUT0_BIT = rio_tx["bitout0"]["bit"];
    VAROUT1_BITOUT1_BIT = rio_tx["bitout1"]["bit"];
    VAROUT1_LEDSCALE0_BIT = rio_tx["ledscale0"]["bit"];
    VAROUT1_LEDSCALE1_BIT = rio_tx["ledscale1"]["bit"];
    VAROUT1_LEDSCALE2_BIT = rio_tx["ledscale2"]["bit"];
    VAROUT1_SELECTEDX_BIT = rio_tx["selectedx"]["bit"];
    VAROUT1_SELECTEDY_BIT = rio_tx["selectedy"]["bit"];
    VAROUT1_SELECTEDZ_BIT = rio_tx["selectedz"]["bit"];

    data.writeInt32LE(RX_HEADER, 0);
    data.writeInt32LE(VAROUT32_STEPDIR0_VELOCITY, 4);
    data.writeInt32LE(VAROUT32_STEPDIR1_VELOCITY, 8);
    data.writeInt32LE(VAROUT32_STEPDIR2_VELOCITY, 12);
    data.writeInt16LE(VAROUT16_PWMOUT0_DTY, 16);
    if (VAROUT1_STEPDIR0_ENABLE) {
        data[18] |= (1<<7);
    }
    if (VAROUT1_STEPDIR1_ENABLE) {
        data[18] |= (1<<6);
    }
    if (VAROUT1_STEPDIR2_ENABLE) {
        data[18] |= (1<<5);
    }
    if (VAROUT1_PWMOUT0_ENABLE) {
        data[18] |= (1<<4);
    }
    if (VAROUT1_BITOUT0_BIT) {
        data[18] |= (1<<3);
    }
    if (VAROUT1_BITOUT1_BIT) {
        data[18] |= (1<<2);
    }
    if (VAROUT1_LEDSCALE0_BIT) {
        data[18] |= (1<<1);
    }
    if (VAROUT1_LEDSCALE1_BIT) {
        data[18] |= (1<<0);
    }
    if (VAROUT1_LEDSCALE2_BIT) {
        data[19] |= (1<<7);
    }
    if (VAROUT1_SELECTEDX_BIT) {
        data[19] |= (1<<6);
    }
    if (VAROUT1_SELECTEDY_BIT) {
        data[19] |= (1<<5);
    }
    if (VAROUT1_SELECTEDZ_BIT) {
        data[19] |= (1<<4);
    }
    return data;
  },

  get_rx: function (data) {
    // read buffer
    TX_HEADER = data.readInt32LE(0);
    TITMESTAMP = data.readInt32LE(4);
    MULTIPLEXED_INPUT_VALUE = data.readInt32LE(8);
    MULTIPLEXED_INPUT_ID = data.readUInt8(12);
    VARIN32_STEPDIR0_POSITION = data.readInt32LE(13);
    VARIN32_STEPDIR1_POSITION = data.readInt32LE(17);
    VARIN32_STEPDIR2_POSITION = data.readInt32LE(21);
    if ((data[25] & (1<<7)) != 0) {
        VARIN1_BITIN0_BIT = 1;
    } else {
        VARIN1_BITIN0_BIT = 0;
    }
    if ((data[25] & (1<<6)) != 0) {
        VARIN1_BITIN1_BIT = 1;
    } else {
        VARIN1_BITIN1_BIT = 0;
    }
    if ((data[25] & (1<<5)) != 0) {
        VARIN1_BITIN2_BIT = 1;
    } else {
        VARIN1_BITIN2_BIT = 0;
    }
    if ((data[25] & (1<<4)) != 0) {
        VARIN1_BITIN3_BIT = 1;
    } else {
        VARIN1_BITIN3_BIT = 0;
    }
    if ((data[25] & (1<<3)) != 0) {
        VARIN1_BITIN4_BIT = 1;
    } else {
        VARIN1_BITIN4_BIT = 0;
    }
    if ((data[25] & (1<<2)) != 0) {
        VARIN1_BITIN5_BIT = 1;
    } else {
        VARIN1_BITIN5_BIT = 0;
    }
    if ((data[25] & (1<<1)) != 0) {
        VARIN1_BITIN6_BIT = 1;
    } else {
        VARIN1_BITIN6_BIT = 0;
    }
    if ((data[25] & (1<<0)) != 0) {
        VARIN1_BITIN7_BIT = 1;
    } else {
        VARIN1_BITIN7_BIT = 0;
    }
    if ((data[26] & (1<<7)) != 0) {
        VARIN1_UARTSUB0_TIMEOUT = 1;
    } else {
        VARIN1_UARTSUB0_TIMEOUT = 0;
    }
    if ((data[26] & (1<<6)) != 0) {
        VARIN1_MPGESTOP_BIT = 1;
    } else {
        VARIN1_MPGESTOP_BIT = 0;
    }
    if ((data[26] & (1<<5)) != 0) {
        VARIN1_SCALE0_BIT = 1;
    } else {
        VARIN1_SCALE0_BIT = 0;
    }
    if ((data[26] & (1<<4)) != 0) {
        VARIN1_SCALE1_BIT = 1;
    } else {
        VARIN1_SCALE1_BIT = 0;
    }
    if ((data[26] & (1<<3)) != 0) {
        VARIN1_SCALE2_BIT = 1;
    } else {
        VARIN1_SCALE2_BIT = 0;
    }
    if ((data[26] & (1<<2)) != 0) {
        VARIN1_SELECTX_BIT = 1;
    } else {
        VARIN1_SELECTX_BIT = 0;
    }
    if ((data[26] & (1<<1)) != 0) {
        VARIN1_SELECTY_BIT = 1;
    } else {
        VARIN1_SELECTY_BIT = 0;
    }
    if ((data[26] & (1<<0)) != 0) {
        VARIN1_SELECTZ_BIT = 1;
    } else {
        VARIN1_SELECTZ_BIT = 0;
    }
    if ((data[27] & (1<<7)) != 0) {
        VARIN1_LBUTTON_BIT = 1;
    } else {
        VARIN1_LBUTTON_BIT = 0;
    }
    if ((data[27] & (1<<6)) != 0) {
        VARIN1_CBUTTON_BIT = 1;
    } else {
        VARIN1_CBUTTON_BIT = 0;
    }
    if ((data[27] & (1<<5)) != 0) {
        VARIN1_RBUTTON_BIT = 1;
    } else {
        VARIN1_RBUTTON_BIT = 0;
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
      "bitin6": {
        "bit": VARIN1_BITIN6_BIT,
      },
      "bitin7": {
        "bit": VARIN1_BITIN7_BIT,
      },
      "uartsub0": {
        "timeout": VARIN1_UARTSUB0_TIMEOUT,
      },
      "mpgestop": {
        "bit": VARIN1_MPGESTOP_BIT,
      },
      "scale0": {
        "bit": VARIN1_SCALE0_BIT,
      },
      "scale1": {
        "bit": VARIN1_SCALE1_BIT,
      },
      "scale2": {
        "bit": VARIN1_SCALE2_BIT,
      },
      "selectx": {
        "bit": VARIN1_SELECTX_BIT,
      },
      "selecty": {
        "bit": VARIN1_SELECTY_BIT,
      },
      "selectz": {
        "bit": VARIN1_SELECTZ_BIT,
      },
      "lbutton": {
        "bit": VARIN1_LBUTTON_BIT,
      },
      "cbutton": {
        "bit": VARIN1_CBUTTON_BIT,
      },
      "rbutton": {
        "bit": VARIN1_RBUTTON_BIT,
      },
    };

    return input;
  }
};
