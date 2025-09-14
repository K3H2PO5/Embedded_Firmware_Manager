/*
 * 样例固件主文件 - 工具配置示例
 * Example Firmware Main File - Tool Configuration Example
 * 
 * 此文件展示了IAR固件发布工具所需的配置参数
 * This file shows the configuration parameters required by IAR Firmware Publish Tool
 */

#include <stdint.h>

#pragma location=0x08004410
__root const char __Firmware_Version[10] = "V0.1.2.3";

#pragma location=0x08004420
__root const char __git_commit_id[7] = "";

#pragma location=0x08004430
__root volatile const uint32_t __file_size = 0;

#pragma location=0x08004434
__root volatile const uint32_t __bin_checksum = 0;