/*
* Mesa SmartSerial (SSLBP) device template project
*
* Copyright (C) 2020 Forest Darling <fdarling@gmail.com>
* Copyright (C) 2025 Oliver Dippel <o.dippel@gmx.de> - doing some changes
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

void update() {
    //pdata_out.input
    //pdata_in.output
}

#ifdef MULTITHREAD
TaskHandle_t Task1;

void Task1code(void * pvParameters){
    for(;;) {
        update();
        delay(1);
    } 
}
#endif

void setup() {
#ifdef STATUS_LED
    pinMode(STATUS_LED, OUTPUT);
    digitalWrite(STATUS_LED, LOW);
#endif
    Serial.begin(115200);
    // while (!Serial);
    SSerial.begin(2500000); // 2.5MBps for Mesa Smart Serial
    // while (!SSerial);
    SSerial.setTimeout(1);

    //setup

#ifdef MULTITHREAD
    xTaskCreatePinnedToCore(Task1code, "Task1", 10000, NULL, 1, &Task1, 0);
#endif
}

uint8_t SSerialRead() {
    uint8_t data = 0;
    SSerial.readBytes(&data, 1);
    return data;
}

void SSerialWrite(const uint8_t *data, const size_t size) {
    SSerial.write(data, size);
    SSerial.flush();
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
                addr.bytes[0] = SSerialRead();
                crc = LBP_CalcNextCRC(addr.bytes[0], crc);
                addr.bytes[1] = SSerialRead();
                crc = LBP_CalcNextCRC(addr.bytes[1], crc);
                lbp_state.address = addr.address;
            }
            if (cmd.ReadWrite.Write) {
                const uint8_t lastByte = SSerialRead();
                if (lastByte != crc) {
                    Serial.println("<bad CRC>");
                    return;
                }
            } else { // (!cmd.ReadWrite.Write)
                const uint8_t lastByte = SSerialRead();
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
                    Serial.print("invalid read address: ");
                    Serial.print(lbp_state.address);
                    Serial.print(" len:");
                    Serial.println(readLength);
                    uint8_t zeros[] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
                    src = zeros; // do not block invalid reads
                    //return;
                }
                uint8_t RESPONSE[sizeof(uint64_t)+1];
                memcpy(RESPONSE, src, readLength);
                RESPONSE[readLength] = LBP_CalcCRC(RESPONSE, readLength);
                SSerialWrite(RESPONSE, readLength+1);
            }

        } else if (cmd.Generic.CommandType == LBP_COMMAND_TYPE_RPC) {
            //pdata_in_next
            const uint8_t lastByte = SSerialRead();
            if (lastByte != crc) {
                Serial.println("<CRC bad>");
                return;
            }
            switch (cmd.value) {
                case LBP_COMMAND_RPC_SMARTSERIAL_RPC_DISCOVERY: {
                    uint8_t RESPONSE[sizeof(DISCOVERY_DATA)+1];
                    memcpy(RESPONSE, &DISCOVERY_DATA, sizeof(DISCOVERY_DATA));
                    RESPONSE[sizeof(RESPONSE)-1] = LBP_CalcCRC(RESPONSE, sizeof(RESPONSE)-1);
                    SSerialWrite(RESPONSE, sizeof(RESPONSE));
                }
                break;
                case LBP_COMMAND_RPC_SMARTSERIAL_UNIT_NUMBER: {
                    uint8_t RESPONSE[sizeof(UNIT_NUMBER)+1];
                    memcpy(RESPONSE, &UNIT_NUMBER, sizeof(UNIT_NUMBER));
                    RESPONSE[sizeof(RESPONSE)-1] = LBP_CalcCRC(RESPONSE, sizeof(RESPONSE)-1);
                    SSerialWrite(RESPONSE, sizeof(RESPONSE));
                }
                break;
                case LBP_COMMAND_RPC_SMARTSERIAL_PROCESS_DATA: {
                    pdata_out.fault = 0;
                    uint8_t RESPONSE[DISCOVERY_DATA.RxSize+1];
                    memcpy(RESPONSE, &pdata_out, sizeof(pdata_out));
                    RESPONSE[sizeof(RESPONSE)-1] = LBP_CalcCRC(RESPONSE, sizeof(RESPONSE)-1);
                    SSerialWrite(RESPONSE, sizeof(RESPONSE));
                    memcpy(&pdata_in, pdata_in_next, sizeof(pdata_in));
#ifdef STATUS_LED
                    digitalWrite(STATUS_LED, (millis() & 0x100) ? HIGH : LOW);
#endif
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
                    param = static_cast<uint8_t>(SSerialRead());
                    crc = LBP_CalcNextCRC(param, crc);
                }
                const uint8_t lastByte = SSerialRead();
                if (lastByte != crc) {
                    Serial.println("<CRC bad>");
                    return;
                }
                switch (cmd.value) {
                    case LBP_COMMAND_LOCAL_WRITE_STATUS: {
                        const uint8_t RESPONSE[] = {LBP_CalcNextCRC(0x00)};
                        SSerialWrite(RESPONSE, sizeof(RESPONSE));
                    }
                    break;
                    case LBP_COMMAND_LOCAL_WRITE_SW_MODE: {
                        const uint8_t RESPONSE[] = {LBP_CalcNextCRC(0x00)};
                        SSerialWrite(RESPONSE, sizeof(RESPONSE));
                    }
                    break;
                    case LBP_COMMAND_LOCAL_WRITE_CLEAR_FAULTS: {
                        const uint8_t RESPONSE[] = {LBP_CalcNextCRC(0x00)};
                        SSerialWrite(RESPONSE, sizeof(RESPONSE));
                    }
                    break;
                    case LBP_COMMAND_LOCAL_WRITE_NVMEM_FLAG: {
                        const uint8_t RESPONSE[] = {LBP_CalcNextCRC(0x00)};
                        SSerialWrite(RESPONSE, sizeof(RESPONSE));
                    }
                    break;
                    case LBP_COMMAND_LOCAL_WRITE_COMMAND_TIMEOUT: {
                        const uint8_t RESPONSE[] = {LBP_CalcNextCRC(0x00)};
                        SSerialWrite(RESPONSE, sizeof(RESPONSE));
                    }
                    break;
                    default: {
                        Serial.println("***UNHANDLED*** LOCAL LBP WRITE COMMAND: 0x%02X");
                    }
                }
            } else { // if (cmd.value < 0xE0)
                const uint8_t lastByte = SSerialRead();
                if (lastByte != crc) {
                    Serial.println("<CRC bad>");
                    return;
                }
                // respond
                switch (cmd.value) {
                    case LBP_COMMAND_LOCAL_READ_LBP_STATUS: {
                        const uint8_t lbp_status = 0x00;
                        const uint8_t RESPONSE[] = {lbp_status, LBP_CalcNextCRC(lbp_status)};
                        SSerialWrite(RESPONSE, sizeof(RESPONSE));
                    }
                    break;
                    case LBP_COMMAND_LOCAL_READ_CLEAR_FAULT_FLAG: {
                        const uint8_t fault_flag = 0x00;
                        const uint8_t RESPONSE[] = {fault_flag, LBP_CalcNextCRC(fault_flag)};
                        SSerialWrite(RESPONSE, sizeof(RESPONSE));
                    }
                    break;
                    case LBP_COMMAND_LOCAL_READ_CARD_NAME_CHAR0:
                    case LBP_COMMAND_LOCAL_READ_CARD_NAME_CHAR1:
                    case LBP_COMMAND_LOCAL_READ_CARD_NAME_CHAR2:
                    case LBP_COMMAND_LOCAL_READ_CARD_NAME_CHAR3: {
                        uint8_t RESPONSE[] = {CARD_NAME[cmd.value - LBP_COMMAND_LOCAL_READ_CARD_NAME_CHAR0], 0x00};
                        RESPONSE[sizeof(RESPONSE)-1] = LBP_CalcCRC(RESPONSE, sizeof(RESPONSE)-1);
                        SSerialWrite(RESPONSE, sizeof(RESPONSE));
                    }
                    break;
                    case LBP_COMMAND_LOCAL_READ_FAULT_DATA: {
                        const uint8_t fault_data = 0x00;
                        const uint8_t RESPONSE[] = {fault_data, LBP_CalcNextCRC(fault_data)};
                        SSerialWrite(RESPONSE, sizeof(RESPONSE));
                    }
                    break;
                    case LBP_COMMAND_LOCAL_READ_COOKIE: {
                        const uint8_t RESPONSE[] = {LBP_COOKIE, LBP_CalcNextCRC(LBP_COOKIE)};
                        SSerialWrite(RESPONSE, sizeof(RESPONSE));
                    }
                    break;
                    default: {
                        Serial.println("***UNHANDLED*** LOCAL LBP READ COMMAND: 0x%02X");
                    }
                }
            }
        } else {
            Serial.print("unknown command: ");
            Serial.println(cmd.Generic.CommandType);
        }
#ifndef MULTITHREAD
    } else {
        update();
#endif
    }
}
