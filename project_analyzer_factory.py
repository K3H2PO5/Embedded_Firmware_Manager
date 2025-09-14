#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目分析器工厂
根据编译工具类型创建相应的项目分析器
"""

from lib_IAR.project_analyzer import IARProjectAnalyzer
from lib_MDK.project_analyzer import MDKProjectAnalyzer


class ProjectAnalyzerFactory:
    """项目分析器工厂类"""
    
    @staticmethod
    def create_analyzer(compile_tool: str):
        """
        根据编译工具类型创建相应的项目分析器
        
        Args:
            compile_tool: 编译工具类型 ('IAR' 或 'MDK')
            
        Returns:
            相应的项目分析器实例
        """
        if compile_tool == 'IAR':
            return IARProjectAnalyzer()
        elif compile_tool == 'MDK':
            return MDKProjectAnalyzer()
        else:
            # 默认使用IAR
            return IARProjectAnalyzer()
    
    @staticmethod
    def get_common_methods():
        """
        获取两个分析器都支持的公共方法列表
        
        Returns:
            list: 公共方法名列表
        """
        return [
            'find_build_outputs',
            '_parse_configurations',
            'analyze_icf_file',  # IAR: analyze_icf_file, MDK: analyze_sct_file
            'get_flash_offset_from_configuration'
        ]
    
    @staticmethod
    def get_iar_only_methods():
        """
        获取IAR分析器独有的方法列表
        
        Returns:
            list: IAR独有方法名列表
        """
        return [
            'analyze_ewp_file',
            'find_ewp_file',
            'analyze_icf_file',
            'get_flash_offset_from_configuration'
        ]
    
    @staticmethod
    def get_mdk_only_methods():
        """
        获取MDK分析器独有的方法列表
        
        Returns:
            list: MDK独有方法名列表
        """
        return [
            'analyze_uvprojx_file',
            'extract_flash_start_address_from_sct',
            'get_project_info',
            '_parse_output_directory',
            '_parse_output_name',
            '_parse_sct_file',
            '_parse_debug_mode'
        ]
    
    @staticmethod
    def get_analyze_method_name(compile_tool: str) -> str:
        """
        获取指定编译工具的分析方法名
        
        Args:
            compile_tool: 编译工具类型
            
        Returns:
            str: 分析方法名
        """
        if compile_tool == 'IAR':
            return 'analyze_ewp_file'
        elif compile_tool == 'MDK':
            return 'analyze_uvprojx_file'
        else:
            return 'analyze_ewp_file'
    
    @staticmethod
    def get_file_extension(compile_tool: str) -> str:
        """
        获取指定编译工具的项目文件扩展名
        
        Args:
            compile_tool: 编译工具类型
            
        Returns:
            str: 文件扩展名
        """
        if compile_tool == 'IAR':
            return '.ewp'
        elif compile_tool == 'MDK':
            return '.uvprojx'
        else:
            return '.ewp'
    
    @staticmethod
    def get_config_analyze_method_name(compile_tool: str) -> str:
        """
        获取指定编译工具的配置文件分析方法名
        
        Args:
            compile_tool: 编译工具类型
            
        Returns:
            str: 配置文件分析方法名
        """
        if compile_tool == 'IAR':
            return 'analyze_icf_file'
        elif compile_tool == 'MDK':
            return 'analyze_sct_file'
        else:
            return 'analyze_icf_file'


def create_unified_analyzer(compile_tool: str):
    """
    创建统一的项目分析器
    
    Args:
        compile_tool: 编译工具类型
        
    Returns:
        统一的项目分析器实例
    """
    return ProjectAnalyzerFactory.create_analyzer(compile_tool)


if __name__ == "__main__":
    # 测试工厂模式
    print("项目分析器工厂测试")
    
    # 测试IAR分析器
    iar_analyzer = ProjectAnalyzerFactory.create_analyzer('IAR')
    print(f"IAR分析器类型: {type(iar_analyzer).__name__}")
    
    # 测试MDK分析器
    mdk_analyzer = ProjectAnalyzerFactory.create_analyzer('MDK')
    print(f"MDK分析器类型: {type(mdk_analyzer).__name__}")
    
    # 显示公共方法
    common_methods = ProjectAnalyzerFactory.get_common_methods()
    print(f"公共方法: {common_methods}")
    
    # 显示IAR独有方法
    iar_only_methods = ProjectAnalyzerFactory.get_iar_only_methods()
    print(f"IAR独有方法: {iar_only_methods}")
    
    # 显示MDK独有方法
    mdk_only_methods = ProjectAnalyzerFactory.get_mdk_only_methods()
    print(f"MDK独有方法: {mdk_only_methods}")
    
    # 显示分析方法名
    print(f"IAR分析方法: {ProjectAnalyzerFactory.get_analyze_method_name('IAR')}")
    print(f"MDK分析方法: {ProjectAnalyzerFactory.get_analyze_method_name('MDK')}")
    
    # 显示文件扩展名
    print(f"IAR文件扩展名: {ProjectAnalyzerFactory.get_file_extension('IAR')}")
    print(f"MDK文件扩展名: {ProjectAnalyzerFactory.get_file_extension('MDK')}")
