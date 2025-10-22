#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logger核心模块
提供日志配置和管理功能
"""

import os
import sys
import threading
from time import strftime, localtime
from loguru._logger import Core, Logger


def get_script_dir():
    """获取脚本所在目录，兼容exe和Python脚本环境"""
    if getattr(sys, 'frozen', False):
        # 如果是打包的exe，使用exe所在目录
        return os.path.dirname(os.path.abspath(sys.executable))
    else:
        # 如果是Python脚本，使用脚本所在目录
        return os.path.dirname(os.path.abspath(__file__))

def get_log_path():
    """
    获取日志文件路径
    
    Returns:
        str: 日志文件目录路径
    """
    try:
        # 获取脚本所在目录，而不是当前工作目录
        script_dir = get_script_dir()
        day = strftime("%Y-%m-%d", localtime())
        log_path = os.path.join(script_dir, 'log', day)
        
        # 确保目录存在
        if not os.path.exists(log_path):
            os.makedirs(log_path, exist_ok=True)
        
        return log_path
    except Exception as e:
        # 如果创建失败，尝试在用户文档目录创建
        try:
            import tempfile
            user_log_dir = os.path.join(os.path.expanduser("~"), "Documents", "Embedded_Firmware_Manager", "logs")
            if not os.path.exists(user_log_dir):
                os.makedirs(user_log_dir, exist_ok=True)
            return user_log_dir
        except:
            # 最后的备用方案：返回脚本目录
            return get_script_dir()

def set_log_level(level='INFO'):
    """
    设置日志级别
    
    Args:
        level: 日志级别，可选值: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    """
    global logger
    # 移除现有的处理器
    logger.remove()
    # 添加新的处理器
    logger.add(sink=sys.stderr, level=level)
    
    # 添加文件日志，确保路径有效
    try:
        log_path = get_log_path()
        if log_path:
            log_file = os.path.join(log_path, f"Time_{strftime('%Y-%m-%d_%H-%M-%S', localtime())}.log")
            logger.add(sink=log_file, level=level)
        else:
            # 如果无法获取日志路径，使用当前目录
            log_file = f"Time_{strftime('%Y-%m-%d_%H-%M-%S', localtime())}.log"
            logger.add(sink=log_file, level=level)
    except Exception as e:
        # 如果文件日志添加失败，只使用控制台日志
        pass


# 创建全局logger实例
logger = Logger(
    core=Core(),
    exception=None,
    depth=0,
    record=False,
    lazy=False,
    colors=False,
    raw=False,
    capture=True,
    patcher=None,
    extra={}
)

# 默认设置为INFO级别，检查stderr是否可用
try:
    if sys.stderr is not None:
        logger.add(sink=sys.stderr, level='INFO')
    else:
        # 如果stderr不可用，使用stdout
        logger.add(sink=sys.stdout, level='INFO')
except Exception as e:
    # 如果都不可用，尝试使用文件
    try:
        logger.add(sink="embedded_firmware_manager.log", level='INFO')
    except:
        # 最后的备用方案：不添加任何sink
        pass

# 文件日志将在第一次使用时添加
_file_log_added = False

def _add_file_log():
    """添加文件日志"""
    global _file_log_added
    if not _file_log_added:
        try:
            log_path = get_log_path()
            if log_path:
                log_file = os.path.join(log_path, f"Time_{strftime('%Y-%m-%d_%H-%M-%S', localtime())}.log")
                # 检查是否已经添加了相同路径的文件日志处理器
                try:
                    handlers = logger._core.handlers
                    for handler in handlers:
                        if hasattr(handler, '_sink') and hasattr(handler._sink, 'name') and handler._sink.name == log_file:
                            _file_log_added = True
                            return
                except:
                    # 如果检查失败，继续添加
                    pass
                
                logger.add(sink=log_file, level='INFO')
            else:
                # 如果无法获取日志路径，使用当前目录
                log_file = f"Time_{strftime('%Y-%m-%d_%H-%M-%S', localtime())}.log"
                logger.add(sink=log_file, level='INFO')
            _file_log_added = True
        except Exception as e:
            # 如果文件日志添加失败，只使用控制台日志
            _file_log_added = True  # 即使失败也标记为已添加，避免重复尝试
            pass

# 直接添加文件日志，不使用包装器
_add_file_log()