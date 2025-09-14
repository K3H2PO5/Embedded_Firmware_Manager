#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
路径管理器工厂
根据编译工具类型创建相应的路径管理器
"""

from typing import Union
from lib_IAR.path_manager import IARPathManager
from lib_MDK.path_manager import MDKPathManager


class PathManagerFactory:
    """路径管理器工厂类"""
    
    @staticmethod
    def create_path_manager(compile_tool: str, project_path: str = None) -> Union[IARPathManager, MDKPathManager]:
        """
        根据编译工具类型创建相应的路径管理器
        
        Args:
            compile_tool: 编译工具类型 ('IAR' 或 'MDK')
            project_path: 项目路径
            
        Returns:
            Union[IARPathManager, MDKPathManager]: 相应的路径管理器实例
            
        Raises:
            ValueError: 当编译工具类型不支持时
        """
        if compile_tool.upper() == 'IAR':
            return IARPathManager(project_path)
        elif compile_tool.upper() == 'MDK':
            return MDKPathManager(project_path)
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
