#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MDK项目分析器模块
负责解析MDK项目文件(.uvprojx)和SCT文件，自动提取flash偏移地址
"""

import os
import re
from typing import Optional, Dict, Tuple, List
from pathlib import Path
from lib_logger import logger, set_log_level

try:
    from lxml import etree as ET
    HAS_LXML = True
except ImportError:
    import xml.etree.ElementTree as ET
    HAS_LXML = False


class MDKProjectAnalyzer:
    """MDK项目分析器"""
    
    def __init__(self):
        """初始化MDK项目分析器"""
        pass
    
    def analyze_uvprojx_file(self, uvprojx_path: str) -> Optional[Dict]:
        """
        分析MDK项目文件(.uvprojx)，提取SCT文件路径和配置信息
        
        Args:
            uvprojx_path: MDK项目文件路径
            
        Returns:
            Dict: 包含SCT文件路径、配置信息和项目信息的字典
        """
        try:
            if not os.path.exists(uvprojx_path):
                logger.error(f"MDK项目文件不存在: {uvprojx_path}")
                return None
            
            # 解析XML文件
            tree = ET.parse(uvprojx_path)
            root = tree.getroot()
            
            result = {
                'project_path': uvprojx_path,
                'configurations': [],
                'project_name': os.path.splitext(os.path.basename(uvprojx_path))[0],
                'project_dir': os.path.dirname(uvprojx_path)
            }
            
            # 解析配置信息
            configurations = self._parse_configurations(root, result['project_dir'])
            result['configurations'] = configurations
            
            # 为每个配置查找输出文件
            for config in configurations:
                # 记录SCT文件信息
                if config.get('sct_file'):
                    sct_file = config['sct_file']
                    logger.info(f"找到SCT文件: {sct_file} (配置: {config['name']})")
                else:
                    logger.warning(f"配置 {config['name']} 中未找到SCT文件")
                
                # 查找编译输出文件
                build_outputs = self.find_build_outputs(uvprojx_path, config, len(configurations))
                config.update(build_outputs)
            
            return result
            
        except Exception as e:
            logger.error(f"分析MDK项目文件失败: {e}")
            return None
    
    def find_build_outputs(self, project_path: str, configuration: Dict, total_configs: int = 1) -> Dict:
        """
        查找指定配置的编译输出文件(bin和axf)
        
        Args:
            project_path: 项目路径
            configuration: 配置信息
            
        Returns:
            Dict: 包含bin和axf文件路径的字典
        """
        result = {
            'bin_file': None,
            'axf_file': None
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
            # MDK编译输出文件名始终是项目名，不包含配置名
            bin_filename = f"{project_name}.bin"
            axf_filename = f"{project_name}.axf"
            logger.info(f"MDK编译输出文件名: {bin_filename}")
            
            bin_file_path = os.path.join(output_dir, bin_filename)
            axf_file_path = os.path.join(output_dir, axf_filename)
            
            # 直接设置文件路径，不检查文件是否存在
            result['bin_file'] = bin_file_path
            result['axf_file'] = axf_file_path
            result['total_configs'] = total_configs
            
            logger.info(f"配置 {config_name}: 生成文件路径")
            logger.info(f"  bin文件: {bin_file_path}")
            logger.info(f"  axf文件: {axf_file_path}")
            
            return result
            
        except Exception as e:
            logger.error(f"查找编译输出文件失败: {e}")
            return result
    
    def _parse_configurations(self, root, project_dir: str) -> List[Dict]:
        """
        解析MDK项目文件中的配置信息
        
        Args:
            root: XML根节点
            project_dir: 项目目录路径
            
        Returns:
            List[Dict]: 配置信息列表
        """
        configurations = []
        
        try:
            # 步骤1: 查找Targets节点
            # 预期: targets_node 应该是一个Element对象，不是None
            targets_node = root.find('Targets')
            logger.debug(f"targets_node = {targets_node}")
            if targets_node is None:
                logger.warning("未找到Targets节点")
                return configurations
            
            # 步骤2: 查找所有Target节点
            # 预期: targets 应该是一个列表，包含至少1个Target节点
            targets = targets_node.findall('Target')
            logger.debug(f"targets count = {len(targets)}")
            
            for i, target in enumerate(targets):
                logger.debug(f"处理Target {i+1}")
                
                # 步骤3: 查找TargetName节点
                # 预期: config_name_node 应该是一个Element对象，config_name 应该是 "Release" 或类似
                config_name_node = target.find('TargetName')
                config_name = config_name_node.text if config_name_node is not None else ''
                logger.debug(f"config_name_node = {config_name_node}")
                logger.debug(f"config_name = '{config_name}'")
                if not config_name:
                    logger.debug(f"跳过Target {i+1}，因为config_name为空")
                    continue
                
                logger.debug(f"开始解析配置: {config_name}")
                logger.info(f"解析配置: {config_name}")
                
                # 步骤4: 解析输出目录
                # 预期: output_dir 应该是 ".\Obj\" 或完整路径
                try:
                    output_dir = self._parse_output_directory(target, project_dir)
                    logger.info(f"output_dir = '{output_dir}'")
                except Exception as e:
                    logger.error(f"解析输出目录失败: {e}")
                    output_dir = ''
                
                # 步骤5: 解析输出文件名
                # 预期: output_name 应该是 "Test_Project_MDK" 或类似
                try:
                    output_name = self._parse_output_name(target)
                    logger.info(f"output_name = '{output_name}'")
                except Exception as e:
                    logger.error(f"解析输出文件名失败: {e}")
                    output_name = ''
                
                # 步骤6: 解析SCT文件
                # 预期: sct_file 应该是 ".\Test_Project_MDK.sct" 或完整路径
                try:
                    sct_file = self._parse_sct_file(target, project_dir)
                    logger.info(f"sct_file = '{sct_file}'")
                except Exception as e:
                    logger.error(f"解析SCT文件失败: {e}")
                    sct_file = ''
                
                # 步骤7: 解析调试模式
                # 预期: debug_mode 应该是 True 或 False
                debug_mode = self._parse_debug_mode(target)
                logger.debug(f"debug_mode = {debug_mode}")
                
                config = {
                    'name': config_name,
                    'output_dir': output_dir,
                    'output_dir_abs': os.path.abspath(output_dir) if output_dir else '',
                    'output_name': output_name,
                    'sct_file': sct_file,
                    'debug': debug_mode
                }
                
                configurations.append(config)
                logger.info(f"配置 {config_name}: 输出目录={output_dir}, 输出名={output_name}, SCT文件={sct_file}")
            
        except Exception as e:
            logger.error(f"解析配置信息失败: {e}")
        
        return configurations
    
    def _parse_output_directory(self, target, project_dir: str) -> str:
        """
        解析输出目录
        
        Args:
            target: Target节点
            project_dir: 项目目录路径
            
        Returns:
            str: 输出目录路径
        """
        try:
            logger.debug("开始解析输出目录")
            logger.debug(f"project_dir = '{project_dir}'")
            logger.debug(f"target = {target}")
            
            # 在TargetOption/TargetCommonOption中查找OutputDirectory
            target_option = target.find('TargetOption')
            logger.debug(f"target_option = {target_option is not None}")
            if target_option is not None:
                # 先检查TargetOption下有哪些子节点
                logger.debug(f"TargetOption子节点: {[child.tag for child in target_option]}")
                
                # 在TargetCommonOption中查找OutputDirectory
                target_common_option = target_option.find('TargetCommonOption')
                logger.debug(f"target_common_option = {target_common_option is not None}")
                if target_common_option is not None:
                    # 检查TargetCommonOption下有哪些子节点
                    logger.debug(f"TargetCommonOption子节点: {[child.tag for child in target_common_option]}")
                    
                    # 检查每个子节点的内容
                    for child in target_common_option:
                        logger.debug(f"TargetCommonOption子节点 {child.tag}: {child.text}")
                    
                    output_dir_node = target_common_option.find('OutputDirectory')
                    logger.debug(f"output_dir_node = {output_dir_node}")
                    if output_dir_node is not None:
                        output_dir = output_dir_node.text or ''
                        logger.debug(f"output_dir原始值 = '{output_dir}'")
                        if output_dir:
                            # 处理相对路径
                            if not os.path.isabs(output_dir):
                                # 去掉开头的 .\ 或 ./
                                if output_dir.startswith('.\\') or output_dir.startswith('./'):
                                    output_dir = output_dir[2:]
                                output_dir = os.path.join(project_dir, output_dir)
                            logger.debug(f"output_dir最终值 = '{output_dir}'")
                            return output_dir
                        else:
                            logger.debug("output_dir为空字符串")
                    else:
                        logger.debug("未找到OutputDirectory节点")
                else:
                    logger.debug("未找到TargetCommonOption节点")
            else:
                logger.debug("未找到TargetOption节点")
        except Exception as e:
            logger.debug(f"解析输出目录异常: {e}")
            logger.error(f"解析输出目录失败: {e}")
            import traceback
            logger.debug(f"异常堆栈: {traceback.format_exc()}")
        
        logger.debug("输出目录解析失败，返回空字符串")
        return ''
    
    def _parse_output_name(self, target) -> str:
        """
        解析输出文件名
        
        Args:
            target: Target节点
            
        Returns:
            str: 输出文件名
        """
        try:
            logger.debug("开始解析输出文件名")
            # 在TargetOption/TargetCommonOption中查找OutputName
            target_option = target.find('TargetOption')
            logger.debug(f"target_option = {target_option is not None}")
            if target_option is not None:
                target_common_option = target_option.find('TargetCommonOption')
                logger.debug(f"target_common_option = {target_common_option is not None}")
                if target_common_option is not None:
                    # 检查TargetCommonOption下有哪些子节点
                    logger.debug(f"TargetCommonOption子节点: {[child.tag for child in target_common_option]}")
                    
                    # 检查每个子节点的内容
                    for child in target_common_option:
                        logger.debug(f"TargetCommonOption子节点 {child.tag}: {child.text}")
                    
                    output_name_node = target_common_option.find('OutputName')
                    logger.debug(f"output_name_node = {output_name_node}")
                    if output_name_node is not None:
                        output_name = output_name_node.text or ''
                        logger.debug(f"output_name = '{output_name}'")
                        return output_name
                    else:
                        logger.debug("未找到OutputName节点")
                else:
                    logger.debug("未找到TargetCommonOption节点")
            else:
                logger.debug("未找到TargetOption节点")
        except Exception as e:
            logger.debug(f"解析输出文件名异常: {e}")
            logger.error(f"解析输出文件名失败: {e}")
        
        logger.debug("输出文件名解析失败，返回空字符串")
        return ''
    
    def _parse_sct_file(self, target, project_dir: str) -> str:
        """
        解析SCT文件路径
        
        Args:
            target: Target节点
            project_dir: 项目目录路径
            
        Returns:
            str: SCT文件路径
        """
        try:
            logger.debug("开始解析SCT文件")
            # 在TargetOption/TargetArmAds/LDads中查找ScatterFile
            target_option = target.find('TargetOption')
            logger.debug(f"target_option = {target_option is not None}")
            if target_option is not None:
                target_arm_ads = target_option.find('TargetArmAds')
                logger.debug(f"target_arm_ads = {target_arm_ads is not None}")
                if target_arm_ads is not None:
                    # 检查TargetArmAds下有哪些子节点
                    logger.debug(f"TargetArmAds子节点: {[child.tag for child in target_arm_ads]}")
                    
                    # 在LDads中查找ScatterFile
                    ldads = target_arm_ads.find('LDads')
                    logger.debug(f"ldads = {ldads is not None}")
                    if ldads is not None:
                        # 检查LDads下有哪些子节点
                        logger.debug(f"LDads子节点: {[child.tag for child in ldads]}")
                        
                        sct_file_node = ldads.find('ScatterFile')
                        logger.debug(f"sct_file_node = {sct_file_node}")
                        if sct_file_node is not None:
                            sct_file = sct_file_node.text or ''
                            logger.debug(f"sct_file原始值 = '{sct_file}'")
                            if sct_file:
                                # 处理相对路径
                                if not os.path.isabs(sct_file):
                                    # 去掉开头的 .\ 或 ./
                                    if sct_file.startswith('.\\') or sct_file.startswith('./'):
                                        sct_file = sct_file[2:]
                                    sct_file = os.path.join(project_dir, sct_file)
                                logger.debug(f"sct_file最终值 = '{sct_file}'")
                                return sct_file
                            else:
                                logger.debug("sct_file为空字符串")
                        else:
                            logger.debug("未找到ScatterFile节点")
                    else:
                        logger.debug("未找到LDads节点")
                else:
                    logger.debug("未找到TargetArmAds节点")
            else:
                logger.debug("未找到TargetOption节点")
        except Exception as e:
            logger.debug(f"解析SCT文件异常: {e}")
            logger.error(f"解析SCT文件路径失败: {e}")
        
        logger.debug("SCT文件解析失败，返回空字符串")
        return ''
    
    def _parse_debug_mode(self, target) -> bool:
        """
        解析调试模式
        
        Args:
            target: Target节点
            
        Returns:
            bool: 是否为调试模式
        """
        try:
            logger.debug("开始解析调试模式")
            # 在TargetOption/TargetCommonOption中查找DebugInformation
            target_option = target.find('TargetOption')
            logger.debug(f"target_option = {target_option is not None}")
            if target_option is not None:
                target_common_option = target_option.find('TargetCommonOption')
                logger.debug(f"target_common_option = {target_common_option is not None}")
                if target_common_option is not None:
                    debug_info_node = target_common_option.find('DebugInformation')
                    logger.debug(f"debug_info_node = {debug_info_node}")
                    if debug_info_node is not None:
                        debug_info = debug_info_node.text or ''
                        logger.debug(f"debug_info = '{debug_info}'")
                        is_debug = debug_info.lower() in ['1', 'true', 'yes']
                        logger.debug(f"is_debug = {is_debug}")
                        return is_debug
                    else:
                        logger.debug("未找到DebugInformation节点")
                else:
                    logger.debug("未找到TargetCommonOption节点")
            else:
                logger.debug("未找到TargetOption节点")
        except Exception as e:
            logger.debug(f"解析调试模式异常: {e}")
            logger.error(f"解析调试模式失败: {e}")
        
        logger.debug("调试模式解析失败，返回False")
        return False
    
    def analyze_sct_file(self, sct_file_path: str) -> Optional[Dict]:
        """
        分析SCT文件，提取配置信息
        
        Args:
            sct_file_path: SCT文件路径
            
        Returns:
            Optional[Dict]: 配置信息字典，包含Flash起始地址等信息
        """
        try:
            if not os.path.exists(sct_file_path):
                logger.error(f"SCT文件不存在: {sct_file_path}")
                return None
            
            with open(sct_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            config_info = {
                'sct_file_path': sct_file_path,
                'flash_start_address': None,
                'flash_size': None,
                'ram_start_address': None,
                'ram_size': None
            }
            
            # 查找Flash起始地址和大小
            # MDK SCT文件格式: LR_IROM1 0x08000400 0x00040000
            flash_pattern = r'LR_IROM1\s+(0x[0-9a-fA-F]+)\s+(0x[0-9a-fA-F]+)'
            flash_match = re.search(flash_pattern, content, re.IGNORECASE)
            
            if flash_match:
                flash_start = int(flash_match.group(1), 16)
                flash_size = int(flash_match.group(2), 16)
                config_info['flash_start_address'] = flash_start
                config_info['flash_size'] = flash_size
                logger.info(f"从SCT文件提取Flash信息: 起始地址=0x{flash_start:08X}, 大小=0x{flash_size:08X}")
            
            # 查找RAM起始地址和大小
            # MDK SCT文件格式: LR_IRAM1 0x20000000 0x00020000
            ram_pattern = r'LR_IRAM1\s+(0x[0-9a-fA-F]+)\s+(0x[0-9a-fA-F]+)'
            ram_match = re.search(ram_pattern, content, re.IGNORECASE)
            
            if ram_match:
                ram_start = int(ram_match.group(1), 16)
                ram_size = int(ram_match.group(2), 16)
                config_info['ram_start_address'] = ram_start
                config_info['ram_size'] = ram_size
                logger.info(f"从SCT文件提取RAM信息: 起始地址=0x{ram_start:08X}, 大小=0x{ram_size:08X}")
            
            if config_info['flash_start_address'] is None:
                logger.warning(f"在SCT文件中未找到Flash起始地址: {sct_file_path}")
                return None
            
            return config_info
                
        except Exception as e:
            logger.error(f"分析SCT文件失败: {e}")
            return None
    
    def extract_flash_start_address_from_sct(self, sct_file_path: str) -> Optional[int]:
        """
        从SCT文件中提取Flash起始地址（保持向后兼容）
        
        Args:
            sct_file_path: SCT文件路径
            
        Returns:
            Optional[int]: Flash起始地址，如果提取失败返回None
        """
        config_info = self.analyze_sct_file(sct_file_path)
        return config_info.get('flash_start_address') if config_info else None
    
    def get_flash_offset_from_configuration(self, configuration: Dict) -> Optional[int]:
        """
        从配置字典中获取Flash起始地址
        
        Args:
            configuration: 配置字典
            
        Returns:
            Optional[int]: Flash起始地址，如果获取失败返回None
        """
        try:
            # 从配置中获取SCT文件路径
            sct_file = configuration.get('sct_file')
            if not sct_file:
                logger.warning("配置中未找到SCT文件路径")
                return None
            
            # 检查SCT文件是否存在
            if not os.path.exists(sct_file):
                logger.error(f"SCT文件不存在: {sct_file}")
                return None
            
            # 分析SCT文件获取Flash起始地址
            config_info = self.analyze_sct_file(sct_file)
            if config_info:
                flash_start = config_info.get('flash_start_address')
                if flash_start:
                    logger.info(f"从配置中获取Flash起始地址: 0x{flash_start:08X}")
                    return flash_start
            
            logger.warning("无法从配置中获取Flash起始地址")
            return None
            
        except Exception as e:
            logger.error(f"从配置中获取Flash起始地址失败: {e}")
            return None
    
    def get_project_info(self, uvprojx_path: str) -> Optional[Dict]:
        """
        获取MDK项目的基本信息
        
        Args:
            uvprojx_path: MDK项目文件路径
            
        Returns:
            Dict: 项目信息字典
        """
        try:
            result = self.analyze_uvprojx_file(uvprojx_path)
            if not result:
                return None
            
            # 提取项目基本信息
            project_info = {
                'project_name': result['project_name'],
                'project_path': result['project_path'],
                'project_dir': result['project_dir'],
                'configurations': []
            }
            
            # 为每个配置添加Flash起始地址信息
            for config in result['configurations']:
                config_info = {
                    'name': config['name'],
                    'output_dir': config['output_dir_abs'],
                    'output_name': config['output_name'],
                    'sct_file': config['sct_file'],
                    'debug': config['debug'],
                    'bin_file': config.get('bin_file', ''),
                    'axf_file': config.get('axf_file', ''),
                    'flash_start_address': None
                }
                
                # 提取Flash起始地址
                if config['sct_file']:
                    flash_start = self.extract_flash_start_address_from_sct(config['sct_file'])
                    config_info['flash_start_address'] = flash_start
                
                project_info['configurations'].append(config_info)
            
            return project_info
            
        except Exception as e:
            logger.error(f"获取MDK项目信息失败: {e}")
            return None


def main():
    """测试函数"""
    # 设置日志级别为DEBUG，显示详细调试信息
    set_log_level('DEBUG')
    
    logger.info("=" * 60)
    logger.info("MDK项目分析器测试")
    logger.info("=" * 60)
    
    # 测试MDK项目分析器
    analyzer = MDKProjectAnalyzer()
    
    # 测试项目文件路径
    test_project = r"E:\MCU_Program\Test_Project_MDK\MDK-ARM\Test_Project_MDK.uvprojx"
    
    logger.info(f"检查项目文件: {test_project}")
    logger.info(f"文件是否存在: {os.path.exists(test_project)}")
    
    if os.path.exists(test_project):
        logger.info(f"\n开始分析MDK项目文件: {test_project}")
        result = analyzer.get_project_info(test_project)
        
        if result:
            logger.info(f"\n✅ 分析成功!")
            logger.info(f"项目名称: {result['project_name']}")
            logger.info(f"项目路径: {result['project_path']}")
            logger.info(f"项目目录: {result['project_dir']}")
            logger.info(f"配置数量: {len(result['configurations'])}")
            
            for i, config in enumerate(result['configurations'], 1):
                logger.info(f"\n--- 配置 {i}: {config['name']} ---")
                logger.info(f"  输出目录: {config['output_dir']}")
                logger.info(f"  输出名称: {config['output_name']}")
                logger.info(f"  SCT文件: {config['sct_file']}")
                logger.info(f"  调试模式: {config['debug']}")
                logger.info(f"  BIN文件: {config['bin_file']}")
                logger.info(f"  AXF文件: {config['axf_file']}")
                if config['flash_start_address']:
                    logger.info(f"  Flash起始地址: 0x{config['flash_start_address']:08X}")
                else:
                    logger.info(f"  Flash起始地址: 未找到")
        else:
            logger.error("❌ 分析失败")
    else:
        logger.error(f"❌ 测试项目文件不存在: {test_project}")
        logger.error("请检查文件路径是否正确")
    
    logger.info("\n" + "=" * 60)


if __name__ == "__main__":
    main()
