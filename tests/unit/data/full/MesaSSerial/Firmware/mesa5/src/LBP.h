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
*/

#ifndef LBP_H
#define LBP_H

// this code was based on the user fupeama's attachments on the following LinuxCNC forum post:
// https://forum.linuxcnc.org/27-driver-boards/34445-custom-board-for-smart-serial-interface?start=10#110007
// https://forum.linuxcnc.org/media/kunena/attachments/16679/sserial.h
// https://forum.linuxcnc.org/media/kunena/attachments/16679/sserial.c

#include <stdint.h>
#include <stddef.h>

#pragma pack(push,1)

struct LBP_Command_Fields_ReadWrite
{ // LSB to MSB within bytes, MSB to LSB for bytes themselves
  unsigned int DataSize        : 2; // 0 = 1 byte, 1 = 2 bytes, 2 = 4 bytes, 3 = 8 bytes
  unsigned int AddressSize     : 1; // 0 = current address, 1 = 2-byte address
  unsigned int AutoInc         : 1; // 0 = leave address unchanged, 1 = address is post incremented by data size in bytes
  unsigned int RPCIncludesData : 1; // 0 = data is from stream, 1 = data is from RPC (RPC only)
  unsigned int Write           : 1; // 0 = read, 1 = write
  unsigned int CommandType     : 2; // must be 0b01 for data read/write commands
};

struct LBP_Command_Fields_Generic
{
  unsigned int _unused     : 6;
  unsigned int CommandType : 2;
};

union LBP_Command
{
  uint8_t value;
  LBP_Command_Fields_Generic           Generic;
  LBP_Command_Fields_ReadWrite         ReadWrite;
};

extern const uint8_t LBP_CRC_table[256];

uint8_t LBP_CalcNextCRC(uint8_t data, uint8_t crc = 0);

uint8_t LBP_CalcCRC(const uint8_t data[], size_t len);

enum LBP_RPC_Commands : uint8_t
{
  LBP_COMMAND_RPC_SMARTSERIAL_RPC_DISCOVERY = 0xBB,
  LBP_COMMAND_RPC_SMARTSERIAL_UNIT_NUMBER   = 0xBC,
  LBP_COMMAND_RPC_SMARTSERIAL_PROCESS_DATA  = 0xBD
};

enum LBP_Local_Commands : uint8_t
{
 LBP_COMMAND_LOCAL_READ_UNIT_ADDRESS     = 0xC0, // TODO called unit address or unit id?
 LBP_COMMAND_LOCAL_READ_LBP_STATUS       = 0xC1,
 LBP_COMMAND_LOCAL_READ_CRC_ENABLE       = 0xC2, // TODO called CRC enable or CRC *check* enable?
 LBP_COMMAND_LOCAL_READ_CRC_ERROR_COUNT  = 0xC3,
 // 0xC4 .. 0xC5 reserved
 LBP_COMMAND_LOCAL_READ_SW_MODE          = 0xC6,
 LBP_COMMAND_LOCAL_READ_CLEAR_FAULT_FLAG = 0xC7,
 // 0xC8 .. 0xC9 reserved
 LBP_COMMAND_LOCAL_READ_ENABLE_RPCMEM    = 0xCA,
 LBP_COMMAND_LOCAL_READ_COMMAND_TIMEOUT  = 0xCB,
 LBP_COMMAND_LOCAL_READ_NONVOL_FLAG      = 0xCC,
 // 0xCC .. 0xCF reserved
 LBP_COMMAND_LOCAL_READ_CARD_NAME_CHAR0  = 0xD0,
 LBP_COMMAND_LOCAL_READ_CARD_NAME_CHAR1  = 0xD1,
 LBP_COMMAND_LOCAL_READ_CARD_NAME_CHAR2  = 0xD2,
 LBP_COMMAND_LOCAL_READ_CARD_NAME_CHAR3  = 0xD3,
 // 7i77 manual says 0xD4 -> 0xD7 are the 4 character configuration name
 /*LBP_COMMAND_LOCAL_READ_CONF_NAME_CHAR0  = 0xD4, // TODO verify, documentation has a typo and says 0xD5-0xD7 but says 4 characters...
 LBP_COMMAND_LOCAL_READ_CONF_NAME_CHAR1  = 0xD5,
 LBP_COMMAND_LOCAL_READ_CONF_NAME_CHAR2  = 0xD6,
 LBP_COMMAND_LOCAL_READ_CONF_NAME_CHAR3  = 0xD7,*/
 // 7i84 says 0xD4 -> 0xD7 are the following...
 LBP_COMMAND_LOCAL_READ_CAPABILITY       = 0xD4,
 LBP_COMMAND_LOCAL_READ_REMOTE_VERSION   = 0xD5, // "remote" version?
 LBP_COMMAND_LOCAL_READ_HW_MODE          = 0xD6, // "remote" hardware mode?
 LBP_COMMAND_LOCAL_READ_FAULT_DATA       = 0xD7, // "remote" fault data?
 LBP_COMMAND_LOCAL_READ_ADDRESS_LOW      = 0xD8,
 LBP_COMMAND_LOCAL_READ_ADDRESS_HIGH     = 0xD9,
 LBP_COMMAND_LOCAL_READ_VERSION          = 0xDA,
 LBP_COMMAND_LOCAL_READ_UNIT_ID          = 0xDB,
 LBP_COMMAND_LOCAL_READ_RPC_PITCH        = 0xDC,
 LBP_COMMAND_LOCAL_READ_RPC_SIZE_L       = 0xDD,
 LBP_COMMAND_LOCAL_READ_RPC_SIZE_H       = 0xDE,
 LBP_COMMAND_LOCAL_READ_COOKIE           = 0xDF,
 // 0xE0 reserved
 LBP_COMMAND_LOCAL_WRITE_STATUS          = 0xE1,
 LBP_COMMAND_LOCAL_WRITE_CRC_CHECK_EN    = 0xE2, // TODO called CRC enable or CRC *check* enable?
 LBP_COMMAND_LOCAL_WRITE_CRC_ERROR_COUNT = 0xE3,
 // 0xE4 .. 0xE5 reserved
 LBP_COMMAND_LOCAL_WRITE_SW_MODE         = 0xE6, // NOTE: undocumented!
 LBP_COMMAND_LOCAL_WRITE_CLEAR_FAULTS    = 0xE7,
 // 0xE8 .. 0xE9 reserved
 LBP_COMMAND_LOCAL_WRITE_ENABLE_RPCMEM   = 0xEA,
 LBP_COMMAND_LOCAL_WRITE_COMMAND_TIMEOUT = 0xEB,
 LBP_COMMAND_LOCAL_WRITE_NVMEM_FLAG      = 0xEC,
 LBP_COMMAND_LOCAL_WRITE_EXTMEM_FLAG     = 0xED,
 // 0xEE .. 0xEF reserved
 LBP_COMMAND_LOCAL_WRITE_LEDS            = 0xF7,
 LBP_COMMAND_LOCAL_WRITE_ADDRESS_LOW     = 0xF8,
 LBP_COMMAND_LOCAL_WRITE_ADDRESS_HIGH    = 0xF9,
 LBP_COMMAND_LOCAL_WRITE_INCREMENT_ADDR  = 0xFA,
 // 0xFB .. 0xFC reserved
 LBP_COMMAND_LOCAL_WRITE_UNIT_ID         = 0xFD, // TODO called unit address or unit id?
 LBP_COMMAND_LOCAL_WRITE_RESET_LBP_PROC  = 0xFE,
 LBP_COMMAND_LOCAL_WRITE_RESET_LBP_PARSE = 0xFF
};

enum LBP_Masks : uint8_t
{
  LBP_MASK_COMMAND = 0xC0
};

enum LBP_Constants : uint8_t
{
  LBP_COOKIE = 0x5A
};

enum LBP_Command_Types : uint8_t
{
  LBP_COMMAND_TYPE_READ_WRITE       = 0b01,
  LBP_COMMAND_TYPE_RPC              = 0b10,
  LBP_COMMAND_TYPE_LOCAL_READ_WRITE = 0b11
};

enum LBP_PDD_Record_Types : uint8_t
{
  LBP_PDD_RECORD_TYPE_NORMAL          = 0xA0, // TODO name?
  LBP_PDD_RECORD_TYPE_MODE_DESCRIPTOR = 0xB0
};

enum LBP_PDD_Data_Types : uint8_t
{
  LBP_PDD_DATA_TYPE_PAD             = 0x00,
  LBP_PDD_DATA_TYPE_BITS            = 0x01,
  LBP_PDD_DATA_TYPE_UNSIGNED        = 0x02,
  LBP_PDD_DATA_TYPE_SIGNED          = 0x03,
  LBP_PDD_DATA_TYPE_NONVOL_UNSIGNED = 0x04,
  LBP_PDD_DATA_TYPE_NONVOL_SIGNED   = 0x05,
  LBP_PDD_DATA_TYPE_STREAM          = 0x06,
  LBP_PDD_DATA_TYPE_BOOLEAN         = 0x07,
  LBP_PDD_DATA_TYPE_ENCODER         = 0x08,
  LBP_PDD_DATA_TYPE_FLOAT           = 0x10,
  LBP_PDD_DATA_TYPE_ENCODER_H       = 0x18,
  LBP_PDD_DATA_TYPE_ENCODER_L       = 0x28,
};

enum LBP_PDD_Data_Directions : uint8_t
{
  LBP_PDD_DIRECTION_INPUT          = 0x00,
  LBP_PDD_DIRECTION_BI_DIRECTIONAL = 0x40,
  LBP_PDD_DIRECTION_OUTPUT         = 0x80
};

enum LBP_PDD_Mode_Types : uint8_t
{
  LBP_PDD_MODE_TYPE_HWMODE = 0x00,
  LBP_PDD_MODE_TYPE_SWMODE = 0x01
};

struct LBP_PDD_Normal // size = 64 bytes
{
  uint8_t RecordType;
  uint8_t DataSize;
  uint8_t DataType;
  uint8_t DataDirection;
  float ParamMin; // offset 4
  float ParamMax;
  uint16_t ParamAddress; // offset 12
  char UnitAndName[50]; // offset 14, wasted space I know... it allows declaring a simple array of structs though
};

struct LBP_PDD_Mode // size = 64 bytes
{
  uint8_t RecordType;
  uint8_t ModeIndex;
  uint8_t ModeType;
  uint8_t _unused;
  char ModeName[60]; // offset 4, wasted space I know... it allows declaring a simple array of structs though
};

union LBP_PDD
{
  LBP_PDD_Normal pdd;
  LBP_PDD_Mode    md;
};

struct LBP_Discovery_Data
{
  uint8_t RxSize;
  uint8_t TxSize;
  uint16_t ptoc;
  uint16_t gtoc;
};

#pragma pack(pop)

#endif // LBP_H
