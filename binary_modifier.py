#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
二进制文件修改模块
负责在bin文件中写入commit ID和CRC值

CRC32多项式信息：
- 标准多项式: X32 + X26 + X23 + X22 + X16 + X12 + X11 + X10 + X8 + X7 + X5 + X4 + X2 + X + 1
- 十六进制表示: 0x04C11DB7 (标准形式) / 0xEDB88320 (反向形式)
- 使用库: zlib.crc32() (使用反向形式 0xEDB88320)
- 标准: IEEE 802.3 (以太网标准)
"""

import os
import struct
import hashlib
import zlib
from lib_logger import logger
from typing import Tuple, Optional
from pathlib import Path


class BinaryModifier:
    """二进制文件修改器"""
    
    def __init__(self, config: dict, feature_settings: dict = None):
        """
        初始化二进制文件修改器
        
        Args:
            config: 配置字典，包含二进制文件相关设置
            feature_settings: 功能设置字典，控制哪些功能启用
        """
        self.config = config
        self.feature_settings = feature_settings or {}
        
        # 从配置中获取偏移量和大小
        self.firmware_version_offset = config.get('firmware_version_offset', 0)
        self.git_commit_id_offset = config.get('git_commit_id_offset', 0)
        self.file_size_offset = config.get('file_size_offset', 0)
        self.bin_checksum_offset = config.get('bin_checksum_offset', 0)
        self.hash_value_offset = config.get('hash_value_offset', 0)
        
        # 调试信息
        logger.info(f"BinaryModifier配置 - firmware_version_offset: 0x{self.firmware_version_offset:X}")
        logger.info(f"BinaryModifier配置 - git_commit_id_offset: 0x{self.git_commit_id_offset:X}")
        logger.info(f"BinaryModifier配置 - file_size_offset: 0x{self.file_size_offset:X}")
        logger.info(f"BinaryModifier配置 - bin_checksum_offset: 0x{self.bin_checksum_offset:X}")
        logger.info(f"BinaryModifier配置 - hash_value_offset: 0x{self.hash_value_offset:X}")
        self.commit_id_size = config.get('commit_id_size', 7)
        self.crc_size = config.get('crc_size', 4)
        self.reserved_area_size = config.get('reserved_area_size', 0x200)
        # 从binary_settings中获取bin_start_address，如果没有则从根级别获取
        binary_settings = config.get('binary_settings', {})
        self.bin_start_address = binary_settings.get('bin_start_address', 0) or config.get('bin_start_address', 0)
        logger.info(f"BinaryModifier初始化 - bin_start_address: 0x{self.bin_start_address:08X} ({self.bin_start_address})")
        
        # 获取功能启用状态
        self.enable_git_commit_id = self.feature_settings.get('enable_git_commit_id', True)
        self.enable_file_size = self.feature_settings.get('enable_file_size', True)
        self.enable_bin_checksum = self.feature_settings.get('enable_bin_checksum', True)
        self.enable_hash_value = self.feature_settings.get('enable_hash_value', True)
        
        logger.info(f"功能启用状态 - Git提交ID: {self.enable_git_commit_id}, 文件大小: {self.enable_file_size}, 校验和: {self.enable_bin_checksum}")
        
        # 验证配置是否有效（只验证启用的功能）
        if self.firmware_version_offset == 0:
            raise ValueError("firmware_version_offset未配置，请检查配置文件")
        if self.bin_start_address == 0:
            raise ValueError("bin_start_address未配置，请在设置中配置bin起始地址")
        
        # 只验证启用的功能
        if self.enable_git_commit_id and self.git_commit_id_offset == 0:
            raise ValueError("git_commit_id_offset未配置，请检查配置文件或禁用Git提交ID功能")
        if self.enable_file_size and self.file_size_offset == 0:
            raise ValueError("file_size_offset未配置，请检查配置文件或禁用文件大小功能")
        if self.enable_bin_checksum and self.bin_checksum_offset == 0:
            raise ValueError("bin_checksum_offset未配置，请检查配置文件或禁用校验和功能")
        if self.enable_hash_value and self.hash_value_offset == 0:
            raise ValueError("hash_value_offset未配置，请检查配置文件或禁用哈希校验和功能")
        
        # 计算实际偏移量（配置中的偏移量是绝对地址，需要减去bin起始地址）
        self.actual_firmware_version_offset = self.firmware_version_offset - self.bin_start_address
        logger.info(f"固件版本偏移量: 0x{self.firmware_version_offset:X} -> 相对偏移: 0x{self.actual_firmware_version_offset:X}")
        
        if self.enable_git_commit_id:
            self.actual_git_commit_id_offset = self.git_commit_id_offset - self.bin_start_address
            logger.info(f"Git提交ID偏移量: 0x{self.git_commit_id_offset:X} -> 相对偏移: 0x{self.actual_git_commit_id_offset:X}")
        else:
            self.actual_git_commit_id_offset = 0
            
        if self.enable_file_size:
            self.actual_file_size_offset = self.file_size_offset - self.bin_start_address
            logger.info(f"文件大小偏移量: 0x{self.file_size_offset:X} -> 相对偏移: 0x{self.actual_file_size_offset:X}")
        else:
            self.actual_file_size_offset = 0
            
        if self.enable_bin_checksum:
            self.actual_bin_checksum_offset = self.bin_checksum_offset - self.bin_start_address
            logger.info(f"校验和偏移量: 0x{self.bin_checksum_offset:X} -> 相对偏移: 0x{self.actual_bin_checksum_offset:X}")
        else:
            self.actual_bin_checksum_offset = 0
            
        if self.enable_hash_value:
            self.actual_hash_value_offset = self.hash_value_offset - self.bin_start_address
            logger.info(f"哈希校验和偏移量: 0x{self.hash_value_offset:X} -> 相对偏移: 0x{self.actual_hash_value_offset:X}")
        else:
            self.actual_hash_value_offset = 0
    
    def calculate_crc32(self, data: bytes) -> int:
        """
        计算CRC32值
        
        使用IEEE 802.3标准的CRC-32多项式：
        多项式: X32 + X26 + X23 + X22 + X16 + X12 + X11 + X10 + X8 + X7 + X5 + X4 + X2 + X + 1
        十六进制: 0x04C11DB7 (标准形式) / 0xEDB88320 (反向形式，zlib使用)
        
        Args:
            data: 要计算CRC的数据
            
        Returns:
            int: CRC32值
        """
        return zlib.crc32(data) & 0xFFFFFFFF
    
    def calculate_file_crc(self, file_path: str) -> int:
        """
        计算文件的CRC32值，排除CRC值和hash值存储区域
        
        Args:
            file_path: 文件路径
            
        Returns:
            int: 文件的CRC32值
        """
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # 排除CRC值存储区域（4字节）
            crc_start = self.actual_bin_checksum_offset
            crc_end = crc_start + self.crc_size
            
            # 排除hash值存储区域（32字节）- 只有在启用hash功能时才排除
            if self.enable_hash_value:
                hash_start = self.actual_hash_value_offset
                hash_end = hash_start + 32
            else:
                hash_start = 0
                hash_end = 0
            
            # 分段计算CRC
            crc_value = 0
            
            # 第一段：文件开始到CRC值之前
            if crc_start > 0 and crc_start < len(data):
                crc_value = zlib.crc32(data[:crc_start], crc_value) & 0xFFFFFFFF
            
            # 第二段：CRC值之后到hash值之前（如果hash值存在）
            if self.enable_hash_value and crc_end < hash_start and crc_end < len(data):
                crc_value = zlib.crc32(data[crc_end:hash_start], crc_value) & 0xFFFFFFFF
            elif not self.enable_hash_value and crc_end < len(data):
                # 如果hash值不存在，直接从CRC值之后到文件结束
                crc_value = zlib.crc32(data[crc_end:], crc_value) & 0xFFFFFFFF
            
            # 第三段：hash值之后到文件结束（只有在hash值存在时才执行）
            if self.enable_hash_value and hash_end < len(data):
                crc_value = zlib.crc32(data[hash_end:], crc_value) & 0xFFFFFFFF
            
            # 记录排除的区域信息
            excluded_regions = f"CRC值区域(0x{crc_start:X}-0x{crc_end:X})"
            if self.enable_hash_value:
                excluded_regions += f"和hash值区域(0x{hash_start:X}-0x{hash_end:X})"
            
            logger.info(f"CRC计算完成，排除了{excluded_regions}")
            return crc_value
            
        except Exception as e:
            logger.error(f"计算文件CRC失败: {e}")
            return 0
    
    def commit_id_to_bytes(self, commit_id: str) -> bytes:
        """
        将commit ID转换为字节数组（直接写入ASCII字符串）
        
        Args:
            commit_id: commit ID字符串（7位十六进制）
            
        Returns:
            bytes: commit ID的ASCII字节表示
        """
        try:
            # 输入验证
            if not commit_id:
                logger.error("commit ID为空")
                return b'\x00' * self.commit_id_size
            
            if not isinstance(commit_id, str):
                logger.error(f"commit ID类型错误: {type(commit_id)}")
                return b'\x00' * self.commit_id_size
            
            # 确保commit ID是有效的十六进制字符串
            if not all(c in '0123456789abcdefABCDEF' for c in commit_id):
                logger.error(f"无效的commit ID格式: {commit_id}")
                return b'\x00' * self.commit_id_size
            
            # 转换为小写
            commit_id = commit_id.lower()
            
            # 如果长度不足7位，用0填充
            if len(commit_id) < 7:
                commit_id = commit_id.ljust(7, '0')
            elif len(commit_id) > 7:
                commit_id = commit_id[:7]
            
            # 直接转换为ASCII字节（字符串形式）
            commit_bytes = commit_id.encode('ascii')
            
            # 确保长度正确
            if len(commit_bytes) < self.commit_id_size:
                commit_bytes += b'\x00' * (self.commit_id_size - len(commit_bytes))
            elif len(commit_bytes) > self.commit_id_size:
                commit_bytes = commit_bytes[:self.commit_id_size]
            
            logger.info(f"Commit ID转换: {commit_id} -> {commit_bytes.decode('ascii', errors='ignore')}")
            return commit_bytes
            
        except Exception as e:
            logger.error(f"转换commit ID失败: {e}")
            return b'\x00' * self.commit_id_size
    
    def _create_backup(self, file_path: str) -> str:
        """
        创建原始文件的备份
        
        Args:
            file_path: 原始文件路径
            
        Returns:
            str: 备份文件路径，失败返回None
        """
        try:
            import shutil
            
            # 生成备份文件名（直接添加_backup）
            file_dir = os.path.dirname(file_path)
            file_name = os.path.basename(file_path)
            name, ext = os.path.splitext(file_name)
            
            backup_name = f"{name}_backup{ext}"
            backup_path = os.path.join(file_dir, backup_name)
            
            # 复制文件
            shutil.copy2(file_path, backup_path)
            
            return backup_path
            
        except Exception as e:
            logger.error(f"创建备份文件失败: {e}")
            return None
    
    def write_commit_id(self, file_path: str, commit_id: str) -> bool:
        """
        在bin文件中写入commit ID
        
        Args:
            file_path: bin文件路径
            commit_id: commit ID
            
        Returns:
            bool: 写入是否成功
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return False
            
            # 检查偏移量是否超出文件大小
            file_size = os.path.getsize(file_path)
            logger.info(f"文件大小: {file_size} 字节")
            logger.info(f"Commit ID偏移量: 0x{self.actual_git_commit_id_offset:X} ({self.actual_git_commit_id_offset})")
            logger.info(f"Commit ID大小: {self.commit_id_size} 字节")
            logger.info(f"写入位置: 0x{self.actual_git_commit_id_offset:X}，大小: {self.commit_id_size} 字节")
            
            if self.actual_git_commit_id_offset + self.commit_id_size > file_size:
                logger.error(f"bin文件太小，无法写入commit ID")
                logger.error(f"当前文件大小: {file_size} 字节")
                logger.error(f"需要大小: {self.actual_git_commit_id_offset + self.commit_id_size} 字节")
                logger.error(f"请检查bin文件是否正确生成，或调整commit_id_offset配置")
                return False
            
            # 转换commit ID为字节
            commit_bytes = self.commit_id_to_bytes(commit_id)
            
            # 写入文件
            with open(file_path, 'r+b') as f:
                f.seek(self.actual_git_commit_id_offset)
                f.write(commit_bytes)
            
            logger.info(f"成功写入commit ID: {commit_id} 到偏移量 0x{self.actual_git_commit_id_offset:X}")
            return True
            
        except Exception as e:
            logger.error(f"写入commit ID失败: {e}")
            return False
    
    def write_crc(self, file_path: str, crc_value: int) -> bool:
        """
        在bin文件中写入CRC值
        
        Args:
            file_path: bin文件路径
            crc_value: CRC值
            
        Returns:
            bool: 写入是否成功
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return False
            
            # 检查偏移量是否超出文件大小
            file_size = os.path.getsize(file_path)
            if self.actual_bin_checksum_offset + self.crc_size > file_size:
                logger.error(f"CRC偏移量超出文件大小: {self.actual_bin_checksum_offset + self.crc_size} > {file_size}")
                return False
            
            # 将CRC值转换为字节（小端序）
            crc_bytes = struct.pack('<I', crc_value)
            
            # 写入文件
            with open(file_path, 'r+b') as f:
                f.seek(self.actual_bin_checksum_offset)
                f.write(crc_bytes)
            
            logger.info(f"成功写入CRC: 0x{crc_value:08X} 到偏移量 0x{self.actual_bin_checksum_offset:X}")
            return True
            
        except Exception as e:
            logger.error(f"写入CRC失败: {e}")
            return False
    
    def write_hash_value(self, file_path: str, hash_value: int) -> bool:
        """
        写入哈希校验和值到二进制文件
        
        Args:
            file_path: 二进制文件路径
            hash_value: 哈希校验和值（magic数）
            
        Returns:
            bool: 是否成功
        """
        try:
            file_size = os.path.getsize(file_path)
            # 由于__hash_value是32字节数组，需要写入32字节
            hash_size = 32
            if self.actual_hash_value_offset + hash_size > file_size:
                logger.error(f"哈希校验和偏移量超出文件大小: {self.actual_hash_value_offset + hash_size} > {file_size}")
                return False
            
            with open(file_path, 'r+b') as f:
                f.seek(self.actual_hash_value_offset)
                # 将magic数转换为32字节的字节数组
                # 前4字节是magic数，其余28字节填充0
                hash_bytes = struct.pack('<I', hash_value) + b'\x00' * 28
                f.write(hash_bytes)
            
            logger.info(f"成功写入哈希校验和值: 0x{hash_value:08X} 到偏移量 0x{self.actual_hash_value_offset:X} (32字节)")
            return True
        except Exception as e:
            logger.error(f"写入哈希校验和值失败: {e}")
            return False
    
    def read_commit_id(self, file_path: str) -> Optional[str]:
        """
        从bin文件中读取commit ID
        
        Args:
            file_path: bin文件路径
            
        Returns:
            str: commit ID，失败时返回None
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return None
            
            file_size = os.path.getsize(file_path)
            if self.actual_git_commit_id_offset + self.commit_id_size > file_size:
                logger.error(f"commit ID偏移量超出文件大小")
                return None
            
            with open(file_path, 'rb') as f:
                f.seek(self.actual_git_commit_id_offset)
                commit_bytes = f.read(self.commit_id_size)
            
            # 转换为十六进制字符串
            commit_id = commit_bytes.hex().upper()
            logger.info(f"读取到commit ID: {commit_id}")
            return commit_id
            
        except Exception as e:
            logger.error(f"读取commit ID失败: {e}")
            return None
    
    def read_crc(self, file_path: str) -> Optional[int]:
        """
        从bin文件中读取CRC值
        
        Args:
            file_path: bin文件路径
            
        Returns:
            int: CRC值，失败时返回None
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return None
            
            file_size = os.path.getsize(file_path)
            if self.actual_bin_checksum_offset + self.crc_size > file_size:
                logger.error(f"CRC偏移量超出文件大小")
                return None
            
            with open(file_path, 'rb') as f:
                f.seek(self.actual_bin_checksum_offset)
                crc_bytes = f.read(self.crc_size)
            
            # 解析CRC值（小端序）
            crc_value = struct.unpack('<I', crc_bytes)[0]
            logger.info(f"读取到CRC: 0x{crc_value:08X}")
            return crc_value
            
        except Exception as e:
            logger.error(f"读取CRC失败: {e}")
            return None
    
    def modify_binary_file(self, file_path: str, commit_id: str, firmware_version: str = None) -> Tuple[bool, str, dict]:
        """
        修改二进制文件，写入固件信息
        
        Args:
            file_path: bin文件路径
            commit_id: commit ID
            firmware_version: 固件版本（可选）
            
        Returns:
            Tuple[bool, str, dict]: (是否成功, 消息, 文件信息)
        """
        result_info = {
            'file_path': file_path,
            'commit_id': commit_id,
            'firmware_version': firmware_version,
            'commit_id_written': False,
            'firmware_version_written': False,
            'file_size_written': False,
            'crc_calculated': 0,
            'crc_written': False,
            'file_size': 0
        }
        
        try:
            # 检查文件
            if not os.path.exists(file_path):
                return False, f"文件不存在: {file_path}", result_info
            
            result_info['file_size'] = os.path.getsize(file_path)
            
            # 创建原始文件的备份
            backup_path = self._create_backup(file_path)
            if backup_path:
                result_info['backup_path'] = backup_path
                logger.info(f"已创建备份文件: {backup_path}")
            else:
                logger.warning("创建备份文件失败，继续执行修改")
            
            # 跳过固件版本写入（编译时已正确设置）
            if firmware_version:
                logger.info(f"跳过固件版本写入（编译时已正确设置）: {firmware_version}")
                result_info['firmware_version_written'] = False  # 标记为未写入
            
            # 写入commit ID（如果启用）
            if self.enable_git_commit_id:
                if not self.write_commit_id(file_path, commit_id):
                    return False, "写入commit ID失败", result_info
                result_info['commit_id_written'] = True
                logger.info("Git提交ID写入成功")
            else:
                logger.info("Git提交ID功能已禁用，跳过写入")
                result_info['commit_id_written'] = False
            
            # 写入文件大小（如果启用）
            if self.enable_file_size:
                if not self.write_file_size(file_path, result_info['file_size']):
                    return False, "写入文件大小失败", result_info
                result_info['file_size_written'] = True
                logger.info("文件大小写入成功")
            else:
                logger.info("文件大小功能已禁用，跳过写入")
                result_info['file_size_written'] = False
            
            # 计算并写入CRC（如果启用）
            if self.enable_bin_checksum:
                crc_value = self.calculate_file_crc(file_path)
                result_info['crc_calculated'] = crc_value
                
                if not self.write_crc(file_path, crc_value):
                    return False, "写入CRC失败", result_info
                result_info['crc_written'] = True
                logger.info("CRC校验和写入成功")
            else:
                logger.info("CRC校验和功能已禁用，跳过写入")
                result_info['crc_calculated'] = 0
                result_info['crc_written'] = False
            
            # 写入哈希校验和（如果启用）
            if self.enable_hash_value:
                # 使用magic数作为哈希值，后续可以替换为实际算法
                magic_hash_value = 0x12345678
                result_info['hash_value'] = magic_hash_value
                
                if not self.write_hash_value(file_path, magic_hash_value):
                    return False, "写入哈希校验和失败", result_info
                result_info['hash_value_written'] = True
                logger.info("哈希校验和写入成功")
            else:
                logger.info("哈希校验和功能已禁用，跳过写入")
                result_info['hash_value'] = 0
                result_info['hash_value_written'] = False
            
            # 验证写入结果（只验证启用的功能）
            success_msg = f"二进制文件修改成功\n"
            success_msg += f"文件: {file_path}\n"
            success_msg += f"大小: {result_info['file_size']} 字节\n"
            
            if self.enable_git_commit_id:
                read_commit_id = self.read_commit_id(file_path)
                success_msg += f"Commit ID: {commit_id} -> {read_commit_id}\n"
            
            if self.enable_bin_checksum:
                read_crc = self.read_crc(file_path)
                success_msg += f"CRC: 0x{result_info['crc_calculated']:08X} -> 0x{read_crc:08X}"
            
            return True, success_msg, result_info
            
        except Exception as e:
            error_msg = f"修改二进制文件失败: {e}"
            logger.error(error_msg)
            return False, error_msg, result_info
    
    def write_firmware_version(self, file_path: str, version: str) -> bool:
        """
        写入固件版本
        
        Args:
            file_path: bin文件路径
            version: 固件版本字符串
            
        Returns:
            bool: 是否成功
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return False
            
            # 检查偏移量是否超出文件大小
            file_size = os.path.getsize(file_path)
            if self.actual_firmware_version_offset + 16 > file_size:  # 假设版本字符串最大16字节
                logger.error(f"固件版本偏移量超出文件大小")
                return False
            
            # 将版本字符串转换为字节
            version_bytes = version.encode('utf-8')[:16]  # 限制长度
            version_bytes = version_bytes.ljust(16, b'\x00')  # 填充到16字节
            
            # 写入文件
            with open(file_path, 'r+b') as f:
                f.seek(self.actual_firmware_version_offset)
                f.write(version_bytes)
            
            logger.info(f"成功写入固件版本: {version} 到偏移量 0x{self.actual_firmware_version_offset:X}")
            return True
            
        except Exception as e:
            logger.error(f"写入固件版本失败: {e}")
            return False
    
    def write_file_size(self, file_path: str, size: int) -> bool:
        """
        写入文件大小
        
        Args:
            file_path: bin文件路径
            size: 文件大小
            
        Returns:
            bool: 是否成功
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return False
            
            # 检查偏移量是否超出文件大小
            file_size = os.path.getsize(file_path)
            if self.actual_file_size_offset + 4 > file_size:
                logger.error(f"文件大小偏移量超出文件大小")
                return False
            
            # 将文件大小转换为字节（小端序）
            size_bytes = struct.pack('<I', size)
            
            # 写入文件
            with open(file_path, 'r+b') as f:
                f.seek(self.actual_file_size_offset)
                f.write(size_bytes)
            
            logger.info(f"成功写入文件大小: {size} 到偏移量 0x{self.actual_file_size_offset:X}")
            return True
            
        except Exception as e:
            logger.error(f"写入文件大小失败: {e}")
            return False
    
    def get_file_info(self, file_path: str) -> dict:
        """
        获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            dict: 文件信息
        """
        info = {
            'exists': False,
            'path': file_path,
            'size': 0,
            'commit_id': None,
            'crc': None,
            'commit_id_offset': self.actual_git_commit_id_offset,
            'crc_offset': self.actual_bin_checksum_offset
        }
        
        try:
            if os.path.exists(file_path):
                info['exists'] = True
                info['size'] = os.path.getsize(file_path)
                info['commit_id'] = self.read_commit_id(file_path)
                info['crc'] = self.read_crc(file_path)
        except Exception as e:
            logger.error(f"获取文件信息失败: {e}")
        
        return info


def test_binary_modifier():
    """测试二进制文件修改器功能"""
    # 测试配置
    test_config = {
        'commit_id_offset': 0x1000,
        'commit_id_size': 8,
        'crc_offset': 0x1008,
        'crc_size': 4,
        'reserved_area_size': 0x200
    }
    
    modifier = BinaryModifier(test_config)
    
    print("二进制文件修改器测试")
    print(f"Commit ID偏移量: 0x{modifier.commit_id_offset:X}")
    print(f"Commit ID大小: {modifier.commit_id_size} 字节")
    print(f"CRC偏移量: 0x{modifier.crc_offset:X}")
    print(f"CRC大小: {modifier.crc_size} 字节")
    
    # 测试commit ID转换
    test_commit_id = "a1b2c3d4e5f6"
    commit_bytes = modifier.commit_id_to_bytes(test_commit_id)
    print(f"Commit ID转换测试: {test_commit_id} -> {commit_bytes.hex()}")


if __name__ == "__main__":
    
    test_binary_modifier()
