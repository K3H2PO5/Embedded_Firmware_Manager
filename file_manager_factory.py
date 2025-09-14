#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件管理器工厂
根据编译工具类型创建相应的文件管理器
"""

from typing import Union
from lib_IAR.file_manager import IARFileManager
from lib_MDK.file_manager import MDKFileManager


class FileManagerFactory:
    """文件管理器工厂类"""
    
    @staticmethod
    def create_file_manager(compile_tool: str, config: dict, project_path: str = None, path_manager=None) -> Union[IARFileManager, MDKFileManager]:
        """
        根据编译工具类型创建相应的文件管理器
        
        Args:
            compile_tool: 编译工具类型 ('IAR' 或 'MDK')
            config: 配置字典
            project_path: 项目路径
            path_manager: 路径管理器实例
            
        Returns:
            Union[IARFileManager, MDKFileManager]: 相应的文件管理器实例
            
        Raises:
            ValueError: 当编译工具类型不支持时
        """
        if compile_tool.upper() == 'IAR':
            return IARFileManager(config, project_path, path_manager)
        elif compile_tool.upper() == 'MDK':
            return MDKFileManager(config, project_path, path_manager)
        else:
            raise ValueError(f"不支持的编译工具类型: {compile_tool}。支持的类型: IAR, MDK")
    
    @staticmethod
    def get_supported_tools() -> list:
        """
        获取支持的编译工具列表
        
        Returns:
            list: 支持的编译工具列表
        """
        return ['IAR', 'MDK']
    
    @staticmethod
    def get_file_extensions(compile_tool: str) -> dict:
        """
        获取指定编译工具的文件扩展名
        
        Args:
            compile_tool: 编译工具类型
            
        Returns:
            dict: 文件扩展名字典
        """
        if compile_tool.upper() == 'IAR':
            return {
                'output_file': '.out',
                'binary_file': '.bin',
                'project_file': '.ewp',
                'workspace_file': '.eww'
            }
        elif compile_tool.upper() == 'MDK':
            return {
                'output_file': '.axf',
                'binary_file': '.bin',
                'project_file': '.uvprojx',
                'workspace_file': '.uvoptx'
            }
        else:
            raise ValueError(f"不支持的编译工具类型: {compile_tool}")
    
    @staticmethod
    def get_common_methods():
        """
        获取两个管理器都支持的公共方法列表
        
        Returns:
            list: 公共方法名列表
        """
        return [
            'ensure_directory_exists',
            'copy_file',
            'generate_filename',
            'publish_firmware',
            'list_published_files',
            'publish_to_remote',
            'process_bin_file'
        ]


def create_unified_file_manager(compile_tool: str, config: dict, project_path: str = None, path_manager=None):
    """
    创建统一的文件管理器
    
    Args:
        compile_tool: 编译工具类型
        config: 配置字典
        project_path: 项目路径
        path_manager: 路径管理器实例
        
    Returns:
        统一的文件管理器实例
    """
    return FileManagerFactory.create_file_manager(compile_tool, config, project_path, path_manager)


if __name__ == "__main__":
    # 测试工厂模式
    test_config = {
        'fw_publish_directory': './fw_publish',
        'remote_publish_directory': './remote_publish'
    }
    
    print("文件管理器工厂测试")
    
    # 测试IAR管理器
    iar_manager = FileManagerFactory.create_file_manager('IAR', test_config)
    print(f"IAR管理器类型: {type(iar_manager).__name__}")
    
    # 测试MDK管理器
    mdk_manager = FileManagerFactory.create_file_manager('MDK', test_config)
    print(f"MDK管理器类型: {type(mdk_manager).__name__}")
    
    # 显示公共方法
    common_methods = FileManagerFactory.get_common_methods()
    print(f"公共方法: {common_methods}")
    
    # 显示文件扩展名
    iar_extensions = FileManagerFactory.get_file_extensions('IAR')
    print(f"IAR文件扩展名: {iar_extensions}")
    
    mdk_extensions = FileManagerFactory.get_file_extensions('MDK')
    print(f"MDK文件扩展名: {mdk_extensions}")
