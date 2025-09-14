#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IAR信息管理模块
负责IAR项目的信息文件更新和配置分析
包含版本信息更新和二进制配置参数分析功能
"""

import os
import re
from lib_logger import logger
from typing import Tuple, Optional, Dict


class IARInfoManager:
    """IAR信息管理器"""
    
    def __init__(self, config: dict):
        """
        初始化IAR信息管理器
        
        Args:
            config: 配置字典
        """
        self.config = config
        
        # 版本号模式（每一位固定一位十进制数）
        self.version_pattern = r'V(\d)\.(\d)\.(\d)\.(\d)'
        
        # 从配置中获取版本变量名，默认为__Firmware_Version
        self.version_var_name = config.get('firmware_version_keyword', '__Firmware_Version')
    
    # ==================== 版本信息管理 ====================
    
    def extract_version_from_info_file(self, info_file_path: str) -> Optional[str]:
        """
        从信息文件中提取固件版本
        
        Args:
            info_file_path: 信息文件路径
            
        Returns:
            str: 版本字符串，失败时返回None
        """
        try:
            if not os.path.exists(info_file_path):
                logger.error(f"信息文件不存在: {info_file_path}")
                return None
            
            with open(info_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找版本变量定义（支持空格和注释）
            # 先尝试匹配完整的pragma+变量定义模式
            full_pattern = rf'#pragma\s+location\s*=\s*0x[0-9a-fA-F]+\s*\n\s*(?:/\*.*?\*/)?\s*(?://.*?\n)?\s*__root\s+const\s+char\s+{re.escape(self.version_var_name)}\s*\[\s*10\s*\]\s*=\s*"([^"]+)"'
            match = re.search(full_pattern, content, re.MULTILINE | re.DOTALL)
            
            # 如果完整模式匹配失败，尝试简单的变量定义模式
            if not match:
                simple_pattern = rf'__root\s+const\s+char\s+{re.escape(self.version_var_name)}\s*\[\s*10\s*\]\s*=\s*"([^"]+)"'
                match = re.search(simple_pattern, content)
            
            if match:
                version = match.group(1)
                logger.info(f"从信息文件提取到版本: {version}")
                return version
            else:
                logger.warning(f"在信息文件中未找到{self.version_var_name}定义")
                return None
                
        except Exception as e:
            logger.error(f"从信息文件提取版本失败: {e}")
            return None
    
    def update_version_in_info_file(self, info_file_path: str, new_version: str) -> Tuple[bool, str]:
        """
        更新信息文件中的版本号
        
        Args:
            info_file_path: 信息文件路径
            new_version: 新版本号
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            # 输入验证
            if not info_file_path:
                return False, "信息文件路径为空"
            
            if not new_version:
                return False, "新版本号为空"
            
            if not isinstance(info_file_path, str):
                return False, f"信息文件路径类型错误: {type(info_file_path)}"
            
            if not isinstance(new_version, str):
                return False, f"版本号类型错误: {type(new_version)}"
            
            if not os.path.exists(info_file_path):
                return False, f"信息文件不存在: {info_file_path}"
            
            # 验证版本号格式
            if not re.match(self.version_pattern, new_version):
                return False, f"版本号格式不正确: {new_version}，应为 Vx.x.x.x 格式"
            
            # 检查文件是否可写
            if not os.access(info_file_path, os.W_OK):
                return False, f"信息文件不可写: {info_file_path}"
            
            # 读取文件内容
            with open(info_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找并替换版本号（支持空格和注释）
            # 先尝试匹配完整的pragma+变量定义模式
            full_pattern = rf'(#pragma\s+location\s*=\s*0x[0-9a-fA-F]+\s*\n\s*(?:/\*.*?\*/)?\s*(?://.*?\n)?\s*__root\s+const\s+char\s+{re.escape(self.version_var_name)}\s*\[\s*10\s*\]\s*=\s*")[^"]+(")'
            new_content = re.sub(full_pattern, f'\\g<1>{new_version}\\g<2>', content, flags=re.MULTILINE | re.DOTALL)
            
            # 如果完整模式没有匹配，尝试简单的变量定义模式
            if new_content == content:
                simple_pattern = rf'(__root\s+const\s+char\s+{re.escape(self.version_var_name)}\s*\[\s*10\s*\]\s*=\s*")[^"]+(")'
                new_content = re.sub(simple_pattern, f'\\g<1>{new_version}\\g<2>', content)
            
            if new_content == content:
                return False, "未找到版本号定义或版本号未发生变化"
            
            # 直接写入新内容（不创建备份文件）
            with open(info_file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logger.info(f"成功更新信息文件中的版本号: {new_version}")
            return True, f"版本号已更新为: {new_version}"
            
        except Exception as e:
            error_msg = f"更新信息文件版本号失败: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def validate_version_format(self, version: str) -> bool:
        """
        验证版本号格式是否正确
        
        Args:
            version: 版本号字符串
            
        Returns:
            bool: 格式是否正确
        """
        return bool(re.match(self.version_pattern, version))
    
    def get_version_line_info(self, info_file_path: str) -> dict:
        """
        获取信息文件中版本号行的信息
        
        Args:
            info_file_path: 信息文件路径
            
        Returns:
            dict: 版本号行信息
        """
        info = {
            'found': False,
            'line_number': 0,
            'line_content': '',
            'version': None
        }
        
        try:
            if not os.path.exists(info_file_path):
                return info
            
            with open(info_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                if self.version_var_name in line and '=' in line:
                    info['found'] = True
                    info['line_number'] = i
                    info['line_content'] = line.strip()
                    
                    # 提取版本号
                    match = re.search(r'"([^"]+)"', line)
                    if match:
                        info['version'] = match.group(1)
                    break
            
        except Exception as e:
            logger.error(f"获取版本号行信息失败: {e}")
        
        return info
    
    # ==================== 配置分析功能 ====================
    
    def analyze_config_file(self, config_file_path: str, feature_settings: Dict = None) -> Dict[str, int]:
        """
        分析IAR配置文件，提取二进制参数（使用#pragma location定位方式）
        
        Args:
            config_file_path: 配置文件路径
            feature_settings: 功能设置字典，包含关键字配置
            
        Returns:
            Dict[str, int]: 解析出的参数字典
        """
        result = {
            'firmware_version_offset': 0,
            'git_commit_id_offset': 0,
            'file_size_offset': 0,
            'bin_checksum_offset': 0,
            'hash_value_offset': 0
        }
        
        if not feature_settings:
            feature_settings = {}
        
        # 从配置中获取关键字
        git_commit_id_keyword = feature_settings.get('git_commit_id_keyword', '__git_commit_id')
        file_size_keyword = feature_settings.get('file_size_keyword', '__file_size')
        bin_checksum_keyword = feature_settings.get('bin_checksum_keyword', '__bin_checksum')
        hash_value_keyword = feature_settings.get('hash_value_keyword', '__hash_value')
        firmware_version_keyword = feature_settings.get('firmware_version_keyword', '__Firmware_Version')
        
        try:
            if not os.path.exists(config_file_path):
                logger.error(f"配置文件不存在: {config_file_path}")
                return result
            
            with open(config_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找固件版本的地址（使用用户配置的关键字）
            fw_version_pattern = rf'#pragma\s+location\s*=\s*0x([0-9a-fA-F]+)\s*\n\s*__root\s+const\s+char\s+{re.escape(firmware_version_keyword)}[^;]*;'
            fw_version_offset = self._find_pragma_location(content, fw_version_pattern)
            if fw_version_offset is not None:
                result['firmware_version_offset'] = fw_version_offset
                logger.info(f"找到{firmware_version_keyword}地址: 0x{fw_version_offset:08X}")
            
            # 查找Git提交ID的地址（使用用户配置的关键字）
            commit_id_pattern = rf'#pragma\s+location\s*=\s*0x([0-9a-fA-F]+)\s*\n\s*__root\s+const\s+char\s+{re.escape(git_commit_id_keyword)}[^;]*;'
            commit_id_offset = self._find_pragma_location(content, commit_id_pattern)
            if commit_id_offset is not None:
                result['git_commit_id_offset'] = commit_id_offset
                logger.info(f"找到{git_commit_id_keyword}地址: 0x{commit_id_offset:08X}")
            
            # 查找文件大小的地址（使用用户配置的关键字）
            file_size_pattern = rf'#pragma\s+location\s*=\s*0x([0-9a-fA-F]+)\s*\n\s*__root\s+volatile\s+const\s+uint32_t\s+{re.escape(file_size_keyword)}[^;]*;'
            file_size_offset = self._find_pragma_location(content, file_size_pattern)
            if file_size_offset is not None:
                result['file_size_offset'] = file_size_offset
                logger.info(f"找到{file_size_keyword}地址: 0x{file_size_offset:08X}")
            
            # 查找二进制校验和的地址（使用用户配置的关键字）
            checksum_pattern = rf'#pragma\s+location\s*=\s*0x([0-9a-fA-F]+)\s*\n\s*__root\s+volatile\s+const\s+uint32_t\s+{re.escape(bin_checksum_keyword)}[^;]*;'
            checksum_offset = self._find_pragma_location(content, checksum_pattern)
            if checksum_offset is not None:
                result['bin_checksum_offset'] = checksum_offset
                logger.info(f"找到{bin_checksum_keyword}地址: 0x{checksum_offset:08X}")
            
            # 查找哈希校验和的地址（使用用户配置的关键字）
            # 支持uint32_t和uint8_t数组类型
            hash_value_pattern = rf'#pragma\s+location\s*=\s*0x([0-9a-fA-F]+)\s*\n\s*__root\s+volatile\s+const\s+(?:uint32_t|uint8_t)\s+{re.escape(hash_value_keyword)}(?:\[\d+\])?[^;]*;'
            hash_value_offset = self._find_pragma_location(content, hash_value_pattern)
            if hash_value_offset is not None:
                result['hash_value_offset'] = hash_value_offset
                logger.info(f"找到{hash_value_keyword}地址: 0x{hash_value_offset:08X}")
            
            # 检查是否找到了所有必需的地址
            missing_addresses = []
            if result['firmware_version_offset'] == 0:
                missing_addresses.append(firmware_version_keyword)
            if result['git_commit_id_offset'] == 0:
                missing_addresses.append(git_commit_id_keyword)
            if result['file_size_offset'] == 0:
                missing_addresses.append(file_size_keyword)
            if result['bin_checksum_offset'] == 0:
                missing_addresses.append(bin_checksum_keyword)
            # 只有当启用hash_value功能时才检查
            if feature_settings.get('enable_hash_value', True) and result['hash_value_offset'] == 0:
                missing_addresses.append(hash_value_keyword)
            
            if missing_addresses:
                logger.error(f"配置文件中缺少以下地址定义: {', '.join(missing_addresses)}")
                logger.error("请确保配置文件中包含以下格式的定义:")
                
                # 只显示实际缺少的变量
                if firmware_version_keyword in missing_addresses:
                    logger.error("#pragma location=0x08004410")
                    logger.error(f"__root const char {firmware_version_keyword}[10] = \"V1.0.0.0\";")
                if git_commit_id_keyword in missing_addresses:
                    logger.error("#pragma location=0x08004420")
                    logger.error(f"__root const char {git_commit_id_keyword}[7] = \"\";")
                if file_size_keyword in missing_addresses:
                    logger.error("#pragma location=0x08004430")
                    logger.error(f"__root volatile const uint32_t {file_size_keyword} = 0;")
                if bin_checksum_keyword in missing_addresses:
                    logger.error("#pragma location=0x08004434")
                    logger.error(f"__root volatile const uint32_t {bin_checksum_keyword} = 0;")
                if hash_value_keyword in missing_addresses:
                    logger.error("#pragma location=0x08004438")
                    logger.error(f"__root volatile const uint32_t {hash_value_keyword} = 0;")
            else:
                logger.info(f"配置分析完成: {result}")
            
        except Exception as e:
            logger.error(f"分析配置文件失败: {e}")
        
        return result
    
    def _find_pragma_location(self, content: str, pattern: str) -> Optional[int]:
        """
        查找#pragma location定位的地址
        
        Args:
            content: 文件内容
            pattern: 正则表达式模式
            
        Returns:
            Optional[int]: 找到的地址，未找到返回None
        """
        try:
            match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
            if match:
                hex_value = match.group(1)
                return int(hex_value, 16)
        except Exception as e:
            logger.debug(f"查找#pragma location模式失败 {pattern}: {e}")
        
        return None
    
    def validate_config_file(self, config_file_path: str, feature_settings: Dict = None) -> Tuple[bool, str]:
        """
        验证配置文件是否包含所有必需的地址定义
        
        Args:
            config_file_path: 配置文件路径
            feature_settings: 功能设置字典
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        if not os.path.exists(config_file_path):
            return False, f"配置文件不存在: {config_file_path}"
        
        result = self.analyze_config_file(config_file_path, feature_settings)
        
        # 检查必需的字段
        missing_fields = []
        if result.get('firmware_version_offset', 0) == 0:
            missing_fields.append("__Firmware_Version地址")
        if result.get('git_commit_id_offset', 0) == 0:
            missing_fields.append("__git_commit_id地址")
        if result.get('file_size_offset', 0) == 0:
            missing_fields.append("__file_size地址")
        if result.get('bin_checksum_offset', 0) == 0:
            missing_fields.append("__bin_checksum地址")
        if result.get('hash_value_offset', 0) == 0:
            missing_fields.append("__hash_value地址")
        
        if missing_fields:
            return False, f"配置文件中缺少以下必需的定义: {', '.join(missing_fields)}。请检查配置文件是否包含正确的#pragma location定义。"
        
        # 检查地址顺序
        addresses = [
            result.get('firmware_version_offset', 0),
            result.get('git_commit_id_offset', 0),
            result.get('file_size_offset', 0),
            result.get('bin_checksum_offset', 0),
            result.get('hash_value_offset', 0)
        ]
        
        # 过滤掉0值
        valid_addresses = [addr for addr in addresses if addr > 0]
        
        if len(valid_addresses) > 1:
            # 检查地址是否按顺序排列
            sorted_addresses = sorted(valid_addresses)
            if valid_addresses != sorted_addresses:
                return False, "地址定义顺序不正确，请确保地址按从小到大的顺序定义"
        
        return True, "配置文件验证通过"


def test_iar_info_manager():
    """测试IAR信息管理器功能"""
    # 测试配置
    test_config = {
        'firmware_version_keyword': '__Firmware_Version'
    }
    
    manager = IARInfoManager(test_config)
    
    logger.info("IAR信息管理器测试")
    
    # 测试版本号格式验证
    test_versions = ["V0.0.1.0", "V1.2.3.4", "V9.9.9.9", "V10.1.2.3", "V1.23.4.5"]
    for version in test_versions:
        is_valid = manager.validate_version_format(version)
        logger.info(f"版本号 {version}: {'有效' if is_valid else '无效'}")


if __name__ == "__main__":
    
    test_iar_info_manager()
