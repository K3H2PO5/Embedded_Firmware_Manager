#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信息管理器工厂
根据编译工具类型创建相应的信息管理器
统一管理版本信息更新和配置分析功能
"""

from lib_IAR.info_manager import IARInfoManager
from lib_MDK.info_manager import MDKInfoManager


class InfoManagerFactory:
    """信息管理器工厂类"""
    
    @staticmethod
    def create_manager(compile_tool: str, config: dict):
        """
        根据编译工具类型创建相应的信息管理器
        
        Args:
            compile_tool: 编译工具类型 ('IAR' 或 'MDK')
            config: 配置字典
            
        Returns:
            相应的信息管理器实例
        """
        if compile_tool == 'IAR':
            return IARInfoManager(config)
        elif compile_tool == 'MDK':
            return MDKInfoManager(config)
        else:
            # 默认使用IAR
            return IARInfoManager(config)
    
    @staticmethod
    def get_common_methods():
        """
        获取两个管理器都支持的公共方法列表
        
        Returns:
            list: 公共方法名列表
        """
        return [
            'extract_version_from_info_file',
            'update_version_in_info_file',
            'validate_version_format',
            'get_version_line_info',
            'analyze_config_file',
            'validate_config_file'
        ]
    
    @staticmethod
    def get_iar_only_methods():
        """
        获取IAR管理器独有的方法列表
        
        Returns:
            list: IAR独有方法名列表
        """
        return [
            '_find_pragma_location'
        ]
    
    @staticmethod
    def get_mdk_only_methods():
        """
        获取MDK管理器独有的方法列表
        
        Returns:
            list: MDK独有方法名列表
        """
        return [
            'update_file_size_in_info_file',
            'update_checksum_in_info_file',
            'get_file_size_line_info',
            'get_checksum_line_info',
            '_find_attribute_at_location'
        ]
    
    @staticmethod
    def get_syntax_example(compile_tool: str) -> str:
        """
        获取指定编译工具的语法示例
        
        Args:
            compile_tool: 编译工具类型
            
        Returns:
            str: 语法示例
        """
        if compile_tool == 'IAR':
            return """
IAR语法示例:
#pragma location=0x08004410
__root const char __Firmware_Version[10] = "V1.0.0.0";
#pragma location=0x08004420
__root const char __git_commit_id[7] = "";
#pragma location=0x08004430
__root volatile const uint32_t __file_size = 0;
#pragma location=0x08004434
__root volatile const uint32_t __bin_checksum = 0;
#pragma location=0x08004438
__root volatile const uint32_t __hash_value = 0;
"""
        elif compile_tool == 'MDK':
            return """
MDK语法示例:
const char __Firmware_Version[10] __attribute__((at(0x8001000))) = "V0.0.7.4";
const char __git_commit_id[16] __attribute__((at(0x8001010))) = "";
const uint32_t __file_size __attribute__((at(0x8001020))) = 0;
const uint32_t __bin_checksum __attribute__((at(0x8001030))) = 0;
const uint8_t __hash_value[32] __attribute__((at(0x8001040))) = "";
"""
        else:
            return "不支持的编译工具"


def create_unified_manager(compile_tool: str, config: dict):
    """
    创建统一的信息管理器
    
    Args:
        compile_tool: 编译工具类型
        config: 配置字典
        
    Returns:
        统一的信息管理器实例
    """
    return InfoManagerFactory.create_manager(compile_tool, config)


if __name__ == "__main__":
    # 测试工厂模式
    test_config = {
        'firmware_version_keyword': '__Firmware_Version',
        'file_size_keyword': '__file_size',
        'bin_checksum_keyword': '__bin_checksum'
    }
    
    print("信息管理器工厂测试")
    
    # 测试IAR管理器
    iar_manager = InfoManagerFactory.create_manager('IAR', test_config)
    print(f"IAR管理器类型: {type(iar_manager).__name__}")
    
    # 测试MDK管理器
    mdk_manager = InfoManagerFactory.create_manager('MDK', test_config)
    print(f"MDK管理器类型: {type(mdk_manager).__name__}")
    
    # 显示公共方法
    common_methods = InfoManagerFactory.get_common_methods()
    print(f"公共方法: {common_methods}")
    
    # 显示IAR独有方法
    iar_only_methods = InfoManagerFactory.get_iar_only_methods()
    print(f"IAR独有方法: {iar_only_methods}")
    
    # 显示MDK独有方法
    mdk_only_methods = InfoManagerFactory.get_mdk_only_methods()
    print(f"MDK独有方法: {mdk_only_methods}")
    
    # 显示语法示例
    print("\nIAR语法示例:")
    print(InfoManagerFactory.get_syntax_example('IAR'))
    
    print("\nMDK语法示例:")
    print(InfoManagerFactory.get_syntax_example('MDK'))
