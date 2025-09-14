#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具版本管理模块
负责工具本身的版本号管理，包括自动修改version.py文件版本号
"""

import os
import sys
import re
from lib_logger import logger
from typing import Optional, Tuple
from datetime import datetime


class ToolVersionManager:
    """工具版本管理器"""
    
    def __init__(self):
        """初始化工具版本管理器"""
        
        # 版本文件路径
        if hasattr(sys, 'frozen') and sys.frozen:
            # 如果是打包后的exe，使用exe所在目录
            base_path = os.path.dirname(sys.executable)
        else:
            # 如果是开发环境，使用脚本所在目录
            base_path = os.path.dirname(__file__)
        
        self.version_file_path = os.path.join(base_path, 'version.py')
        
        # 版本号模式 - 支持数量不定的空格和注释
        self.version_pattern = r'VERSION\s*=\s*["\']([^"\']+)["\'](?:\s*#.*)?'
        self.version_format = 'VERSION = "{}"'
        
        logger.info(f"工具版本管理器初始化，版本文件路径: {self.version_file_path}")
    
    def get_current_version(self) -> str:
        """
        获取当前工具版本号
        
        Returns:
            str: 当前版本号
        """
        try:
            if not os.path.exists(self.version_file_path):
                logger.error(f"版本文件不存在: {self.version_file_path}")
                return "1.0.0.0"
            
            with open(self.version_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            match = re.search(self.version_pattern, content)
            if match:
                version = match.group(1)
                logger.info(f"当前版本号: {version}")
                return version
            else:
                logger.error("版本文件中未找到版本号")
                return "1.0.0.0"
                
        except Exception as e:
            logger.error(f"读取版本号失败: {e}")
            return "1.0.0.0"
    
    def increment_version(self, increment_type: str = 'patch') -> str:
        """
        递增版本号
        
        Args:
            increment_type: 递增类型 ('major', 'minor', 'patch', 'build')
            
        Returns:
            str: 新的版本号
        """
        current_version = self.get_current_version()
        version_parts = current_version.split('.')
        
        if len(version_parts) != 4:
            logger.error(f"版本号格式错误: {current_version}")
            return current_version
        
        try:
            major, minor, patch, build = map(int, version_parts)
            
            if increment_type == 'major':
                major += 1
                minor = 0
                patch = 0
                build = 0
            elif increment_type == 'minor':
                minor += 1
                patch = 0
                build = 0
            elif increment_type == 'patch':
                patch += 1
                build = 0
            elif increment_type == 'build':
                build += 1
            else:
                logger.error(f"无效的递增类型: {increment_type}")
                return current_version
            
            new_version = f"{major}.{minor}.{patch}.{build}"
            logger.info(f"版本号递增: {current_version} -> {new_version}")
            return new_version
            
        except ValueError as e:
            logger.error(f"版本号解析失败: {e}")
            return current_version
    
    def update_version(self, new_version: str) -> bool:
        """
        更新版本号到文件
        
        Args:
            new_version: 新的版本号
            
        Returns:
            bool: 是否更新成功
        """
        try:
            if not os.path.exists(self.version_file_path):
                logger.error(f"版本文件不存在: {self.version_file_path}")
                return False
            
            with open(self.version_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替换版本号
            new_content = re.sub(self.version_pattern, self.version_format.format(new_version), content)
            
            if new_content == content:
                logger.error("版本号替换失败，可能格式不匹配")
                return False
            
            with open(self.version_file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logger.info(f"版本号更新成功: {new_version}")
            return True
            
        except Exception as e:
            logger.error(f"更新版本号失败: {e}")
            return False
    
    def get_version_info(self) -> dict:
        """
        获取版本信息
        
        Returns:
            dict: 版本信息字典
        """
        version = self.get_current_version()
        return {
            'version': version,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'file_path': self.version_file_path
        }
    
    def auto_increment_and_update(self, increment_type: str = 'patch') -> Tuple[bool, str]:
        """
        自动递增版本号并更新文件
        
        Args:
            increment_type: 递增类型
            
        Returns:
            Tuple[bool, str]: (是否成功, 新版本号)
        """
        new_version = self.increment_version(increment_type)
        success = self.update_version(new_version)
        return success, new_version
    
    def parse_version(self, version_str: str) -> Optional[Tuple[int, int, int, int]]:
        """
        解析版本字符串
        
        Args:
            version_str: 版本字符串，格式如 "1.0.1.9"
            
        Returns:
            tuple: (major, minor, revision, build) 或 None
        """
        pattern = r'(\d+)\.(\d+)\.(\d+)\.(\d+)'
        match = re.match(pattern, version_str)
        if match:
            return tuple(int(x) for x in match.groups())
        return None
    
    def format_version(self, major: int, minor: int, revision: int, build: int) -> str:
        """
        格式化版本号
        
        Args:
            major, minor, revision, build: 版本号各部分
            
        Returns:
            str: 格式化后的版本号
        """
        return f"{major}.{minor}.{revision}.{build}"
    
    def increment_version_advanced(self, major: int, minor: int, revision: int, build: int) -> Tuple[int, int, int, int]:
        """
        高级版本号递增（支持进位）
        注意：每个版本部分限制在0-9范围内
        
        Args:
            major, minor, revision, build: 当前版本号
            
        Returns:
            tuple: 递增后的版本号
        """
        # 递增build号
        build += 1
        
        # 处理进位
        if build > 9:
            build = 0
            revision += 1
            
            if revision > 9:
                revision = 0
                minor += 1
                
                if minor > 9:
                    minor = 0
                    major += 1
                    
                    if major > 9:
                        major = 9  # 限制在9
                        minor = 9
                        revision = 9
                        build = 9
        
        return major, minor, revision, build
    
    def increment_and_update_advanced(self) -> Tuple[bool, str]:
        """
        高级版本号递增并更新文件（用于构建脚本）
        
        Returns:
            Tuple[bool, str]: (是否成功, 新版本号)
        """
        try:
            # 获取当前版本
            current_version = self.get_current_version()
            if not current_version:
                logger.error("无法获取当前版本号")
                return False, ""
            
            logger.info(f"当前版本: {current_version}")
            
            # 解析版本
            version_parts = self.parse_version(current_version)
            if not version_parts:
                logger.error("版本号格式无效")
                return False, ""
            
            # 递增版本
            new_parts = self.increment_version_advanced(*version_parts)
            new_version = self.format_version(*new_parts)
            
            logger.info(f"新版本: {new_version}")
            
            # 更新文件
            if self.update_version(new_version):
                logger.info(f"版本递增成功: {current_version} -> {new_version}")
                return True, new_version
            else:
                logger.error("版本更新失败")
                return False, ""
                
        except Exception as e:
            logger.error(f"版本递增失败: {e}")
            return False, ""