#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IAR项目分析器模块
负责解析IAR项目文件(.ewp)和ICF文件，自动提取flash偏移地址
"""

import os
import re
from lib_logger import logger
from typing import Optional, Dict, Tuple, List
from pathlib import Path

try:
    from lxml import etree as ET
    HAS_LXML = True
except ImportError:
    import xml.etree.ElementTree as ET
    HAS_LXML = False


class IARProjectAnalyzer:
    """IAR项目分析器"""
    
    def __init__(self):
        """初始化IAR项目分析器"""
    
    def analyze_ewp_file(self, ewp_path: str) -> Optional[Dict]:
        """
        分析IAR项目文件(.ewp)，提取ICF文件路径和配置信息
        
        Args:
            ewp_path: IAR项目文件路径
            
        Returns:
            Dict: 包含ICF文件路径、配置信息和项目信息的字典
        """
        try:
            if not os.path.exists(ewp_path):
                logger.error(f"IAR项目文件不存在: {ewp_path}")
                return None
            
            # 解析XML文件
            tree = ET.parse(ewp_path)
            root = tree.getroot()
            
            result = {
                'project_path': ewp_path,
                'configurations': [],
                'project_name': os.path.splitext(os.path.basename(ewp_path))[0],
                'project_dir': os.path.dirname(ewp_path)
            }
            
            # 解析配置信息
            configurations = self._parse_configurations(root, result['project_dir'])
            result['configurations'] = configurations
            
            # 为每个配置查找输出文件
            for config in configurations:
                # 记录ICF文件信息
                if config.get('icf_file'):
                    icf_file = config['icf_file']
                    logger.info(f"找到ICF文件: {icf_file} (配置: {config['name']})")
                else:
                    logger.warning(f"配置 {config['name']} 中未找到ICF文件")
                
                # 查找编译输出文件
                build_outputs = self.find_build_outputs(ewp_path, config, len(configurations))
                config.update(build_outputs)
            
            return result
            
        except Exception as e:
            logger.error(f"分析IAR项目文件失败: {e}")
            return None
    
    def find_build_outputs(self, project_path: str, configuration: Dict, total_configs: int = 1) -> Dict:
        """
        查找指定配置的编译输出文件(bin和out)
        
        Args:
            project_path: 项目路径
            configuration: 配置信息
            
        Returns:
            Dict: 包含bin和out文件路径的字典
        """
        result = {
            'bin_file': None,
            'out_file': None
        }
        
        try:
            output_dir = configuration.get('output_dir_abs', '')
            config_name = configuration.get('name', '')
            project_name = os.path.splitext(os.path.basename(project_path))[0]
            logger.info(f"原始项目名: {project_name} (从文件: {os.path.basename(project_path)})")
            logger.info(f"当前配置名: {config_name}")
            
            # 如果项目名包含配置名后缀，移除它
            if config_name and project_name.endswith(f"_{config_name}"):
                project_name = project_name[:-len(f"_{config_name}")]
                logger.info(f"移除配置名后缀后的项目名: {project_name}")
            else:
                logger.info(f"项目名不包含配置名后缀，保持原样: {project_name}")
            
            logger.info(f"最终项目名: {project_name}")
            
            if not output_dir or not os.path.exists(output_dir):
                logger.warning(f"配置 {config_name} 的输出目录不存在: {output_dir}")
                return result
            
            # 构建文件名
            logger.info(f"配置总数: {total_configs}")
            # IAR编译输出文件名始终是项目名，不包含配置名
            bin_filename = f"{project_name}.bin"
            out_filename = f"{project_name}.out"
            logger.info(f"IAR编译输出文件名: {bin_filename}")
            
            bin_file_path = os.path.join(output_dir, bin_filename)
            out_file_path = os.path.join(output_dir, out_filename)
            
            # 直接设置文件路径，不检查文件是否存在
            result['bin_file'] = bin_file_path
            result['out_file'] = out_file_path
            result['total_configs'] = total_configs
            
            logger.info(f"配置 {config_name}: 生成文件路径")
            logger.info(f"  bin文件: {bin_file_path}")
            logger.info(f"  out文件: {out_file_path}")
            
            return result
            
        except Exception as e:
            logger.error(f"查找编译输出文件失败: {e}")
            return result
    
    def _parse_configurations(self, root, project_dir: str) -> List[Dict]:
        """
        解析IAR项目文件中的配置信息
        
        Args:
            root: XML根节点
            project_dir: 项目目录路径
            
        Returns:
            List[Dict]: 配置信息列表
        """
        configurations = []
        
        try:
            # 查找所有configuration节点
            for config_elem in root.findall('.//configuration'):
                config_info = {
                    'name': '',
                    'output_dir': '',
                    'output_dir_abs': '',
                    'debug': False,
                    'toolchain': '',
                    'icf_file': ''
                }
                
                # 获取配置名称
                name_elem = config_elem.find('name')
                if name_elem is not None:
                    config_info['name'] = name_elem.text
                
                # 获取debug状态
                debug_elem = config_elem.find('debug')
                if debug_elem is not None:
                    config_info['debug'] = debug_elem.text == '1'
                
                # 获取工具链
                toolchain_elem = config_elem.find('toolchain/name')
                if toolchain_elem is not None:
                    config_info['toolchain'] = toolchain_elem.text
                
                # 查找输出目录
                # 通常在 <option><name>ExePath</name><state>Debug\Exe</state></option>
                for option in config_elem.findall('.//option'):
                    name_elem = option.find('name')
                    if name_elem is not None and name_elem.text == 'ExePath':
                        state_elem = option.find('state')
                        if state_elem is not None:
                            config_info['output_dir'] = state_elem.text
                            # 构建绝对路径
                            if os.path.isabs(state_elem.text):
                                config_info['output_dir_abs'] = state_elem.text
                            else:
                                config_info['output_dir_abs'] = os.path.join(project_dir, state_elem.text)
                
                # 查找ICF文件配置
                for option in config_elem.findall('.//option'):
                    name_elem = option.find('name')
                    if name_elem is not None and name_elem.text == 'IlinkIcfFile':
                        state_elem = option.find('state')
                        if state_elem is not None:
                            icf_file = state_elem.text
                            # 处理$PROJ_DIR$宏
                            if icf_file.startswith('$PROJ_DIR$'):
                                icf_file = icf_file.replace('$PROJ_DIR$', project_dir)
                            elif not os.path.isabs(icf_file):
                                icf_file = os.path.join(project_dir, icf_file)
                            config_info['icf_file'] = icf_file
                
                if config_info['name']:  # 只添加有效的配置
                    configurations.append(config_info)
                    logger.info(f"找到配置: {config_info['name']}, 输出目录: {config_info['output_dir_abs']}, Debug: {config_info['debug']}")
            
            return configurations
            
        except Exception as e:
            logger.error(f"解析配置信息失败: {e}")
            return []
    
    def analyze_icf_file(self, icf_path: str) -> Optional[Dict]:
        """
        分析ICF文件，提取flash偏移地址
        
        Args:
            icf_path: ICF文件路径
            
        Returns:
            Dict: 包含flash偏移地址的字典
        """
        try:
            if not os.path.exists(icf_path):
                logger.error(f"ICF文件不存在: {icf_path}")
                return None
            
            with open(icf_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            result = {
                'icf_path': icf_path,
                'flash_start': None,
                'flash_size': None,
                'ram_start': None,
                'ram_size': None,
                'intvec_start': None
            }
            
            # 查找__ICFEDIT_intvec_start__定义
            intvec_pattern = r'__ICFEDIT_intvec_start__\s*=\s*0x([0-9a-fA-F]+)'
            match = re.search(intvec_pattern, content)
            if match:
                intvec_start = int(match.group(1), 16)
                result['intvec_start'] = intvec_start
                logger.info(f"找到__ICFEDIT_intvec_start__: 0x{intvec_start:X}")
            
            # 查找flash区域定义
            # 格式通常为: define memory with size = 0x100000;
            # 或者: define region FLASH = [from 0x08000000 to 0x080FFFFF];
            flash_patterns = [
                r'define\s+region\s+FLASH\s*=\s*\[\s*from\s+0x([0-9a-fA-F]+)\s+to\s+0x([0-9a-fA-F]+)\s*\]',
                r'define\s+memory\s+with\s+size\s*=\s*0x([0-9a-fA-F]+)',
                r'define\s+region\s+ROM\s*=\s*\[\s*from\s+0x([0-9a-fA-F]+)\s+to\s+0x([0-9a-fA-F]+)\s*\]'
            ]
            
            for pattern in flash_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    if len(match.groups()) == 2:  # from ... to ... 格式
                        flash_start = int(match.group(1), 16)
                        flash_end = int(match.group(2), 16)
                        result['flash_start'] = flash_start
                        result['flash_size'] = flash_end - flash_start + 1
                        logger.info(f"找到Flash区域: 0x{flash_start:X} - 0x{flash_end:X} (大小: 0x{result['flash_size']:X})")
                    else:  # size 格式
                        flash_size = int(match.group(1), 16)
                        # 尝试从intvec_start推断flash_start
                        if result['intvec_start']:
                            result['flash_start'] = result['intvec_start']
                            result['flash_size'] = flash_size
                            logger.info(f"找到Flash大小: 0x{flash_size:X}, 起始地址: 0x{result['flash_start']:X}")
                    break
            
            # 查找RAM区域定义
            ram_patterns = [
                r'define\s+region\s+RAM\s*=\s*\[\s*from\s+0x([0-9a-fA-F]+)\s+to\s+0x([0-9a-fA-F]+)\s*\]',
                r'define\s+region\s+IRAM\s*=\s*\[\s*from\s+0x([0-9a-fA-F]+)\s+to\s+0x([0-9a-fA-F]+)\s*\]'
            ]
            
            for pattern in ram_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    ram_start = int(match.group(1), 16)
                    ram_end = int(match.group(2), 16)
                    result['ram_start'] = ram_start
                    result['ram_size'] = ram_end - ram_start + 1
                    logger.info(f"找到RAM区域: 0x{ram_start:X} - 0x{ram_end:X} (大小: 0x{result['ram_size']:X})")
                    break
            
            # 验证结果
            if not result['intvec_start'] and not result['flash_start']:
                logger.warning("未找到flash起始地址信息")
                return None
            
            return result
            
        except Exception as e:
            logger.error(f"分析ICF文件失败: {e}")
            return None
    
    def get_flash_offset_from_configuration(self, configuration: Dict) -> Optional[int]:
        """
        从配置信息中获取flash偏移地址
        
        Args:
            configuration: 配置信息
            
        Returns:
            int: flash偏移地址，失败返回None
        """
        try:
            if not configuration.get('icf_file'):
                logger.error("配置中未找到ICF文件路径")
                return None
            
            icf_file = configuration['icf_file']
            if not os.path.exists(icf_file):
                logger.error(f"ICF文件不存在: {icf_file}")
                return None
            
            logger.info(f"分析ICF文件: {icf_file}")
            icf_result = self.analyze_icf_file(icf_file)
            if icf_result and icf_result.get('intvec_start'):
                logger.info(f"从ICF文件获取flash偏移地址: 0x{icf_result['intvec_start']:X}")
                return icf_result['intvec_start']
            else:
                logger.error("ICF文件中未找到flash偏移地址")
                return None
            
        except Exception as e:
            logger.error(f"分析ICF文件失败: {e}")
            return None
    
    def find_ewp_file(self, project_path: str) -> Optional[str]:
        """
        在项目路径中查找IAR项目文件
        
        Args:
            project_path: 项目根目录
            
        Returns:
            str: 找到的.ewp文件路径，未找到返回None
        """
        try:
            # 搜索路径
            search_paths = [
                project_path,
                os.path.join(project_path, 'EWARM'),
                os.path.join(project_path, '..', 'EWARM'),
                os.path.join(project_path, '..', '..', 'EWARM')
            ]
            
            for search_path in search_paths:
                if not os.path.exists(search_path):
                    continue
                
                # 递归搜索.ewp文件
                for root, dirs, files in os.walk(search_path):
                    for file in files:
                        if file.lower().endswith('.ewp'):
                            ewp_path = os.path.join(root, file)
                            logger.info(f"找到IAR项目文件: {ewp_path}")
                            return ewp_path
            
            logger.warning("未找到IAR项目文件")
            return None
            
        except Exception as e:
            logger.error(f"查找IAR项目文件失败: {e}")
            return None


def test_iar_project_analyzer():
    """测试IAR项目分析器功能"""
    analyzer = IARProjectAnalyzer()
    
    logger.info("IAR项目分析器测试")
    
    # 测试查找项目文件
    ewp_file = analyzer.find_ewp_file(".")
    logger.info(f"找到项目文件: {ewp_file}")
    
    if ewp_file:
        # 测试分析项目文件
        project_info = analyzer.analyze_ewp_file(ewp_file)
        logger.info(f"项目信息: {project_info}")
        
        # 测试获取flash偏移地址
        if project_info and project_info.get('configurations'):
            config = project_info['configurations'][0]  # 使用第一个配置
            flash_offset = analyzer.get_flash_offset_from_configuration(config)
            logger.info(f"Flash偏移地址: 0x{flash_offset:X}" if flash_offset else "未找到")
        else:
            logger.info("未找到配置信息")


if __name__ == "__main__":
    test_iar_project_analyzer()
