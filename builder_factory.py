#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建器工厂
根据编译工具类型创建相应的构建器
"""

from lib_IAR.builder import IARBuilder
from lib_MDK.builder import MDKBuilder


class BuilderFactory:
    """构建器工厂类"""
    
    @staticmethod
    def create_builder(compile_tool: str, config: dict, configuration: dict = None):
        """
        根据编译工具类型创建相应的构建器
        
        Args:
            compile_tool: 编译工具类型 ('IAR' 或 'MDK')
            config: 配置字典
            configuration: 当前选择的配置信息
            
        Returns:
            相应的构建器实例
        """
        if compile_tool == 'IAR':
            return IARBuilder(config, configuration)
        elif compile_tool == 'MDK':
            return MDKBuilder(config, configuration)
        else:
            # 默认使用IAR
            return IARBuilder(config, configuration)
    
    @staticmethod
    def get_common_methods():
        """
        获取两个构建器都支持的公共方法列表
        
        Returns:
            list: 公共方法名列表
        """
        return [
            'build_project',
            'clean_project',
            'smart_build',
            'build_and_check',
            'check_bin_file',
            'get_bin_file_info',
            'get_build_info',
            'diagnose_environment'
        ]
    
    @staticmethod
    def get_iar_only_methods():
        """
        获取IAR构建器独有的方法列表
        
        Returns:
            list: IAR独有方法名列表
        """
        return [
            'test_iar_command'
        ]
    
    @staticmethod
    def get_mdk_only_methods():
        """
        获取MDK构建器独有的方法列表
        
        Returns:
            list: MDK独有方法名列表
        """
        return [
            'test_mdk_command',
            'get_build_output_path',
            'check_build_output'
        ]


def create_unified_builder(compile_tool: str, config: dict, configuration: dict = None):
    """
    创建统一的构建器
    
    Args:
        compile_tool: 编译工具类型
        config: 配置字典
        configuration: 当前选择的配置信息
        
    Returns:
        统一的构建器实例
    """
    return BuilderFactory.create_builder(compile_tool, config, configuration)


if __name__ == "__main__":
    # 测试工厂模式
    test_config = {
        'iar_installation_path': 'C:/Program Files/IAR Systems',
        'mdk_installation_path': 'C:/Keil_v5',
        'project_path': 'test_project'
    }
    
    print("构建器工厂测试")
    
    # 测试IAR构建器
    iar_builder = BuilderFactory.create_builder('IAR', test_config)
    print(f"IAR构建器类型: {type(iar_builder).__name__}")
    
    # 测试MDK构建器
    mdk_builder = BuilderFactory.create_builder('MDK', test_config)
    print(f"MDK构建器类型: {type(mdk_builder).__name__}")
    
    # 显示公共方法
    common_methods = BuilderFactory.get_common_methods()
    print(f"公共方法: {common_methods}")
    
    # 显示IAR独有方法
    iar_only_methods = BuilderFactory.get_iar_only_methods()
    print(f"IAR独有方法: {iar_only_methods}")
    
    # 显示MDK独有方法
    mdk_only_methods = BuilderFactory.get_mdk_only_methods()
    print(f"MDK独有方法: {mdk_only_methods}")
