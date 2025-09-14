#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MDK路径管理模块
负责MDK项目的路径验证、自动查找和路径解析
"""

import os
from lib_logger import logger
from typing import Optional, List, Tuple, Dict
from pathlib import Path
from .project_analyzer import MDKProjectAnalyzer


class MDKPathManager:
    """MDK路径管理器"""
    
    def __init__(self, project_path: str = None):
        """
        初始化MDK路径管理器
        
        Args:
            project_path: 项目根目录路径
        """
        if project_path:
            self.project_path = os.path.abspath(project_path)
        else:
            # 不使用os.getcwd()，避免打包exe时的问题
            # 默认使用空字符串，表示需要用户明确指定项目路径
            self.project_path = ""
            
        self.mdk_analyzer = MDKProjectAnalyzer()
        
        if self.project_path:
            logger.info(f"项目根目录: {self.project_path}")
        else:
            logger.warning("未指定项目路径，请使用set_project_path()方法设置")
    
    def set_project_path(self, project_path: str) -> None:
        """
        设置项目路径
        
        Args:
            project_path: 项目根目录路径
        """
        self.project_path = os.path.abspath(project_path)
        logger.info(f"设置项目根目录: {self.project_path}")
    
    def find_mdk_project(self, pattern: str = "*.uvprojx") -> Optional[str]:
        """
        查找MDK项目文件
        
        Args:
            pattern: 文件匹配模式
            
        Returns:
            str: 找到的项目文件路径，未找到返回None
        """
        try:
            # 在项目目录及其子目录中查找
            search_paths = [
                self.project_path,
                os.path.join(self.project_path, "MDK-ARM"),
                os.path.join(self.project_path, "..", "MDK-ARM"),
                os.path.join(self.project_path, "..", "..", "MDK-ARM"),
                os.path.join(self.project_path, "..", "..", "..", "MDK-ARM")
            ]
            
            for search_path in search_paths:
                if os.path.exists(search_path):
                    # 递归查找匹配的文件
                    for root, dirs, files in os.walk(search_path):
                        for file in files:
                            if file.lower().endswith('.uvprojx'):
                                file_path = os.path.join(root, file)
                                logger.info(f"找到MDK项目文件: {file_path}")
                                return file_path
            
            logger.warning("未找到MDK项目文件")
            return None
            
        except Exception as e:
            logger.error(f"查找MDK项目文件失败: {e}")
            return None
    
    def find_bin_file(self, project_name: str = None, configuration: Dict = None) -> Optional[str]:
        """
        查找编译生成的bin文件
        
        Args:
            project_name: 项目名称
            configuration: 配置信息（如果提供，优先使用）
            
        Returns:
            str: 找到的bin文件路径，未找到返回None
        """
        try:
            # 如果提供了配置信息，优先使用配置中的bin文件路径
            if configuration and configuration.get('bin_file'):
                bin_file = configuration['bin_file']
                if os.path.exists(bin_file):
                    logger.info(f"使用配置中的bin文件: {bin_file}")
                    return bin_file
                else:
                    logger.warning(f"配置中的bin文件不存在: {bin_file}")
            
            # 如果配置中没有bin文件，直接返回None
            logger.warning("配置中未提供bin文件路径")
            
            # 如果以上方法都失败，返回None
            logger.warning("未找到bin文件")
            return None
            
        except Exception as e:
            logger.error(f"查找bin文件失败: {e}")
            return None
    
    def find_axf_file(self, project_name: str = None, configuration: Dict = None) -> Optional[str]:
        """
        查找编译生成的axf文件（MDK使用axf文件，不是out文件）
        
        Args:
            project_name: 项目名称
            configuration: 配置信息（如果提供，优先使用）
            
        Returns:
            str: 找到的axf文件路径，未找到返回None
        """
        try:
            # 如果提供了配置信息，优先使用配置中的axf文件路径
            if configuration:
                logger.info(f"查找axf文件，配置信息: {configuration}")
                if configuration.get('axf_file'):
                    axf_file = configuration['axf_file']
                    logger.info(f"配置中的axf文件路径: {axf_file}")
                    if os.path.exists(axf_file):
                        logger.info(f"使用配置中的axf文件: {axf_file}")
                        return axf_file
                    else:
                        logger.warning(f"配置中的axf文件不存在: {axf_file}")
                else:
                    logger.warning("配置中未提供axf_file字段")
            else:
                logger.warning("未提供配置信息")
            
            # 如果配置中没有axf文件，直接返回None
            logger.warning("配置中未提供axf文件路径")
            return None
            
        except Exception as e:
            logger.error(f"查找axf文件失败: {e}")
            return None
    
    def find_info_file(self, info_file_name: str) -> Optional[str]:
        """
        在项目中查找指定的信息文件
        
        Args:
            info_file_name: 要查找的具体文件名（包含扩展名），如"main.c"
        
        Returns:
            str: 找到的信息文件路径，未找到或找到多个则返回None
            
        Note:
            搜索时会自动排除以下目录：
            - .git (Git版本控制目录)
            - .clion (CLion IDE配置目录)
            - .idea (IntelliJ IDEA配置目录)
            - cmake* (以cmake开头的构建目录)
        """
        try:
            # 检查项目路径是否已设置
            if not self.project_path:
                logger.error("项目路径未设置，无法查找信息文件")
                return None
            
            if not info_file_name or not info_file_name.strip():
                logger.error("信息文件名不能为空")
                return None
            
            logger.info(f"在项目 {self.project_path} 中查找信息文件: {info_file_name}")
            
            # 检查项目路径是否存在
            if not os.path.exists(self.project_path):
                logger.error(f"项目路径不存在: {self.project_path}")
                return None
            
            # 递归搜索文件
            found_files = []
            
            # 定义要排除的目录
            excluded_dirs = {'.git', '.clion', '.idea'}
            
            for root, dirs, files in os.walk(self.project_path):
                # 排除以cmake开头的目录和其他不相关目录
                dirs[:] = [d for d in dirs if not (d in excluded_dirs or d.startswith('cmake'))]
                
                for file in files:
                    if file == info_file_name:  # 精确匹配文件名
                        file_path = os.path.join(root, file)
                        found_files.append(file_path)
            
            if len(found_files) == 0:
                logger.error(f"未找到信息文件: {info_file_name}")
                logger.error(f"请检查：")
                logger.error(f"1. 文件名是否正确（包括扩展名）")
                logger.error(f"2. 文件是否存在于项目目录中")
                logger.error(f"3. 在设置中正确配置信息文件名")
                return None
            elif len(found_files) == 1:
                logger.info(f"找到信息文件: {found_files[0]}")
                return found_files[0]
            else:
                logger.error(f"找到多个信息文件 ({len(found_files)}个): {info_file_name}")
                logger.error(f"请删除多余的文件或在设置中指定具体的文件路径：")
                for i, file_path in enumerate(found_files, 1):
                    logger.error(f"  {i}. {file_path}")
                logger.error(f"建议保留项目源代码中的文件，删除构建系统生成的临时文件")
                return None
                
        except Exception as e:
            logger.error(f"查找信息文件失败: {e}")
            return None
    
    def find_info_file_with_details(self, info_file_name: str) -> tuple[Optional[str], str]:
        """
        在项目中查找指定的信息文件，并返回详细的错误信息
        
        Args:
            info_file_name: 要查找的具体文件名（包含扩展名），如"main.c"
        
        Returns:
            tuple: (文件路径, 错误信息)
                - 如果找到唯一文件：返回 (文件路径, "")
                - 如果未找到文件：返回 (None, 详细错误信息)
                - 如果找到多个文件：返回 (None, 详细错误信息)
        """
        try:
            # 检查项目路径是否已设置
            if not self.project_path:
                return None, "项目路径未设置，无法查找信息文件"
            
            if not info_file_name or not info_file_name.strip():
                return None, "信息文件名不能为空"
            
            logger.info(f"在项目 {self.project_path} 中查找信息文件: {info_file_name}")
            
            # 检查项目路径是否存在
            if not os.path.exists(self.project_path):
                return None, f"项目路径不存在: {self.project_path}"
            
            # 递归搜索文件
            found_files = []
            
            # 定义要排除的目录
            excluded_dirs = {'.git', '.clion', '.idea'}
            
            for root, dirs, files in os.walk(self.project_path):
                # 排除以cmake开头的目录和其他不相关目录
                dirs[:] = [d for d in dirs if not (d in excluded_dirs or d.startswith('cmake'))]
                
                for file in files:
                    if file == info_file_name:  # 精确匹配文件名
                        file_path = os.path.join(root, file)
                        found_files.append(file_path)
            
            if len(found_files) == 0:
                error_msg = f"未找到信息文件: {info_file_name}\n请检查：\n1. 文件名是否正确（包括扩展名）\n2. 文件是否存在于项目目录中\n3. 在设置中正确配置信息文件名"
                logger.error(error_msg)
                return None, error_msg
            elif len(found_files) == 1:
                logger.info(f"找到信息文件: {found_files[0]}")
                return found_files[0], ""
            else:
                error_msg = f"找到多个信息文件 ({len(found_files)}个): {info_file_name}\n请删除多余的文件或在设置中指定具体的文件路径：\n"
                for i, file_path in enumerate(found_files, 1):
                    error_msg += f"  {i}. {file_path}\n"
                error_msg += "建议保留项目源代码中的文件，删除构建系统生成的临时文件"
                logger.error(error_msg)
                return None, error_msg
                
        except Exception as e:
            error_msg = f"查找信息文件失败: {e}"
            logger.error(error_msg)
            return None, error_msg
    
    def resolve_relative_path(self, relative_path: str) -> str:
        """
        解析相对路径为绝对路径
        
        Args:
            relative_path: 相对路径
            
        Returns:
            str: 绝对路径
        """
        if os.path.isabs(relative_path):
            return relative_path
        
        # 基于项目根目录解析相对路径
        absolute_path = os.path.join(self.project_path, relative_path)
        absolute_path = os.path.normpath(absolute_path)
        
        logger.info(f"解析相对路径: {relative_path} -> {absolute_path}")
        return absolute_path
    
    def validate_paths(self, paths: dict) -> Tuple[bool, List[str]]:
        """
        验证路径是否存在
        
        Args:
            paths: 路径字典，键为路径名称，值为路径字符串
            
        Returns:
            Tuple[bool, List[str]]: (是否全部有效, 无效路径列表)
        """
        invalid_paths = []
        
        for name, path in paths.items():
            if not path:
                continue
                
            # 解析相对路径
            if not os.path.isabs(path):
                path = self.resolve_relative_path(path)
            
            if not os.path.exists(path):
                invalid_paths.append(f"{name}: {path}")
                logger.warning(f"路径不存在: {name} = {path}")
            else:
                logger.info(f"路径有效: {name} = {path}")
        
        return len(invalid_paths) == 0, invalid_paths
    
    def auto_find_paths(self, config: dict) -> dict:
        """
        自动查找并更新配置中的路径
        
        Args:
            config: 配置字典
            
        Returns:
            dict: 更新后的配置字典
        """
        updated_config = config.copy()
        
        # 确保project_settings存在
        if 'project_settings' not in updated_config:
            updated_config['project_settings'] = {}
        
        project_settings = updated_config['project_settings']
        
        # 查找MDK项目文件
        current_project = project_settings.get('mdk_project_path', '')
        if not current_project or not os.path.exists(current_project):
            project_path = self.find_mdk_project()
            if project_path:
                project_settings['mdk_project_path'] = project_path
                updated_config['mdk_project_path'] = project_path  # 同时更新根级别
                logger.info(f"自动找到MDK项目文件: {project_path}")
        
        # 查找bin文件
        current_bin = project_settings.get('output_bin_path', '')
        if not current_bin or not os.path.exists(current_bin):
            # 尝试从项目文件中获取项目名称
            project_name = self._extract_project_name_from_uvprojx(project_settings.get('mdk_project_path', ''))
            if not project_name:
                project_name = 'MCU'  # 默认项目名称
            
            bin_path = self.find_bin_file(project_name)
            if bin_path:
                project_settings['output_bin_path'] = bin_path
                updated_config['output_bin_path'] = bin_path  # 同时更新根级别
                logger.info(f"自动找到bin文件: {bin_path}")
        
        # 自动获取flash偏移地址
        if 'binary_settings' not in updated_config:
            updated_config['binary_settings'] = {}
        
        current_bin_start = updated_config['binary_settings'].get('bin_start_address', 0)
        logger.info(f"当前bin_start_address: 0x{current_bin_start:X}")
        if current_bin_start == 0:
            logger.info("尝试自动获取flash偏移地址...")
            flash_offset = self.get_flash_offset_from_configuration()
            if flash_offset:
                updated_config['binary_settings']['bin_start_address'] = flash_offset
                logger.info(f"自动获取flash偏移地址成功: 0x{flash_offset:X}")
            else:
                # 如果无法自动获取，设置一个默认值（STM32的常见起始地址）
                default_flash_offset = 0x08000000
                updated_config['binary_settings']['bin_start_address'] = default_flash_offset
                logger.warning(f"无法自动获取flash偏移地址，使用默认值: 0x{default_flash_offset:X}")
                logger.warning("请检查MDK项目文件是否正确配置，或手动设置正确的起始地址")
        else:
            logger.info(f"使用已配置的bin_start_address: 0x{current_bin_start:X}")
        
        # 验证最终配置
        final_bin_start = updated_config['binary_settings'].get('bin_start_address', 0)
        logger.info(f"最终bin_start_address配置: 0x{final_bin_start:X}")
        
        return updated_config
    
    def _extract_project_name_from_uvprojx(self, uvprojx_path: str) -> Optional[str]:
        """
        从uvprojx文件中提取项目名称（bin文件名）
        
        Args:
            uvprojx_path: uvprojx文件路径
            
        Returns:
            str: 项目名称（bin文件名），失败时返回None
        """
        try:
            if not uvprojx_path or not os.path.exists(uvprojx_path):
                return None
            
            # 使用MDK项目分析器解析项目文件
            result = self.mdk_analyzer.analyze_uvprojx_file(uvprojx_path)
            if result and result.get('configurations'):
                # 获取第一个配置的输出名称
                first_config = result['configurations'][0]
                project_name = first_config.get('output_name', '')
                if project_name:
                    logger.info(f"从uvprojx文件提取项目名称: {project_name}")
                    return project_name
            
            # 如果没找到，使用文件名作为默认值
            project_name = os.path.splitext(os.path.basename(uvprojx_path))[0]
            logger.warning(f"无法从uvprojx文件内容提取项目名称，使用文件名: {project_name}")
            return project_name
            
        except Exception as e:
            logger.error(f"从uvprojx文件提取项目名称失败: {e}")
            # 失败时使用文件名作为默认值
            try:
                project_name = os.path.splitext(os.path.basename(uvprojx_path))[0]
                logger.warning(f"解析失败，使用文件名作为默认值: {project_name}")
                return project_name
            except:
                return None
    
    def get_flash_offset_from_configuration(self, configuration: Dict = None) -> Optional[int]:
        """
        从配置信息中获取flash偏移地址
        
        Args:
            configuration: 配置信息（如果提供，优先使用）
            
        Returns:
            int: flash偏移地址，失败返回None
        """
        try:
            # 如果提供了配置信息，优先使用配置中的SCT文件
            if configuration and configuration.get('sct_file'):
                sct_file = configuration['sct_file']
                if os.path.exists(sct_file):
                    logger.info(f"使用配置中的SCT文件: {sct_file}")
                    return self.mdk_analyzer.extract_flash_start_address_from_sct(sct_file)
                else:
                    logger.warning(f"配置中的SCT文件不存在: {sct_file}")
            
            # 如果配置中没有SCT文件，直接返回None
            logger.warning("配置中未提供SCT文件路径")
            
            logger.warning("未找到有效的SCT文件")
            return None
                
        except Exception as e:
            logger.error(f"获取flash偏移地址失败: {e}")
            return None


def test_mdk_path_manager():
    """测试MDK路径管理器功能"""
    manager = MDKPathManager()
    
    print("MDK路径管理器测试")
    print(f"项目根目录: {manager.project_path}")
    
    # 查找各种文件
    project = manager.find_mdk_project()
    print(f"MDK项目文件: {project}")
    
    bin_file = manager.find_bin_file()
    print(f"Bin文件: {bin_file}")
    
    axf_file = manager.find_axf_file()
    print(f"Axf文件: {axf_file}")
    
    # 测试新的find_info_file方法
    print("测试find_info_file方法:")
    # 使用默认文件名进行测试
    source_file = manager.find_info_file("main.c")
    print(f"项目信息文件: {source_file}")
    
    # 测试查找main.c文件
    print("\n测试查找main.c文件:")
    main_c = manager.find_info_file("main.c")
    print(f"项目Main.c文件: {main_c}")
    
    # 测试查找特定文件
    print("\n测试查找example_info.c:")
    example_file = manager.find_info_file("example_info_MDK.c")
    print(f"项目Example文件: {example_file}")


if __name__ == "__main__":
    
    test_mdk_path_manager()
