#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IAR编译模块
负责调用IAR编译系统生成bin文件
"""

import subprocess
import os
from lib_logger import logger
import time
from typing import Tuple, Optional, Dict
from pathlib import Path


class IARBuilder:
    """IAR编译管理类"""
    
    def __init__(self, config: dict, configuration: Dict = None):
        """
        初始化IAR编译器
        
        Args:
            config: 配置字典，包含IAR相关设置
            configuration: 当前选择的配置信息
        """
        self.config = config
        self.configuration = configuration
        
        # 从配置中获取路径
        iar_installation_path = config.get('iar_installation_path', '')
        logger.info(f"配置中的IAR安装路径: {iar_installation_path}")
        self.iar_exe_path = self._find_iar_executable(iar_installation_path)
        logger.info(f"最终IAR可执行文件路径: {self.iar_exe_path}")
        
        # 从project_settings中获取IAR相关路径，如果没有则从根级别获取
        project_settings = config.get('project_settings', {})
        self.workspace_path = project_settings.get('iar_workspace_path', '') or config.get('iar_workspace_path', '')
        self.iar_project_path = project_settings.get('iar_project_path', '') or config.get('iar_project_path', '')
        self.output_bin_path = project_settings.get('output_bin_path', '') or config.get('output_bin_path', '')
        
        # 项目根目录从config中获取，这是用户设置的项目根目录
        self.project_path = config.get('project_path', '')
        self.build_config = config.get('build_configuration', 'Debug')
        self.clean_before_build = config.get('clean_before_build', False)  # 默认使用增量编译
        self.timeout_seconds = config.get('timeout_seconds', 300)
        
        # 验证路径
        logger.info(f"IAR可执行文件: {self.iar_exe_path}")
        logger.info(f"IAR工作区文件: {self.workspace_path}")
        logger.info(f"IAR项目文件: {self.project_path}")
        logger.info(f"输出bin文件: {self.output_bin_path}")
        self._validate_paths()
        self._check_permissions()
        self.diagnose_environment()
        self.test_iar_command()
    
    def _find_iar_executable(self, iar_dir: str) -> str:
        """
        在IAR安装目录中查找IarBuild.exe
        
        Args:
            iar_dir: IAR安装目录
            
        Returns:
            str: IarBuild.exe的完整路径，未找到返回默认路径
        """
        if not iar_dir:
            return 'C:/Program Files (x86)/IAR Systems/Embedded Workbench 8.3/common/bin/IarBuild.exe'
        
        possible_paths = [
            os.path.join(iar_dir, "common", "bin", "IarBuild.exe"),
            os.path.join(iar_dir, "bin", "IarBuild.exe"),
            os.path.join(iar_dir, "IarBuild.exe"),
            os.path.join(iar_dir, "arm", "bin", "IarBuild.exe"),
            os.path.join(iar_dir, "EWARM", "bin", "IarBuild.exe")
        ]
        
        logger.info(f"搜索IAR可执行文件，尝试以下路径:")
        for i, path in enumerate(possible_paths, 1):
            exists = os.path.exists(path)
            logger.info(f"  {i}. {path} - {'存在' if exists else '不存在'}")
            if exists:
                logger.info(f"找到IAR可执行文件: {path}")
                return path
        
        # 如果没找到，检查是否是直接指定的exe路径
        if iar_dir.endswith('.exe') and os.path.exists(iar_dir):
            return iar_dir
        
        # 如果都没找到，返回默认路径
        default_path = 'C:/Program Files (x86)/IAR Systems/Embedded Workbench 8.3/common/bin/IarBuild.exe'
        logger.warning(f"在IAR目录中未找到IarBuild.exe: {iar_dir}")
        logger.warning(f"使用默认路径: {default_path}")
        return default_path
    
    def _validate_paths(self):
        """验证IAR相关路径是否存在"""
        # 检查IAR可执行文件
        if not os.path.exists(self.iar_exe_path):
            logger.warning(f"IAR可执行文件不存在: {self.iar_exe_path}")
        
        # 检查工作区文件
        if self.workspace_path and not os.path.exists(self.workspace_path):
            logger.warning(f"IAR工作区文件不存在: {self.workspace_path}")
        
        # 检查项目文件
        if self.project_path and not os.path.exists(self.project_path):
            logger.warning(f"IAR项目文件不存在: {self.project_path}")
    
    def _check_permissions(self):
        """检查权限"""
        try:
            # 检查IAR可执行文件权限
            if os.path.exists(self.iar_exe_path):
                if not os.access(self.iar_exe_path, os.X_OK):
                    logger.warning(f"IAR可执行文件没有执行权限: {self.iar_exe_path}")
            
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
        logger.info(f"当前工作目录: {os.getcwd()}")
        
        # 检查环境变量
        logger.info(f"PATH环境变量: {os.environ.get('PATH', '')[:200]}...")
        
        # 检查IAR相关路径
        logger.info(f"IAR可执行文件路径: {self.iar_exe_path}")
        logger.info(f"IAR可执行文件存在: {os.path.exists(self.iar_exe_path)}")
        if os.path.exists(self.iar_exe_path):
            stat = os.stat(self.iar_exe_path)
            logger.info(f"IAR可执行文件大小: {stat.st_size} 字节")
            logger.info(f"IAR可执行文件权限: {oct(stat.st_mode)}")
        
        logger.info(f"项目文件路径: {self.project_path}")
        logger.info(f"项目文件存在: {os.path.exists(self.project_path)}")
        
        # 检查项目目录权限
        if self.project_path and os.path.exists(self.project_path):
            project_dir = os.path.dirname(self.project_path)
            logger.info(f"项目目录: {project_dir}")
            logger.info(f"项目目录存在: {os.path.exists(project_dir)}")
            logger.info(f"项目目录可写: {os.access(project_dir, os.W_OK)}")
            logger.info(f"项目目录可读: {os.access(project_dir, os.R_OK)}")
            logger.info(f"项目目录可执行: {os.access(project_dir, os.X_OK)}")
        
        logger.info("=== 环境诊断结束 ===")
    
    def test_iar_command(self) -> bool:
        """测试IAR命令是否能正常执行"""
        try:
            logger.info("测试IAR命令执行...")
            # 简单的测试命令
            test_cmd = [self.iar_exe_path, "-?"]
            
            # 尝试不同的调用方式
            for use_shell in [False, True]:
                try:
                    logger.info(f"尝试执行IAR测试命令 (shell={use_shell})...")
                    if use_shell:
                        # 对于shell模式，需要特殊处理包含空格的路径
                        cmd_str = ' '.join(f'"{arg}"' for arg in test_cmd)
                        result = subprocess.run(
                            cmd_str,
                            capture_output=True,
                            text=True,
                            timeout=10,
                            shell=True
                        )
                    else:
                        result = subprocess.run(
                            test_cmd,
                            capture_output=True,
                            text=True,
                            timeout=10,
                            shell=False
                        )
                    
                    logger.info(f"IAR测试命令返回码: {result.returncode}")
                    logger.info(f"stdout: {result.stdout[:200]}...")
                    logger.info(f"stderr: {result.stderr[:200]}...")
                    
                    if result.returncode == 0 or "IAR" in result.stderr or "IAR" in result.stdout:
                        logger.info(f"IAR命令测试成功 (shell={use_shell})")
                        return True
                    else:
                        logger.warning(f"IAR命令测试失败 (shell={use_shell}): {result.stderr}")
                        
                except Exception as e:
                    logger.warning(f"IAR命令测试异常 (shell={use_shell}): {e}")
                    continue
            
            logger.error("所有IAR命令测试方式都失败")
            return False
            
        except Exception as e:
            logger.error(f"IAR命令测试异常: {e}")
            return False
    
    def clean_project(self) -> bool:
        """
        清理项目
        
        Returns:
            bool: 清理是否成功
        """
        try:
            logger.info("开始清理项目...")
            
            # 构建清理命令
            cmd = [
                self.iar_exe_path,
                self.iar_project_path,
                '-clean',
                self.build_config
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0,
                shell=False,  # 明确设置为False，避免shell权限问题
                cwd=os.path.dirname(self.project_path) if self.project_path else None  # 设置工作目录
            )
            
            if result.returncode == 0:
                logger.info("项目清理成功")
                return True
            else:
                logger.error(f"项目清理失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("项目清理超时")
            return False
        except Exception as e:
            logger.error(f"项目清理异常: {e}")
            return False
    
    def build_project(self, force_rebuild: bool = False) -> Tuple[bool, str]:
        """
        编译项目
        
        Args:
            force_rebuild: 是否强制重新编译（清理后编译）
        
        Returns:
            Tuple[bool, str]: (编译是否成功, 输出信息)
        """
        try:
            logger.info(f"开始编译项目: {self.iar_project_path}")
            logger.info(f"编译配置: {self.build_config}")
            
            # 决定是否清理项目
            should_clean = self.clean_before_build or force_rebuild
            if should_clean:
                logger.info("执行清理编译（rebuild all）")
                if not self.clean_project():
                    return False, "项目清理失败"
                # 使用build命令进行全量编译
                cmd = [
                    self.iar_exe_path,
                    self.iar_project_path,
                    '-build',
                    self.build_config
                ]
            else:
                logger.info("执行增量编译（make）")
                # 使用make命令进行增量编译
                cmd = [
                    self.iar_exe_path,
                    self.iar_project_path,
                    self.build_config  # 不指定-build参数，默认为make操作
                ]
            
            logger.info(f"执行命令: {' '.join(cmd)}")
            
            # 调试信息
            logger.info(f"IAR可执行文件路径: {self.iar_exe_path}")
            logger.info(f"项目文件路径: {self.iar_project_path}")
            logger.info(f"工作目录: {os.path.dirname(self.iar_project_path) if self.iar_project_path else None}")
            
            # 检查文件是否存在
            if not os.path.exists(self.iar_exe_path):
                return False, f"IAR可执行文件不存在: {self.iar_exe_path}"
            if not os.path.exists(self.iar_project_path):
                return False, f"项目文件不存在: {self.iar_project_path}"
            
            # 执行编译
            start_time = time.time()
            result = None
            
            # 尝试不同的调用方式
            for attempt, (use_shell, use_creationflags) in enumerate([
                (False, subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0),
                (False, 0),  # 不使用CREATE_NO_WINDOW
                (True, 0)    # 使用shell模式
            ]):
                try:
                    logger.info(f"编译尝试 {attempt + 1}/3: shell={use_shell}, creationflags={use_creationflags}")
                    
                    if use_shell:
                        # 对于shell模式，需要特殊处理包含空格的路径
                        cmd_str = ' '.join(f'"{arg}"' for arg in cmd)
                        logger.info(f"执行shell命令: {cmd_str}")
                        result = subprocess.run(
                            cmd_str,
                            capture_output=True,
                            text=True,
                            timeout=self.timeout_seconds,
                            shell=True,
                            cwd=os.path.dirname(self.project_path) if self.project_path else None
                        )
                    else:
                        logger.info(f"执行命令: {' '.join(cmd)}")
                        result = subprocess.run(
                            cmd,
                            capture_output=True,
                            text=True,
                            timeout=self.timeout_seconds,
                            creationflags=use_creationflags,
                            shell=False,
                            cwd=os.path.dirname(self.project_path) if self.project_path else None
                        )
                    
                    # 如果成功执行，跳出循环
                    logger.info(f"编译尝试 {attempt + 1} 成功执行，返回码: {result.returncode}")
                    break
                    
                except PermissionError as e:
                    logger.warning(f"编译尝试 {attempt + 1} 权限不足: {e}")
                    if attempt == 2:  # 最后一次尝试
                        return False, f"权限不足，无法执行IAR编译。请尝试以管理员身份运行程序。\n错误详情: {e}"
                    continue
                except FileNotFoundError as e:
                    logger.warning(f"编译尝试 {attempt + 1} 找不到文件: {e}")
                    if attempt == 2:  # 最后一次尝试
                        return False, f"找不到IAR可执行文件: {self.iar_exe_path}\n请检查IAR安装路径是否正确。"
                    continue
                except Exception as e:
                    logger.warning(f"编译尝试 {attempt + 1} 异常: {e}")
                    if attempt == 2:  # 最后一次尝试
                        return False, f"执行IAR编译时发生异常: {e}"
                    continue
            
            if result is None:
                return False, "所有编译尝试都失败了"
            end_time = time.time()
            
            compile_time = end_time - start_time
            logger.info(f"编译耗时: {compile_time:.2f}秒")
            
            # 分析编译结果
            if result.returncode == 0:
                logger.info("编译成功")
                output_info = f"编译成功\n耗时: {compile_time:.2f}秒\n\n输出信息:\n{result.stdout}"
                return True, output_info
            else:
                logger.error("编译失败")
                error_info = f"编译失败\n返回码: {result.returncode}\n\n错误信息:\n{result.stderr}\n\n输出信息:\n{result.stdout}"
                return False, error_info
                
        except subprocess.TimeoutExpired:
            logger.error("编译超时")
            return False, f"编译超时 (>{self.timeout_seconds}秒)"
        except Exception as e:
            logger.error(f"编译异常: {e}")
            return False, f"编译异常: {str(e)}"
    
    def check_bin_file(self) -> bool:
        """
        检查生成的bin文件是否存在
        
        Returns:
            bool: bin文件是否存在
        """
        if not self.output_bin_path:
            logger.warning("未配置输出bin文件路径")
            return False
        
        bin_exists = os.path.exists(self.output_bin_path)
        if bin_exists:
            file_size = os.path.getsize(self.output_bin_path)
            logger.info(f"找到bin文件: {self.output_bin_path}, 大小: {file_size} 字节")
        else:
            logger.warning(f"未找到bin文件: {self.output_bin_path}")
        
        return bin_exists
    
    def get_bin_file_info(self, configuration: Dict = None) -> dict:
        """
        获取bin文件信息 - 优先使用配置信息
        
        Args:
            configuration: 配置信息（如果提供，优先使用）
            
        Returns:
            dict: bin文件信息
        """
        try:
            # 优先使用传入的配置参数，如果没有则使用实例变量
            config_to_use = configuration or self.configuration
            logger.info(f"使用的配置: {config_to_use}")
            
            # 如果提供了配置信息，优先使用配置中的bin文件路径
            if config_to_use and config_to_use.get('bin_file'):
                bin_file = config_to_use['bin_file']
                if os.path.exists(bin_file):
                    file_stat = os.stat(bin_file)
                    return {
                        'exists': True,
                        'path': bin_file,
                        'size': file_stat.st_size,
                        'modified_time': file_stat.st_mtime
                    }
                else:
                    logger.warning(f"配置中的bin文件不存在: {bin_file}")
            else:
                logger.warning("配置中未提供bin文件路径")
            
            # 如果以上方法都失败，返回默认信息
            logger.warning("未找到bin文件")
            return {
                'exists': False,
                'path': '',
                'size': 0,
                'modified_time': None
            }
            
        except Exception as e:
            logger.error(f"获取bin文件信息失败: {e}")
            return {
                'exists': False,
                'path': '',
                'size': 0,
                'modified_time': None
            }
    
    
    def build_and_check(self) -> Tuple[bool, str, dict]:
        """
        编译项目并检查结果
        
        Returns:
            Tuple[bool, str, dict]: (是否成功, 消息, bin文件信息)
        """
        # 执行编译
        success, message = self.build_project()
        
        # 获取bin文件信息
        bin_info = self.get_bin_file_info()
        
        if success and not bin_info['exists']:
            success = False
            message += "\n警告: 编译成功但未找到输出bin文件"
        
        return success, message, bin_info
    
    def smart_build(self, only_version_changed: bool = True) -> Tuple[bool, str]:
        """
        智能编译：根据修改内容决定编译策略
        
        Args:
            only_version_changed: 是否只有版本号发生变化
        
        Returns:
            Tuple[bool, str]: (编译是否成功, 输出信息)
        """
        if only_version_changed:
            logger.info("检测到仅版本号变化，使用增量编译（make）")
            return self.build_project(force_rebuild=False)
        else:
            logger.info("检测到代码变化，使用清理编译（rebuild all）")
            return self.build_project(force_rebuild=True)


def test_iar_builder():
    """测试IAR编译器功能"""
    # 测试配置
    test_config = {
        'iar_installation_path': 'C:/Program Files (x86)/IAR Systems/Embedded Workbench 8.3/common/bin/IarBuild.exe',
        'iar_workspace_path': '../EWARM/Project_N32A455.eww',
        'iar_project_path': '../EWARM/MCU.ewp',
        'output_bin_path': '../EWARM/Debug/Exe/MCU.bin',
        'build_configuration': 'Debug',
        'clean_before_build': True,
        'timeout_seconds': 300
    }
    
    builder = IARBuilder(test_config)
    
    logger.info("IAR编译器测试")
    logger.info(f"IAR可执行文件: {builder.iar_exe_path}")
    logger.info(f"项目文件: {builder.project_path}")
    logger.info(f"输出bin文件: {builder.output_bin_path}")
    
    # 检查bin文件
    bin_info = builder.get_bin_file_info()
    logger.info(f"Bin文件信息: {bin_info}")


if __name__ == "__main__":
    
    test_iar_builder()
