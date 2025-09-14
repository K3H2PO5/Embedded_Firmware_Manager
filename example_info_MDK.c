/*
 * 样例固件主文件 - 工具配置示例
 * Example Firmware Main File - Tool Configuration Example
 * 
 * 此文件展示了IAR固件发布工具所需的配置参数
 * This file shows the configuration parameters required by IAR Firmware Publish Tool
 */

#include <stdint.h>

const char __Firmware_Version[10] __attribute__((at(0x8001000)))  = "V0.0.9.7";

const char __git_commit_id[16] __attribute__((at(0x8001010)))  = "";

const uint32_t __file_size __attribute__((at(0x8001020)))  = 0;

const uint32_t __bin_checksum __attribute__((at(0x8001030)))  = 0;

const uint8_t __hash_value[32] __attribute__((at(0x8001040)))  = "";