#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MDK文件管理模块
负责MDK项目的文件重命名、移动、目录管理等操作
"""

import os
import sys
import shutil
from lib_logger import logger
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional, List, Dict


class MDKFileManager:
    """MDK文件管理器"""
    
    def __init__(self, config: dict, project_path: str = None, path_manager=None):
        """
        初始化MDK文件管理器
        
        Args:
            config: 配置字典，包含文件管理相关设置
            project_path: 项目目录路径，用于解析相对路径
            path_manager: 路径管理器实例
        """
        self.config = config
        
        # 保存项目路径和路径管理器
        self.project_path = project_path
        self.path_manager = path_manager
        
        # 从配置中获取设置
        self.fw_publish_directory = config.get('fw_publish_directory', './fw_publish')
        self.remote_publish_directory = config.get('remote_publish_directory', '')
        
        # 使用项目路径的文件夹名称作为项目名称
        if project_path:
            self.project_name = os.path.basename(os.path.abspath(project_path))
            logger.info(f"使用项目路径文件夹名称作为项目名称: {self.project_name}")
        else:
            self.project_name = config.get('project_name', 'MCU')
            logger.info(f"使用配置中的项目名称: {self.project_name}")
        
        # 将相对路径转换为绝对路径（基于项目目录）
        if project_path:
            self.fw_publish_directory = os.path.abspath(os.path.join(project_path, self.fw_publish_directory))
            if self.remote_publish_directory:
                self.remote_publish_directory = os.path.abspath(os.path.join(project_path, self.remote_publish_directory))
        
        logger.info(f"固件发布目录: {self.fw_publish_directory}")
        if self.remote_publish_directory:
            logger.info(f"远程发布目录: {self.remote_publish_directory}")
    
    def ensure_directory_exists(self, directory_path: str) -> bool:
        """
        确保目录存在，如果不存在则创建
        
        Args:
            directory_path: 目录路径
            
        Returns:
            bool: 是否成功创建或目录已存在
        """
        try:
            if not os.path.exists(directory_path):
                os.makedirs(directory_path, exist_ok=True)
                logger.info(f"创建目录: {directory_path}")
            return True
        except Exception as e:
            logger.error(f"创建目录失败: {directory_path}, 错误: {e}")
            return False
    
    def copy_file(self, source_path: str, destination_path: str) -> bool:
        """
        复制文件
        
        Args:
            source_path: 源文件路径
            destination_path: 目标文件路径
            
        Returns:
            bool: 是否复制成功
        """
        try:
            # 确保目标目录存在
            dest_dir = os.path.dirname(destination_path)
            if not self.ensure_directory_exists(dest_dir):
                return False
            
            # 复制文件
            shutil.copy2(source_path, destination_path)
            logger.info(f"文件复制成功: {source_path} -> {destination_path}")
            return True
        except Exception as e:
            logger.error(f"文件复制失败: {source_path} -> {destination_path}, 错误: {e}")
            return False
    
    def generate_filename(self, version: str, commit_id: str, configuration: str = None, 
                         timestamp: Optional[datetime] = None, add_timestamp: bool = True, 
                         branch_name: str = "main") -> str:
        """
        生成固件文件名
        
        Args:
            version: 版本号
            commit_id: Git提交ID
            configuration: 编译配置名称
            timestamp: 时间戳
            add_timestamp: 是否在文件名中添加时间戳
            branch_name: Git分支名称
            
        Returns:
            str: 生成的文件名
        """
        try:
            # 基础文件名
            base_name = f"{self.project_name}_{branch_name}_{version}_{commit_id}"
            
            # 添加配置名称
            if configuration:
                base_name += f"_{configuration}"
            
            # 添加时间戳
            if add_timestamp and timestamp:
                timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
                base_name += f"_{timestamp_str}"
            
            # 添加文件扩展名
            filename = f"{base_name}.bin"
            
            logger.info(f"生成文件名: {filename}")
            return filename
        except Exception as e:
            logger.error(f"生成文件名失败: {e}")
            return f"{self.project_name}_main_{version}_{commit_id}.bin"
    
    def publish_firmware(self, source_bin_path: str, commit_id: str, version: str,
                        timestamp: Optional[datetime] = None, add_timestamp: bool = True, 
                        publish_out_file: bool = False, configuration: Dict = None, 
                        branch_name: str = "main") -> Tuple[bool, str, dict]:
        """
        发布固件到fw_publish目录
        
        Args:
            source_bin_path: 源bin文件路径
            version: 版本号
            commit_id: Git提交ID
            timestamp: 时间戳
            add_timestamp: 是否在文件名中添加时间戳
            publish_out_file: 是否同时发布.axf文件
            configuration: 配置信息
            
        Returns:
            Tuple[bool, str, dict]: (是否成功, 消息, 文件信息)
        """
        try:
            # 确保发布目录存在
            if not self.ensure_directory_exists(self.fw_publish_directory):
                return False, "无法创建固件发布目录", {}
            
            # 生成文件名
            config_name = configuration.get('name', '') if configuration else ''
            new_filename = self.generate_filename(version, commit_id, config_name, timestamp, add_timestamp, branch_name)
            destination_path = os.path.join(self.fw_publish_directory, new_filename)
            
            # 复制bin文件
            if self.copy_file(source_bin_path, destination_path):
                result_info = {
                    'source_path': source_bin_path,
                    'destination_path': destination_path,
                    'file_size': os.path.getsize(destination_path),
                    'operation': 'publish',
                    'timestamp': timestamp or datetime.now(),
                    'out_file': None,
                    'out_destination_path': None
                }
                
                success_msg = f"固件发布成功\n"
                success_msg += f"源文件: {source_bin_path}\n"
                success_msg += f"目标文件: {destination_path}\n"
                success_msg += f"文件大小: {result_info['file_size']} 字节\n"
                success_msg += f"版本: {version}\n"
                success_msg += f"Commit ID: {commit_id}\n"
                success_msg += f"时间戳: {result_info['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}"
                
                # 如果需要发布.axf文件
                if publish_out_file:
                    logger.info(f"需要发布.axf文件，publish_out_file: {publish_out_file}")
                    axf_file_path = None
                    if self.path_manager:
                        logger.info("path_manager存在，开始查找.axf文件")
                        axf_file_path = self.path_manager.find_axf_file(configuration=configuration)
                    else:
                        logger.warning("path_manager为None，无法查找.axf文件")
                    
                    if axf_file_path and os.path.exists(axf_file_path):
                        # 生成.axf文件名（与bin文件名相同，但扩展名为.axf）
                        axf_filename = new_filename.replace('.bin', '.axf')
                        axf_destination_path = os.path.join(self.fw_publish_directory, axf_filename)
                        
                        # 保存.axf文件信息到result_info
                        result_info['out_file'] = axf_file_path
                        result_info['out_destination_path'] = axf_destination_path
                        
                        if self.copy_file(axf_file_path, axf_destination_path):
                            success_msg += f"\n.axf文件发布成功: {axf_destination_path}"
                            logger.info(f".axf文件发布成功: {axf_file_path} -> {axf_destination_path}")
                        else:
                            success_msg += f"\n.axf文件发布失败: {axf_file_path}"
                            logger.warning(f".axf文件发布失败: {axf_file_path}")
                    else:
                        success_msg += f"\n未找到对应的.axf文件"
                        logger.warning(f"未找到对应的.axf文件，源bin文件: {source_bin_path}")
                
                return True, success_msg, result_info
            else:
                return False, "固件发布失败", {}
                
        except Exception as e:
            logger.error(f"发布固件失败: {e}")
            return False, f"发布固件失败: {e}", {}
    
    def list_published_files(self) -> List[Dict]:
        """
        列出已发布的文件
        
        Returns:
            List[Dict]: 文件信息列表
        """
        files = []
        try:
            if os.path.exists(self.fw_publish_directory):
                for filename in os.listdir(self.fw_publish_directory):
                    file_path = os.path.join(self.fw_publish_directory, filename)
                    if os.path.isfile(file_path):
                        stat = os.stat(file_path)
                        files.append({
                            'name': filename,
                            'path': file_path,
                            'size': stat.st_size,
                            'modified': datetime.fromtimestamp(stat.st_mtime)
                        })
        except Exception as e:
            logger.error(f"列出已发布文件失败: {e}")
        
        return files
    
    def publish_to_remote(self, bin_file_path: str, release_note_path: str, branch_name: str = "main", 
                         publish_out_file: bool = False, configuration: Dict = None) -> Tuple[bool, str, dict]:
        """
        发布到远程目录
        
        Args:
            bin_file_path: bin文件路径
            release_note_path: release note文件路径
            branch_name: 分支名称
            publish_out_file: 是否同时发布.axf文件
            configuration: 配置信息
            
        Returns:
            Tuple[bool, str, dict]: (成功标志, 消息, 结果信息)
        """
        try:
            if not self.remote_publish_directory:
                return False, "远程发布目录未配置", {}
            
            # 创建远程子目录（按项目名称_分支名称）
            remote_sub_dir = os.path.join(self.remote_publish_directory, f"{self.project_name}_{branch_name}")
            if not self.ensure_directory_exists(remote_sub_dir):
                return False, f"无法创建远程子目录: {remote_sub_dir}", {}
            
            result_info = {
                'remote_directory': remote_sub_dir,
                'bin_file_copied': False,
                'release_note_copied': False,
                'out_file_copied': False,
                'files': []
            }
            
            # 复制bin文件
            bin_filename = os.path.basename(bin_file_path)
            remote_bin_path = os.path.join(remote_sub_dir, bin_filename)
            
            if self.copy_file(bin_file_path, remote_bin_path):
                result_info['bin_file_copied'] = True
                result_info['files'].append({
                    'type': 'bin',
                    'local_path': bin_file_path,
                    'remote_path': remote_bin_path,
                    'filename': bin_filename
                })
                logger.info(f"bin文件已复制到远程目录: {remote_bin_path}")
            else:
                logger.warning(f"复制bin文件失败: {bin_file_path}")
            
            # 复制Release Notes文件
            if release_note_path and os.path.exists(release_note_path):
                release_note_filename = os.path.basename(release_note_path)
                remote_release_note_path = os.path.join(remote_sub_dir, release_note_filename)
                
                if self.copy_file(release_note_path, remote_release_note_path):
                    result_info['release_note_copied'] = True
                    result_info['files'].append({
                        'type': 'release_note',
                        'local_path': release_note_path,
                        'remote_path': remote_release_note_path,
                        'filename': release_note_filename
                    })
                    logger.info(f"Release Notes已复制到远程目录: {remote_release_note_path}")
                else:
                    logger.warning(f"复制Release Notes失败: {release_note_path}")
            else:
                logger.warning(f"Release Notes文件不存在: {release_note_path}")
            
            # 复制.axf文件（如果需要）
            if publish_out_file:
                axf_file_path = None
                if self.path_manager:
                    axf_file_path = self.path_manager.find_axf_file(configuration=configuration)
                if axf_file_path and os.path.exists(axf_file_path):
                    # 生成与bin文件对应的axf文件名
                    bin_filename = os.path.basename(bin_file_path)
                    axf_filename = bin_filename.replace('.bin', '.axf')
                    remote_axf_path = os.path.join(remote_sub_dir, axf_filename)
                    
                    if self.copy_file(axf_file_path, remote_axf_path):
                        result_info['out_file_copied'] = True
                        result_info['files'].append({
                            'type': 'axf',
                            'local_path': axf_file_path,
                            'remote_path': remote_axf_path,
                            'filename': axf_filename
                        })
                        logger.info(f".axf文件已复制到远程目录: {remote_axf_path}")
                    else:
                        logger.warning(f"复制.axf文件失败: {axf_file_path}")
                else:
                    logger.warning(f"未找到对应的.axf文件，源bin文件: {bin_file_path}")
            
            success_msg = f"远程发布成功\n"
            success_msg += f"远程目录: {remote_sub_dir}\n"
            success_msg += f"bin文件: {'已复制' if result_info['bin_file_copied'] else '复制失败'}\n"
            success_msg += f"Release Notes: {'已复制' if result_info['release_note_copied'] else '复制失败'}\n"
            if publish_out_file:
                success_msg += f".axf文件: {'已复制' if result_info['out_file_copied'] else '复制失败'}\n"
            success_msg += f"文件数量: {len(result_info['files'])}"
            
            return True, success_msg, result_info
            
        except Exception as e:
            logger.error(f"远程发布失败: {e}")
            return False, f"远程发布失败: {e}", result_info
    
    def process_bin_file(self, source_bin_path: str, commit_id: str, 
                        timestamp: Optional[datetime] = None, version: str = None, 
                        configuration: Dict = None) -> Tuple[bool, str, dict]:
        """
        处理bin文件：重命名并移动到输出目录
        
        Args:
            source_bin_path: 源bin文件路径
            commit_id: commit ID
            timestamp: 时间戳
            version: 版本号
            configuration: 配置信息
            
        Returns:
            Tuple[bool, str, dict]: (是否成功, 消息, 文件信息)
        """
        result_info = {
            'source_path': source_bin_path,
            'commit_id': commit_id,
            'timestamp': timestamp or datetime.now(),
            'version': version,
            'new_filename': None,
            'destination_path': None,
            'file_size': 0,
            'operation': 'unknown'
        }
        
        try:
            # 检查源文件是否存在
            if not os.path.exists(source_bin_path):
                return False, f"源文件不存在: {source_bin_path}", result_info
            
            result_info['file_size'] = os.path.getsize(source_bin_path)
            
            # 生成新文件名
            config_name = configuration.get('name', '') if configuration else ''
            new_filename = self.generate_filename(version or "V1.0.0", commit_id, config_name, timestamp, True)
            result_info['new_filename'] = new_filename
            
            # 直接返回成功，不复制到输出目录
            result_info['operation'] = 'processed'
            success_msg = f"文件处理成功\n"
            success_msg += f"源文件: {source_bin_path}\n"
            success_msg += f"文件大小: {result_info['file_size']} 字节\n"
            success_msg += f"Commit ID: {commit_id}\n"
            if version:
                success_msg += f"版本号: {version}\n"
            success_msg += f"时间戳: {result_info['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}"
            
            return True, success_msg, result_info
                
        except Exception as e:
            logger.error(f"处理bin文件失败: {e}")
            return False, f"处理bin文件失败: {e}", result_info


def test_mdk_file_manager():
    """测试MDK文件管理器功能"""
    config = {
        'fw_publish_directory': './fw_publish',
        'remote_publish_directory': './remote_publish'
    }
    
    manager = MDKFileManager(config, project_path="E:/TestProject")
    
    print("MDK文件管理器测试")
    print(f"项目名称: {manager.project_name}")
    print(f"固件发布目录: {manager.fw_publish_directory}")
    print(f"远程发布目录: {manager.remote_publish_directory}")
    
    # 测试文件名生成
    filename = manager.generate_filename("V1.0.0", "abc1234", "Debug", datetime.now(), True)
    print(f"生成的文件名: {filename}")


if __name__ == "__main__":
    
    test_mdk_file_manager()
