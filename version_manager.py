#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
固件版本管理模块
负责版本号解析、比较、自动递增等功能
"""

import os
import re
from lib_logger import logger
from typing import Tuple, Optional, List, Dict
from datetime import datetime


class VersionManager:
    """固件版本管理器"""
    
    def __init__(self, config: dict, project_path: str = None, fw_publish_dir: str = None, current_branch: str = None):
        """
        初始化版本管理器
        
        Args:
            config: 配置字典
            project_path: 项目目录路径，用于解析相对路径
            fw_publish_dir: 固件发布目录路径
            current_branch: 当前git分支名称
        """
        self.config = config
        
        # 从配置中获取设置
        # fw_publish_directory现在在project_settings中，需要从外部传入
        self.fw_publish_dir = fw_publish_dir if fw_publish_dir else './fw_publish'
        self.version_pattern = config.get('version_pattern', r'V(\d)\.(\d)\.(\d)\.(\d)')
        self.max_version_parts = config.get('max_version_parts', [9, 9, 9, 9])
        self.current_branch = current_branch
        
        # 将相对路径转换为绝对路径（基于项目目录）
        if project_path and os.path.exists(project_path):
            project_root = os.path.abspath(project_path)
            logger.info(f"使用提供的项目路径: {project_path}")
        else:
            # 如果没有提供项目路径或路径不存在，使用当前工作目录
            project_root = os.getcwd()
            logger.warning(f"项目路径无效或不存在: {project_path}，使用当前工作目录: {project_root}")
        
        logger.info(f"项目根目录: {project_root}")
        logger.info(f"当前工作目录: {os.getcwd()}")
        logger.info(f"原始fw_publish路径: {self.fw_publish_dir}")
        logger.info(f"项目根目录是否存在: {os.path.exists(project_root)}")
        logger.info(f"fw_publish_dir是否为绝对路径: {os.path.isabs(self.fw_publish_dir)}")
        
        # 检查是否为真正的绝对路径（不是以./或../开头的相对路径）
        is_truly_absolute = os.path.isabs(self.fw_publish_dir) and not self.fw_publish_dir.startswith(('./', '../'))
        
        if is_truly_absolute:
            # 如果是真正的绝对路径，直接使用
            self.fw_publish_dir = os.path.abspath(self.fw_publish_dir)
            logger.info(f"绝对路径fw_publish: {self.fw_publish_dir}")
            logger.info(f"绝对路径fw_publish是否存在: {os.path.exists(self.fw_publish_dir)}")
        else:
            # 如果是相对路径，基于项目根目录解析
            # ./fw_publish -> 项目目录/fw_publish
            # ../fw_publish -> 项目目录/../fw_publish
            self.fw_publish_dir = os.path.join(project_root, self.fw_publish_dir)
            self.fw_publish_dir = os.path.abspath(self.fw_publish_dir)
            logger.info(f"解析后的fw_publish路径: {self.fw_publish_dir}")
            logger.info(f"解析后的fw_publish路径是否存在: {os.path.exists(self.fw_publish_dir)}")
            
            # 如果解析后的路径不存在，记录警告但不尝试在父目录查找
            if not os.path.exists(self.fw_publish_dir):
                logger.warning(f"fw_publish目录不存在，将创建: {self.fw_publish_dir}")
        
        # 确保fw_publish目录存在
        self._ensure_fw_publish_directory()
    
    def _ensure_fw_publish_directory(self):
        """确保fw_publish目录存在"""
        try:
            os.makedirs(self.fw_publish_dir, exist_ok=True)
            logger.info(f"固件发布目录已准备: {self.fw_publish_dir}")
        except Exception as e:
            logger.error(f"创建固件发布目录失败: {e}")
    
    def parse_version(self, version_str: str) -> Optional[Tuple[int, int, int, int]]:
        """
        解析版本字符串
        
        Args:
            version_str: 版本字符串，如 "V0.0.1.0"
            
        Returns:
            Tuple[int, int, int, int]: 版本号元组 (major, minor, patch, build)
        """
        try:
            # 移除可能的空白字符
            version_str = version_str.strip()
            
            # 使用正则表达式匹配版本号
            match = re.match(self.version_pattern, version_str)
            if not match:
                logger.warning(f"无法解析版本号: {version_str}")
                return None
            
            # 提取版本号部分
            major = int(match.group(1))
            minor = int(match.group(2))
            patch = int(match.group(3))
            build = int(match.group(4))
            
            logger.info(f"解析版本号: {version_str} -> ({major}, {minor}, {patch}, {build})")
            return (major, minor, patch, build)
            
        except Exception as e:
            logger.error(f"解析版本号失败: {e}")
            return None
    
    def format_version(self, major: int, minor: int, patch: int, build: int) -> str:
        """
        格式化版本号为字符串
        
        Args:
            major: 主版本号
            minor: 次版本号
            patch: 补丁版本号
            build: 构建版本号
            
        Returns:
            str: 格式化的版本字符串
        """
        return f"V{major}.{minor}.{patch}.{build}"
    
    def increment_version(self, version_tuple: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        """
        递增版本号（末位加一，溢出则进位）
        
        Args:
            version_tuple: 当前版本号元组
            
        Returns:
            Tuple[int, int, int, int]: 递增后的版本号元组
        """
        major, minor, patch, build = version_tuple
        
        # 从末位开始递增
        build += 1
        
        # 检查是否需要进位
        if build > self.max_version_parts[3]:
            build = 0
            patch += 1
            
            if patch > self.max_version_parts[2]:
                patch = 0
                minor += 1
                
                if minor > self.max_version_parts[1]:
                    minor = 0
                    major += 1
                    
                    if major > self.max_version_parts[0]:
                        # 如果所有位都溢出，重置为0.0.0.1
                        major = 0
                        minor = 0
                        patch = 0
                        build = 1
                        logger.warning("版本号溢出，重置为 V0.0.0.1")
        
        new_version = (major, minor, patch, build)
        logger.info(f"版本号递增: {self.format_version(*version_tuple)} -> {self.format_version(*new_version)}")
        return new_version
    
    def compare_versions(self, version1: Tuple[int, int, int, int], 
                        version2: Tuple[int, int, int, int]) -> int:
        """
        比较两个版本号
        
        Args:
            version1: 版本号1
            version2: 版本号2
            
        Returns:
            int: 1 if version1 > version2, -1 if version1 < version2, 0 if equal
        """
        for v1, v2 in zip(version1, version2):
            if v1 > v2:
                return 1
            elif v1 < v2:
                return -1
        return 0
    
    def get_latest_version_from_files(self) -> Optional[Tuple[int, int, int, int]]:
        """
        从fw_publish目录中的文件获取最新版本号（仅限当前分支）
        
        Returns:
            Tuple[int, int, int, int]: 最新版本号，如果没有文件则返回None
        """
        try:
            logger.info(f"正在检查fw_publish目录: {self.fw_publish_dir}")
            if not os.path.exists(self.fw_publish_dir):
                logger.warning(f"fw_publish目录不存在: {self.fw_publish_dir}")
                return None
            
            latest_version = None
            latest_file = None
            
            # 遍历fw_publish目录中的文件
            files_in_dir = os.listdir(self.fw_publish_dir)
            logger.info(f"fw_publish目录中的文件数量: {len(files_in_dir)}")
            logger.info(f"fw_publish目录中的文件: {files_in_dir}")
            for filename in files_in_dir:
                logger.info(f"检查文件: {filename}")
                if not filename.endswith('.bin'):
                    logger.info(f"跳过非bin文件: {filename}")
                    continue
                
                # 检查文件名是否属于当前分支
                is_current_branch = self._is_file_from_current_branch(filename)
                logger.info(f"文件 {filename} 是否属于当前分支 {self.current_branch}: {is_current_branch}")
                if not is_current_branch:
                    continue
                
                # 从文件名中提取版本号
                # 文件名格式: {project_name}_{branch}_{version}_{timestamp}_{commit_id}.bin
                version = self._extract_version_from_filename(filename)
                logger.info(f"从文件 {filename} 提取的版本: {version}")
                if version is None:
                    continue
                
                # 比较版本号
                if latest_version is None or self.compare_versions(version, latest_version) > 0:
                    latest_version = version
                    latest_file = filename
                    logger.info(f"更新最新版本: {self.format_version(*version)} (文件: {filename})")
            
            if latest_version:
                logger.info(f"找到当前分支({self.current_branch})最新版本: {self.format_version(*latest_version)} (文件: {latest_file})")
            else:
                logger.info(f"fw_publish目录中没有找到当前分支({self.current_branch})的固件文件")
            
            return latest_version
            
        except Exception as e:
            logger.error(f"获取最新版本号失败: {e}")
            return None
    
    def _is_file_from_current_branch(self, filename: str) -> bool:
        """
        检查文件名是否属于当前分支
        
        Args:
            filename: 文件名
            
        Returns:
            bool: 是否属于当前分支
        """
        if not self.current_branch:
            # 如果没有指定当前分支，则检查所有文件
            return True
        
        try:
            # 文件名格式: {project_name}_{branch}_{version}_{timestamp}_{commit_id}.bin
            # 通过查找版本号模式来定位分支名
            parts = filename.replace('.bin', '').split('_')
            
            if len(parts) < 3:
                return False
            
            # 查找版本号模式 V数字.数字.数字.数字
            version_pattern = re.compile(r'^V\d+\.\d+\.\d+\.\d+$')
            version_index = -1
            
            for i, part in enumerate(parts):
                if version_pattern.match(part):
                    version_index = i
                    break
            
            if version_index == -1 or version_index < 1:
                # 没有找到版本号或版本号在第一个位置
                return False
            
            # 分支名应该在版本号的前一个位置
            file_branch = parts[version_index - 1]
            
            # 比较分支名（忽略大小写）
            is_match = file_branch.lower() == self.current_branch.lower()
            logger.info(f"文件分支: '{file_branch}', 当前分支: '{self.current_branch}', 匹配: {is_match}")
            return is_match
            
        except Exception as e:
            logger.warning(f"检查文件分支失败: {filename}, 错误: {e}")
            return False
    
    def _extract_version_from_filename(self, filename: str) -> Optional[Tuple[int, int, int, int]]:
        """
        从文件名中提取版本号
        
        Args:
            filename: 文件名
            
        Returns:
            Tuple[int, int, int, int]: 版本号元组
        """
        try:
            # 新的文件名格式: {project_name}_{branch}_{version}_{timestamp}_{commit_id}.bin
            # 尝试匹配包含版本号的文件名格式
            # 格式1: ProjectName_branch_V1.2.3.4_20241201_143022_commit.bin
            version_match = re.search(r'_V(\d+)\.(\d+)\.(\d+)\.(\d+)_', filename)
            if version_match:
                major = int(version_match.group(1))
                minor = int(version_match.group(2))
                patch = int(version_match.group(3))
                build = int(version_match.group(4))
                return (major, minor, patch, build)
            
            # 如果没有明确的版本号，返回None
            return None
            
        except Exception as e:
            logger.error(f"从文件名提取版本号失败: {e}")
            return None
    
    def get_next_version(self, current_version_str: str) -> Tuple[str, str]:
        """
        获取下一个版本号
        
        Args:
            current_version_str: 当前版本字符串
            
        Returns:
            Tuple[str, str]: (下一个版本字符串, 版本递增说明)
        """
        try:
            # 解析当前版本
            current_version = self.parse_version(current_version_str)
            if current_version is None:
                # 如果无法解析，使用默认版本
                current_version = (0, 0, 0, 0)
                logger.warning(f"无法解析版本号 {current_version_str}，使用默认版本 V0.0.0.0")
            
            # 获取fw_publish目录中的最新版本
            latest_published = self.get_latest_version_from_files()
            logger.info(f"当前代码版本: {self.format_version(*current_version)}")
            if latest_published:
                logger.info(f"已发布的最新版本: {self.format_version(*latest_published)}")
            else:
                logger.info("没有找到已发布的版本")
            
            # 确定应该使用哪个版本作为基准
            if latest_published is not None:
                # 比较当前版本和已发布的最新版本
                version_comparison = self.compare_versions(current_version, latest_published)
                if version_comparison > 0:
                    # 当前版本更新，直接使用当前版本，不需要递增
                    next_version_str = self.format_version(*current_version)
                    explanation = f"当前版本 {next_version_str} 已高于已发布版本 {self.format_version(*latest_published)}，无需递增"
                    logger.info(explanation)
                    return next_version_str, explanation
                elif version_comparison == 0:
                    # 版本相同，需要递增
                    base_version = current_version
                    version_source = "当前代码版本"
                else:
                    # 已发布版本更新，使用已发布版本并递增
                    base_version = latest_published
                    version_source = "已发布版本"
            else:
                # 没有已发布版本，使用当前版本并递增
                base_version = current_version
                version_source = "当前代码版本"
            
            # 递增版本号
            next_version = self.increment_version(base_version)
            next_version_str = self.format_version(*next_version)
            
            # 生成说明
            explanation = f"基于{version_source} {self.format_version(*base_version)} 自动递增到 {next_version_str}"
            
            logger.info(explanation)
            return next_version_str, explanation
            
        except Exception as e:
            logger.error(f"获取下一个版本号失败: {e}")
            # 返回默认版本
            return "V0.0.0.1", f"获取版本号失败，使用默认版本: {e}"
    
    def list_published_firmware(self) -> List[Dict]:
        """
        列出已发布的固件文件
        
        Returns:
            List[Dict]: 固件文件信息列表
        """
        firmware_list = []
        
        try:
            if not os.path.exists(self.fw_publish_dir):
                return firmware_list
            
            for filename in os.listdir(self.fw_publish_dir):
                if not filename.endswith('.bin'):
                    continue
                
                file_path = os.path.join(self.fw_publish_dir, filename)
                stat = os.stat(file_path)
                
                # 提取版本号
                version = self._extract_version_from_filename(filename)
                version_str = self.format_version(*version) if version else "未知版本"
                
                firmware_info = {
                    'filename': filename,
                    'path': file_path,
                    'version': version_str,
                    'version_tuple': version,
                    'size': stat.st_size,
                    'modified_time': datetime.fromtimestamp(stat.st_mtime),
                    'created_time': datetime.fromtimestamp(stat.st_ctime)
                }
                
                firmware_list.append(firmware_info)
            
            # 按版本号排序（最新的在前）
            firmware_list.sort(key=lambda x: x['version_tuple'] or (0, 0, 0, 0), reverse=True)
            
        except Exception as e:
            logger.error(f"列出已发布固件失败: {e}")
        
        return firmware_list
    
    def cleanup_old_firmware(self, keep_count: int = 10) -> int:
        """
        清理旧的固件文件
        
        Args:
            keep_count: 保留的文件数量
            
        Returns:
            int: 删除的文件数量
        """
        deleted_count = 0
        
        try:
            firmware_list = self.list_published_firmware()
            
            if len(firmware_list) <= keep_count:
                logger.info(f"固件文件数量({len(firmware_list)})不超过保留数量({keep_count})，无需清理")
                return 0
            
            # 删除多余的文件
            files_to_delete = firmware_list[keep_count:]
            for firmware_info in files_to_delete:
                try:
                    os.remove(firmware_info['path'])
                    deleted_count += 1
                    logger.info(f"删除旧固件: {firmware_info['filename']} (版本: {firmware_info['version']})")
                except Exception as e:
                    logger.error(f"删除固件文件失败 {firmware_info['filename']}: {e}")
            
            logger.info(f"固件清理完成，删除了 {deleted_count} 个旧文件")
            
        except Exception as e:
            logger.error(f"清理旧固件失败: {e}")
        
        return deleted_count


def test_version_manager():
    """测试版本管理器功能"""
    # 测试配置
    test_config = {
        'fw_publish_directory': './test_fw_publish',
        'version_pattern': r'V(\d+)\.(\d+)\.(\d+)\.(\d+)',
        'max_version_parts': [99, 99, 99, 99]
    }
    
    manager = VersionManager(test_config)
    
    print("版本管理器测试")
    print(f"固件发布目录: {manager.fw_publish_dir}")
    
    # 测试版本解析
    test_versions = ["V0.0.1.0", "V1.2.3.4", "V10.20.30.40", "V99.99.99.99"]
    for version_str in test_versions:
        parsed = manager.parse_version(version_str)
        if parsed:
            incremented = manager.increment_version(parsed)
            print(f"{version_str} -> {manager.format_version(*parsed)} -> {manager.format_version(*incremented)}")
    
    # 测试版本比较
    v1 = (1, 2, 3, 4)
    v2 = (1, 2, 3, 5)
    result = manager.compare_versions(v1, v2)
    print(f"版本比较: {manager.format_version(*v1)} vs {manager.format_version(*v2)} = {result}")
    
    # 测试获取下一个版本
    next_ver, explanation = manager.get_next_version("V0.0.1.0")
    print(f"下一个版本: {next_ver} - {explanation}")


if __name__ == "__main__":
    
    test_version_manager()
