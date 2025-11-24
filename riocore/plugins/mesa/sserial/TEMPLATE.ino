/*
* Mesa SmartSerial (SSLBP) device template project
*
* Copyright (C) 2020 Forest Darling <fdarling@gmail.com>
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program.  If not, see <http://www.gnu.org/licenses/>.
*
* this code was based on the user fupeama's attachments on the following LinuxCNC forum post:
* https://forum.linuxcnc.org/27-driver-boards/34445-custom-board-for-smart-serial-interface?start=10#110007
* https://forum.linuxcnc.org/media/kunena/attachments/16679/sserial.h
* https://forum.linuxcnc.org/media/kunena/attachments/16679/sserial.c
*/

#include "LBP.h"
#include <stdint.h>
#pragma pack(push,1)

//defines
//CARD_NAME
//ProcessDataOut
//ProcessDataIn

static const uint32_t UNIT_NUMBER = 0x04030201;
static const uint16_t  GTOC_BASE_ADDRESS = 0x1000; // arbitrary, not real location in memory
static const uint16_t  PTOC_BASE_ADDRESS = 0x2000; // arbitrary, not real location in memory
static const uint16_t   PDD_BASE_ADDRESS = 0x3000; // arbitrary, not real location in memory
static const uint16_t PARAM_BASE_ADDRESS = 0x4000; // arbitrary, not real location in memory

//LBP_Discovery_Data
static const LBP_PDD PDD[] = {
    {
        .md = {
            .RecordType = LBP_PDD_RECORD_TYPE_MODE_DESCRIPTOR,
            .ModeIndex  = 0,
            .ModeType   = LBP_PDD_MODE_TYPE_HWMODE,
            ._unused    = 0,
            "Standard"
        }
    },
    {
        .md = {
            .RecordType = LBP_PDD_RECORD_TYPE_MODE_DESCRIPTOR,
            .ModeIndex  = 0,
            .ModeType   = LBP_PDD_MODE_TYPE_SWMODE,
            ._unused    = 0,
            "Input_Output"
        }
    },
    //PDD
};
//PTOC
//GTOC

static const struct {
    uint16_t base;
    uint16_t size;
    const void *data;
} VIRTUAL_MEMORY_MAP[] = {
    {.base = GTOC_BASE_ADDRESS, .size = sizeof(GTOC), .data = GTOC},
    {.base = PTOC_BASE_ADDRESS, .size = sizeof(PTOC), .data = PTOC},
    {.base =  PDD_BASE_ADDRESS, .size = sizeof( PDD), .data = PDD}
};

#pragma pack(pop)

struct LBP_State {
    uint16_t address;
} lbp_state = {
    .address = 0x0000
};

void setup() {
    //pinMode(LED_BUILTIN, OUTPUT);
    //setup
    Serial.begin(9600); // baudrate doesn't matter, full speed USB always
    SSerial.begin(2500000); // 2.5MBps for Mesa Smart Serial
}

void loop() {
    if (SSerial.available()) {
        LBP_Command cmd = {.value = static_cast<uint8_t>(SSerial.read())};
        uint8_t crc = LBP_CalcNextCRC(cmd.value);
        if (cmd.Generic.CommandType == LBP_COMMAND_TYPE_READ_WRITE) {
            // possibly read 2-byte address
            if (cmd.ReadWrite.AddressSize) {
                union {
                    uint16_t address;
                    uint8_t bytes[2];
                } addr;
                // read LSB
                while (!SSerial.available()) {
                    yield();
                }
                addr.bytes[0] = SSerial.read();
                crc = LBP_CalcNextCRC(addr.bytes[0], crc);
                // read MSB
                while (!SSerial.available()) {
                    yield();
                }
                addr.bytes[1] = SSerial.read();
                crc = LBP_CalcNextCRC(addr.bytes[1], crc);
                lbp_state.address = addr.address;
            }
            if (cmd.ReadWrite.Write) {
                while (!SSerial.available()) {
                    yield();
                }
                const uint8_t lastByte = SSerial.read();
                if (lastByte != crc) {
                    Serial.println("<bad CRC>");
                    return;
                }
            } else { // (!cmd.ReadWrite.Write)
                while (!SSerial.available()) {
                    yield();
                }
                const uint8_t lastByte = SSerial.read();
                if (lastByte != crc) {
                    Serial.println("<bad CRC>");
                    return;
                }
                const uint8_t readLength = 1 << cmd.ReadWrite.DataSize;
                const void *src = NULL;
                for (size_t i = 0; i < sizeof(VIRTUAL_MEMORY_MAP)/sizeof(VIRTUAL_MEMORY_MAP[0]); i++) {
                    if (lbp_state.address >= VIRTUAL_MEMORY_MAP[i].base && (lbp_state.address + readLength) <= (VIRTUAL_MEMORY_MAP[i].base + VIRTUAL_MEMORY_MAP[i].size)) {
                        src = reinterpret_cast<const uint8_t*>(VIRTUAL_MEMORY_MAP[i].data) + (lbp_state.address - VIRTUAL_MEMORY_MAP[i].base);
                        break;
                    }
                }
                if (!src) {
                    Serial.println("<invalid read address 0x%04X>");
                    return;
                }
                uint8_t RESPONSE[sizeof(uint64_t)+1];
                memcpy(RESPONSE, src, readLength);
                RESPONSE[readLength] = LBP_CalcCRC(RESPONSE, readLength);
                SSerial.write(RESPONSE, readLength+1);
                SSerial.flush();
            }

        } else if (cmd.Generic.CommandType == LBP_COMMAND_TYPE_RPC) {
            //pdata_in_next
            while (!SSerial.available()) {
                yield();
            }
            const uint8_t lastByte = SSerial.read();
            if (lastByte != crc) {
                Serial.println("<CRC bad>");
                return;
            }
            switch (cmd.value) {
                case LBP_COMMAND_RPC_SMARTSERIAL_RPC_DISCOVERY: {
                    uint8_t RESPONSE[sizeof(DISCOVERY_DATA)+1];
                    memcpy(RESPONSE, &DISCOVERY_DATA, sizeof(DISCOVERY_DATA));
                    RESPONSE[sizeof(RESPONSE)-1] = LBP_CalcCRC(RESPONSE, sizeof(RESPONSE)-1);
                    SSerial.write(RESPONSE, sizeof(RESPONSE));
                    SSerial.flush();
                }
                break;
                case LBP_COMMAND_RPC_SMARTSERIAL_UNIT_NUMBER: {
                    uint8_t RESPONSE[sizeof(UNIT_NUMBER)+1];
                    memcpy(RESPONSE, &UNIT_NUMBER, sizeof(UNIT_NUMBER));
                    RESPONSE[sizeof(RESPONSE)-1] = LBP_CalcCRC(RESPONSE, sizeof(RESPONSE)-1);
                    SSerial.write(RESPONSE, sizeof(RESPONSE));
                    SSerial.flush();
                }
                break;
                case LBP_COMMAND_RPC_SMARTSERIAL_PROCESS_DATA: {
                    pdata_out.fault = 0;
                    //pdata_out.input
                    uint8_t RESPONSE[DISCOVERY_DATA.RxSize+1];
                    memcpy(RESPONSE, &pdata_out, sizeof(pdata_out));
                    RESPONSE[sizeof(RESPONSE)-1] = LBP_CalcCRC(RESPONSE, sizeof(RESPONSE)-1);
                    SSerial.write(RESPONSE, sizeof(RESPONSE));
                    SSerial.flush();

                    //pdata_in.output
                    //digitalWriteFast(LED_BUILTIN, (millis() & 0x100) ? HIGH : LOW);
                }
                break;
                default: {
                    Serial.println("***UNHANDLED*** LBP_COMMAND_TYPE_RPC: 0x%02X");
                }
            }
        } else if (cmd.Generic.CommandType == LBP_COMMAND_TYPE_LOCAL_READ_WRITE) {
            if (cmd.value >= 0xE0) { // HACK check if it's a write command
                uint8_t param = 0;
                if (cmd.value != LBP_COMMAND_LOCAL_WRITE_RESET_LBP_PARSE) {
                    // skip parameter byte for now
                    while (!SSerial.available()) {
                        yield();
                    }
                    param = static_cast<uint8_t>(SSerial.read());
                    crc = LBP_CalcNextCRC(param, crc);
                }
                while (!SSerial.available()) {
                    yield();
                }
                const uint8_t lastByte = SSerial.read();
                if (lastByte != crc) {
                    Serial.println("<CRC bad>");
                    return;
                }
                switch (cmd.value) {
                    case LBP_COMMAND_LOCAL_WRITE_STATUS: {
                        const uint8_t RESPONSE[] = {LBP_CalcNextCRC(0x00)};
                        SSerial.write(RESPONSE, sizeof(RESPONSE));
                        SSerial.flush();
                    }
                    break;
                    case LBP_COMMAND_LOCAL_WRITE_SW_MODE: {
                        const uint8_t RESPONSE[] = {LBP_CalcNextCRC(0x00)};
                        SSerial.write(RESPONSE, sizeof(RESPONSE));
                        SSerial.flush();
                    }
                    break;
                    case LBP_COMMAND_LOCAL_WRITE_CLEAR_FAULTS: {
                        const uint8_t RESPONSE[] = {LBP_CalcNextCRC(0x00)};
                        SSerial.write(RESPONSE, sizeof(RESPONSE));
                        SSerial.flush();
                    }
                    break;
                    case LBP_COMMAND_LOCAL_WRITE_NVMEM_FLAG: {
                        const uint8_t RESPONSE[] = {LBP_CalcNextCRC(0x00)};
                        SSerial.write(RESPONSE, sizeof(RESPONSE));
                        SSerial.flush();
                    }
                    break;
                    case LBP_COMMAND_LOCAL_WRITE_COMMAND_TIMEOUT: {
                        const uint8_t RESPONSE[] = {LBP_CalcNextCRC(0x00)};
                        SSerial.write(RESPONSE, sizeof(RESPONSE));
                        SSerial.flush();
                    }
                    break;
                    default: {
                        Serial.println("***UNHANDLED*** LOCAL LBP WRITE COMMAND: 0x%02X");
                    }
                }
            } else { // if (cmd.value < 0xE0)
                while (!SSerial.available()) {
                    yield();
                }
                const uint8_t lastByte = SSerial.read();
                if (lastByte != crc) {
                    Serial.println("<CRC bad>");
                    return;
                }
                // respond
                switch (cmd.value) {
                    case LBP_COMMAND_LOCAL_READ_LBP_STATUS: {
                        const uint8_t lbp_status = 0x00;
                        const uint8_t RESPONSE[] = {lbp_status, LBP_CalcNextCRC(lbp_status)};
                        SSerial.write(RESPONSE, sizeof(RESPONSE));
                        SSerial.flush();
                    }
                    break;
                    case LBP_COMMAND_LOCAL_READ_CLEAR_FAULT_FLAG: {
                        const uint8_t fault_flag = 0x00;
                        const uint8_t RESPONSE[] = {fault_flag, LBP_CalcNextCRC(fault_flag)};
                        SSerial.write(RESPONSE, sizeof(RESPONSE));
                        SSerial.flush();
                    }
                    break;
                    case LBP_COMMAND_LOCAL_READ_CARD_NAME_CHAR0:
                    case LBP_COMMAND_LOCAL_READ_CARD_NAME_CHAR1:
                    case LBP_COMMAND_LOCAL_READ_CARD_NAME_CHAR2:
                    case LBP_COMMAND_LOCAL_READ_CARD_NAME_CHAR3: {
                        uint8_t RESPONSE[] = {CARD_NAME[cmd.value - LBP_COMMAND_LOCAL_READ_CARD_NAME_CHAR0], 0x00};
                        RESPONSE[sizeof(RESPONSE)-1] = LBP_CalcCRC(RESPONSE, sizeof(RESPONSE)-1);
                        SSerial.write(RESPONSE, sizeof(RESPONSE));
                        SSerial.flush();
                    }
                    break;
                    case LBP_COMMAND_LOCAL_READ_FAULT_DATA: {
                        const uint8_t fault_data = 0x00;
                        const uint8_t RESPONSE[] = {fault_data, LBP_CalcNextCRC(fault_data)};
                        SSerial.write(RESPONSE, sizeof(RESPONSE));
                        SSerial.flush();
                    }
                    break;
                    case LBP_COMMAND_LOCAL_READ_COOKIE: {
                        const uint8_t RESPONSE[] = {LBP_COOKIE, LBP_CalcNextCRC(LBP_COOKIE)};
                        SSerial.write(RESPONSE, sizeof(RESPONSE));
                        SSerial.flush();
                    }
                    break;
                    default: {
                        Serial.println("***UNHANDLED*** LOCAL LBP READ COMMAND: 0x%02X");
                    }
                }
            }
        } else {
            Serial.println("unknown command %02X");
        }
    }
}
