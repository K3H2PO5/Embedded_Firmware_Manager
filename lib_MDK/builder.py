#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MDK编译模块
负责调用MDK编译系统生成bin文件
"""

import subprocess
import os
import time
from typing import Tuple, Optional, Dict
from pathlib import Path
from lib_logger import logger
from .project_analyzer import MDKProjectAnalyzer


class MDKBuilder:
    """MDK编译管理类"""
    
    def __init__(self, config: dict, configuration: Dict = None):
        """
        初始化MDK编译器
        
        Args:
            config: 配置字典，包含MDK相关设置
            configuration: 当前选择的配置信息
        """
        self.config = config
        self.configuration = configuration
        
        # 从配置中获取路径
        mdk_installation_path = config.get('mdk_installation_path', '')
        logger.info(f"配置中的MDK安装路径: {mdk_installation_path}")
        self.mdk_exe_path = self._find_mdk_executable(mdk_installation_path)
        logger.info(f"最终MDK可执行文件路径: {self.mdk_exe_path}")
        
        # 从project_settings中获取MDK相关路径，如果没有则从根级别获取
        project_settings = config.get('project_settings', {})
        self.workspace_path = project_settings.get('mdk_workspace_path', '') or config.get('mdk_workspace_path', '')
        self.mdk_project_path = project_settings.get('mdk_project_path', '') or config.get('mdk_project_path', '')
        self.output_bin_path = project_settings.get('output_bin_path', '') or config.get('output_bin_path', '')
        
        # 项目根目录从config中获取，这是用户设置的项目根目录
        self.project_root = config.get('project_path', '')
        # 实际的项目文件路径
        self.project_path = self.mdk_project_path
        self.build_config = config.get('build_configuration', 'Debug')
        self.clean_before_build = config.get('clean_before_build', False)  # 默认使用增量编译
        self.timeout_seconds = config.get('timeout_seconds', 300)
        
        # 验证路径
        logger.info(f"MDK可执行文件: {self.mdk_exe_path}")
        logger.info(f"MDK工作区文件: {self.workspace_path}")
        logger.info(f"MDK项目文件: {self.project_path}")
        logger.info(f"输出bin文件: {self.output_bin_path}")
        self._validate_paths()
        self._check_permissions()
        self.diagnose_environment()
        self.test_mdk_command()
    
    def _find_mdk_executable(self, mdk_dir: str) -> str:
        """
        在MDK安装目录中查找UV4.exe
        
        Args:
            mdk_dir: MDK安装目录
            
        Returns:
            str: UV4.exe的完整路径，未找到返回空字符串
        """
        if not mdk_dir:
            return ""
        
        possible_paths = [
            os.path.join(mdk_dir, "UV4", "UV4.exe"),
            os.path.join(mdk_dir, "UV4.exe"),
            os.path.join(mdk_dir, "bin", "UV4.exe"),
            os.path.join(mdk_dir, "ARM", "UV4", "UV4.exe"),
            os.path.join(mdk_dir, "ARM", "bin", "UV4.exe")
        ]
        
        logger.info(f"搜索MDK可执行文件，尝试以下路径:")
        for i, path in enumerate(possible_paths, 1):
            exists = os.path.exists(path)
            logger.info(f"  {i}. {path} - {'存在' if exists else '不存在'}")
            if exists:
                logger.info(f"找到MDK可执行文件: {path}")
                return path
        
        # 如果没找到，检查是否是直接指定的exe路径
        if mdk_dir.endswith('.exe') and os.path.exists(mdk_dir):
            return mdk_dir
        
        # 如果都没找到，返回空字符串
        logger.warning(f"在MDK目录中未找到UV4.exe: {mdk_dir}")
        return ""
    
    def _validate_paths(self):
        """验证MDK相关路径是否存在"""
        # 检查MDK可执行文件
        if not os.path.exists(self.mdk_exe_path):
            logger.warning(f"MDK可执行文件不存在: {self.mdk_exe_path}")
        
        # 检查工作区文件
        if self.workspace_path and not os.path.exists(self.workspace_path):
            logger.warning(f"MDK工作区文件不存在: {self.workspace_path}")
        
        # 检查项目文件
        if self.project_path and not os.path.exists(self.project_path):
            logger.warning(f"MDK项目文件不存在: {self.project_path}")
    
    def _check_permissions(self):
        """检查权限"""
        try:
            # 检查MDK可执行文件权限
            if os.path.exists(self.mdk_exe_path):
                if not os.access(self.mdk_exe_path, os.X_OK):
                    logger.warning(f"MDK可执行文件没有执行权限: {self.mdk_exe_path}")
            
            # 检查项目目录权限
            if self.project_path and os.path.exists(self.project_path):
                project_dir = os.path.dirname(self.project_path)
                if not os.access(project_dir, os.W_OK):
                    logger.warning(f"项目目录没有写权限: {project_dir}")
            
            # 检查输出目录权限
            if self.output_bin_path and os.path.exists(os.path.dirname(self.output_bin_path)):
                output_dir = os.path.dirname(self.output_bin_path)
                if not os.access(output_dir, os.W_OK):
                    logger.warning(f"输出目录没有写权限: {output_dir}")
                    
        except Exception as e:
            logger.warning(f"权限检查失败: {e}")
    
    def diagnose_environment(self):
        """诊断运行环境，特别针对打包exe的情况"""
        logger.info("=== 环境诊断开始 ===")
        
        # 检查是否在打包环境中运行
        import sys
        if getattr(sys, 'frozen', False):
            logger.info("运行环境: 打包exe")
            logger.info(f"exe路径: {sys.executable}")
        else:
            logger.info("运行环境: Python脚本")
            logger.info(f"Python路径: {sys.executable}")
        
        # 检查当前工作目录
        import os
        current_dir = os.getcwd()
        logger.info(f"当前工作目录: {current_dir}")
        
        # 检查环境变量
        path_env = os.environ.get('PATH', '')
        logger.info(f"PATH环境变量长度: {len(path_env)}")
        
        # 检查MDK相关环境变量
        keil_path = os.environ.get('KEIL_PATH', '')
        if keil_path:
            logger.info(f"KEIL_PATH环境变量: {keil_path}")
        else:
            logger.info("KEIL_PATH环境变量: 未设置")
        
        # 检查MDK可执行文件
        if os.path.exists(self.mdk_exe_path):
            logger.info(f"MDK可执行文件存在: {self.mdk_exe_path}")
            try:
                stat = os.stat(self.mdk_exe_path)
                logger.info(f"文件大小: {stat.st_size} 字节")
                logger.info(f"修改时间: {time.ctime(stat.st_mtime)}")
            except Exception as e:
                logger.warning(f"获取文件信息失败: {e}")
        else:
            logger.warning(f"MDK可执行文件不存在: {self.mdk_exe_path}")
        
        logger.info("=== 环境诊断结束 ===")
    
    def test_mdk_command(self):
        """测试MDK命令是否可用"""
        logger.info("=== 测试MDK命令 ===")
        
        if not os.path.exists(self.mdk_exe_path):
            logger.error(f"MDK可执行文件不存在: {self.mdk_exe_path}")
            return False
        
        # 测试MDK可执行文件是否存在且可执行
        logger.info("=" * 50)
        logger.info("测试MDK可执行文件:")
        logger.info(f"文件路径: {self.mdk_exe_path}")
        logger.info(f"文件存在: {os.path.exists(self.mdk_exe_path)}")
        logger.info(f"文件可执行: {os.access(self.mdk_exe_path, os.X_OK)}")
        logger.info("=" * 50)
        
        # 不执行实际命令，只检查文件
        if os.path.exists(self.mdk_exe_path) and os.access(self.mdk_exe_path, os.X_OK):
            logger.info("MDK可执行文件检查通过")
            return True
        else:
            logger.warning("MDK可执行文件检查失败")
            return False
    
    def build_project(self, force_rebuild: bool = False) -> Tuple[bool, str]:
        """
        编译MDK项目
        
        Args:
            force_rebuild: 是否强制重新编译（清理后编译）
            
        Returns:
            Tuple[bool, str]: (编译是否成功, 输出信息)
        """
        configuration = self.build_config
        
        logger.info("=" * 60)
        logger.info("进入 build_project 方法")
        logger.info(f"开始编译MDK项目，配置: {configuration}")
        logger.info(f"项目文件: {self.project_path}")
        logger.info(f"MDK可执行文件: {self.mdk_exe_path}")
        logger.info("=" * 60)
        
        if not os.path.exists(self.mdk_exe_path):
            error_msg = f"MDK可执行文件不存在: {self.mdk_exe_path}"
            logger.error(error_msg)
            return False, "", error_msg
        
        if not os.path.exists(self.project_path):
            error_msg = f"MDK项目文件不存在: {self.project_path}"
            logger.error(error_msg)
            return False, "", error_msg
        
        try:
            # 设置工作目录为项目文件所在目录
            project_dir = os.path.dirname(self.project_path)
            
            # 构建MDK编译命令
            # 完整命令：UV4.exe -b -j0 -t <target> <project_file> -o <logfile>
            cmd = [
                self.mdk_exe_path,
                '-b',  # 编译参数
                '-j0',  # 后台静默编译，使用所有CPU核心
                '-t', configuration,  # 目标配置名称
                self.project_path,  # 项目文件
            ]
            
            # 如果是完整重新编译，先清理再编译
            if self.clean_before_build:
                # 先执行清理
                clean_cmd = [
                    self.mdk_exe_path, 
                    '-c',  # 清理参数
                    '-t', configuration,  # 目标配置名称
                    self.project_path
                ]
                logger.info("=" * 50)
                logger.info("执行清理命令:")
                logger.info(f"命令: {' '.join(clean_cmd)}")
                logger.info(f"工作目录: {project_dir}")
                logger.info("=" * 50)
                
                clean_result = subprocess.run(
                    clean_cmd,
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=project_dir
                )
                logger.info(f"清理完成，返回码: {clean_result.returncode}")
                if clean_result.stdout:
                    logger.info(f"清理标准输出: {clean_result.stdout}")
                if clean_result.stderr:
                    logger.warning(f"清理错误输出: {clean_result.stderr}")
            
            # 添加输出日志文件
            log_file = os.path.join(project_dir, f"build_{configuration}.log")
            cmd.extend(['-o', log_file])
            
            # 记录编译命令信息
            logger.info("=" * 60)
            logger.info("执行编译命令:")
            logger.info(f"完整命令: {' '.join(cmd)}")
            logger.info(f"命令参数:")
            logger.info(f"  - MDK可执行文件: {self.mdk_exe_path}")
            logger.info(f"  - 编译参数: -b -j0")
            logger.info(f"  - 目标配置: -t {configuration}")
            logger.info(f"  - 项目文件: {self.project_path}")
            logger.info(f"  - 输出日志: -o {log_file}")
            logger.info(f"工作目录: {project_dir}")
            logger.info("=" * 60)
            
            
            # 执行编译
            logger.info("开始执行编译...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                cwd=project_dir
            )
            
            # 记录编译结果
            logger.info("=" * 50)
            logger.info("编译结果:")
            logger.info(f"返回码: {result.returncode}")
            logger.info(f"标准输出长度: {len(result.stdout)}")
            logger.info(f"错误输出长度: {len(result.stderr)}")
            
            # 显示编译输出的前500个字符
            if result.stdout:
                logger.info(f"标准输出内容: {result.stdout[:500]}...")
            if result.stderr:
                logger.info(f"错误输出内容: {result.stderr[:500]}...")
            
            logger.info("=" * 50)
            
            if result.returncode == 0:
                logger.info("✅ 编译成功")
                return True, result.stdout
            else:
                logger.error(f"❌ 编译失败，返回码: {result.returncode}")
                return False, f"编译失败: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            error_msg = f"编译超时，超过 {self.timeout_seconds} 秒"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"编译异常: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def clean_project(self) -> bool:
        """
        清理MDK项目
        
        Returns:
            bool: 清理是否成功
        """
        configuration = self.build_config
        
        logger.info(f"开始清理MDK项目，配置: {configuration}")
        
        if not os.path.exists(self.mdk_exe_path):
            error_msg = f"MDK可执行文件不存在: {self.mdk_exe_path}"
            logger.error(error_msg)
            return False, "", error_msg
        
        if not os.path.exists(self.project_path):
            error_msg = f"MDK项目文件不存在: {self.project_path}"
            logger.error(error_msg)
            return False, "", error_msg
        
        try:
            # 设置工作目录为项目文件所在目录
            project_dir = os.path.dirname(self.project_path)
            
            # 构建MDK清理命令
            # 完整命令：UV4.exe -c -t <target> <project_file>
            cmd = [
                self.mdk_exe_path,
                '-c',  # 清理参数
                '-t', configuration,  # 目标配置名称
                self.project_path  # 项目文件
            ]
            
            logger.info("=" * 50)
            logger.info("执行清理命令:")
            logger.info(f"命令: {' '.join(cmd)}")
            logger.info(f"工作目录: {project_dir}")
            logger.info("=" * 50)
            
            # 执行清理
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                cwd=project_dir
            )
            
            # 记录清理结果
            logger.info(f"清理完成，返回码: {result.returncode}")
            
            if result.returncode == 0:
                logger.info("清理成功")
                return True
            else:
                logger.error(f"清理失败，返回码: {result.returncode}")
                logger.error(f"错误输出: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            error_msg = f"清理超时，超过 {self.timeout_seconds} 秒"
            logger.error(error_msg)
            return False
        except Exception as e:
            error_msg = f"清理异常: {str(e)}"
            logger.error(error_msg)
            return False
    
    def get_build_output_path(self, configuration: str = None) -> str:
        """
        获取编译输出文件路径
        
        Args:
            configuration: 编译配置名称，如果为None则使用默认配置
            
        Returns:
            str: 输出文件路径
        """
        if not configuration:
            configuration = self.build_config
        
        # 如果有配置的输出路径，直接使用
        if self.output_bin_path:
            return self.output_bin_path
        
        # 使用MDK项目分析器获取实际的输出路径
        if self.project_path:
            try:
                analyzer = MDKProjectAnalyzer()
                project_info = analyzer.get_project_info(self.project_path)
                
                if project_info and project_info.get('configurations'):
                    # 查找指定配置的输出路径
                    for config in project_info['configurations']:
                        if config.get('name') == configuration:
                            bin_file = config.get('bin_file')
                            if bin_file and os.path.exists(bin_file):
                                logger.info(f"找到配置 {configuration} 的bin文件: {bin_file}")
                                return bin_file
                            else:
                                logger.warning(f"配置 {configuration} 的bin文件不存在: {bin_file}")
                                break
                    
                    # 如果没找到指定配置，使用第一个配置
                    if project_info['configurations']:
                        first_config = project_info['configurations'][0]
                        bin_file = first_config.get('bin_file')
                        if bin_file:
                            logger.info(f"使用第一个配置的bin文件: {bin_file}")
                            return bin_file
                
                logger.warning("无法从项目分析器获取输出路径，使用默认路径")
                
            except Exception as e:
                logger.error(f"获取项目输出路径失败: {e}")
        
        # 如果项目分析器失败，使用默认路径
        if self.project_path:
            project_dir = os.path.dirname(self.project_path)
            project_name = os.path.splitext(os.path.basename(self.project_path))[0]
            output_file = os.path.join(project_dir, f"{project_name}.bin")
            logger.info(f"使用默认输出路径: {output_file}")
            return output_file
        
        return ""
    
    def check_build_output(self, configuration: str = None) -> bool:
        """
        检查编译输出文件是否存在
        
        Args:
            configuration: 编译配置名称，如果为None则使用默认配置
            
        Returns:
            bool: 输出文件是否存在
        """
        output_path = self.get_build_output_path(configuration)
        if not output_path:
            return False
        
        exists = os.path.exists(output_path)
        if exists:
            logger.info(f"找到编译输出文件: {output_path}")
        else:
            logger.warning(f"编译输出文件不存在: {output_path}")
        
        return exists
    
    def get_build_info(self) -> Dict:
        """
        获取编译信息
        
        Returns:
            Dict: 编译信息字典
        """
        return {
            'mdk_exe_path': self.mdk_exe_path,
            'project_path': self.project_path,
            'workspace_path': self.workspace_path,
            'output_bin_path': self.output_bin_path,
            'build_config': self.build_config,
            'clean_before_build': self.clean_before_build,
            'timeout_seconds': self.timeout_seconds,
            'mdk_available': os.path.exists(self.mdk_exe_path),
            'project_available': os.path.exists(self.project_path) if self.project_path else False
        }
    
    def check_bin_file(self) -> bool:
        """
        检查bin文件是否存在
        
        Returns:
            bool: bin文件是否存在
        """
        return self.check_build_output()
    
    def get_bin_file_info(self, configuration: Dict = None) -> dict:
        """
        获取bin文件信息
        
        Args:
            configuration: 配置信息（兼容IAR接口）
            
        Returns:
            dict: bin文件信息
        """
        output_path = self.get_build_output_path()
        exists = os.path.exists(output_path)
        
        return {
            'exists': exists,
            'path': output_path,
            'size': os.path.getsize(output_path) if exists else 0
        }
    
    def build_and_check(self) -> Tuple[bool, str, dict]:
        """
        编译并检查结果
        
        Returns:
            Tuple[bool, str, dict]: (编译是否成功, 输出信息, bin文件信息)
        """
        success, output = self.build_project()
        bin_info = self.get_bin_file_info()
        
        return success, output, bin_info
    
    def smart_build(self, only_version_changed: bool = True) -> Tuple[bool, str]:
        """
        智能编译：根据修改内容决定编译策略
        
        Args:
            only_version_changed: 是否只有版本号发生变化
        
        Returns:
            Tuple[bool, str]: (编译是否成功, 输出信息)
        """
        if only_version_changed:
            logger.info("检测到仅版本号变化，使用增量编译")
            success, output = self.build_project()
            return success, output
        else:
            logger.info("检测到代码变化，使用清理编译")
            # 先清理再编译
            clean_success = self.clean_project()
            if not clean_success:
                return False, "清理失败"
            
            success, output = self.build_project()
            return success, output


def main():
    """测试函数"""
    from lib_logger import set_log_level, logger
    set_log_level('DEBUG')
    
    logger.info("=" * 60)
    logger.info("MDK构建器测试")
    logger.info("=" * 60)
    
    # 配置参数
    config = {
        'mdk_installation_path': r'C:\Users\dravi\AppData\Local\Keil_v5',
        'project_path': r'E:\MCU_Program\Test_Project_MDK',
        'build_configuration': 'Debug',
        'clean_before_build': False,
        'timeout_seconds': 300
    }
    
    logger.info(f"MDK安装路径: {config['mdk_installation_path']}")
    logger.info(f"项目路径: {config['project_path']}")
    
    # 查找项目文件
    project_files = []
    if os.path.exists(config['project_path']):
        for root, dirs, files in os.walk(config['project_path']):
            for file in files:
                if file.endswith('.uvprojx'):
                    project_files.append(os.path.join(root, file))
    
    if not project_files:
        logger.error("未找到MDK项目文件(.uvprojx)")
        return
    
    logger.info(f"找到 {len(project_files)} 个项目文件:")
    for i, project_file in enumerate(project_files, 1):
        logger.info(f"  {i}. {project_file}")
    
    # 使用第一个项目文件进行测试
    test_project = project_files[0]
    config['mdk_project_path'] = test_project
    logger.info(f"使用项目文件: {test_project}")
    
    # 确保项目文件路径正确设置
    if not config.get('mdk_project_path'):
        config['mdk_project_path'] = test_project
    
    try:
        # 创建MDK构建器
        logger.info("创建MDK构建器...")
        builder = MDKBuilder(config)
        
        # 获取构建信息
        build_info = builder.get_build_info()
        logger.info("构建信息:")
        for key, value in build_info.items():
            logger.info(f"  {key}: {value}")
        
        # 测试编译
        logger.info("\n开始测试编译...")
        logger.info("调用 builder.build_project('Debug')...")
        
        
        success, stdout, stderr = builder.build_project('Debug')
        logger.info(f"build_project 返回: success={success}")
        
        if success:
            logger.info("✅ 编译成功!")
            logger.info(f"标准输出: {stdout[:500]}...")
            if stderr:
                logger.info(f"错误输出: {stderr[:500]}...")
        else:
            logger.error("❌ 编译失败!")
            logger.error(f"错误信息: {stderr}")
            logger.error(f"标准输出: {stdout}")
        
        # 检查输出文件
        logger.info("\n检查编译输出文件...")
        output_exists = builder.check_build_output('Debug')
        if output_exists:
            output_path = builder.get_build_output_path('Debug')
            logger.info(f"✅ 找到输出文件: {output_path}")
        else:
            logger.warning("❌ 未找到输出文件")
        
    except Exception as e:
        logger.error(f"测试过程中出现异常: {e}")
        import traceback
        logger.error(f"异常堆栈: {traceback.format_exc()}")
    
    logger.info("\n" + "=" * 60)


if __name__ == "__main__":
    main()
