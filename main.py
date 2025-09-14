#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主应用程序
嵌入式固件管理工具 - 带GUI界面的Windows应用程序
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
import os
import sys
from lib_logger import logger
import threading
import queue
from datetime import datetime
from pathlib import Path
from typing import Optional

# 导入自定义模块
from git_manager import GitManager
from builder_factory import BuilderFactory
from project_analyzer_factory import ProjectAnalyzerFactory
from binary_modifier import BinaryModifier
from file_manager_factory import FileManagerFactory
from version_manager import VersionManager
from info_manager_factory import InfoManagerFactory
from path_manager_factory import PathManagerFactory
from tool_version_manager import ToolVersionManager
from version import VERSION

# 语言配置
LANGUAGES = {
    'zh_CN': {
        'name': '简体中文',
        'texts': {
            'app_title': '嵌入式固件管理工具',
            'project_path': '项目路径:',
            'iar_path': '编译工具路径:',
            'check_git': '检查Git状态',
            'check_version': '检查版本',
            'start_build': '开始编译',
            'open_settings': '设置',
            'open_firmware': '本地发布目录',
            'status_ready': '就绪',
            'status_checking': '检查中...',
            'status_building': '编译中...',
            'project_info': '项目信息',
            'firmware_version': '固件版本:',
            'git_status': 'Git状态:',
            'iar_path_display': '编译工具路径:',
            'flash_start_addr': 'Flash起始地址:',
            'settings_title': '设置',
            'project_settings': '项目设置',
            'binary_settings': '二进制设置',
            'compile_tool': '编译工具:',
            'iar_installation_path': 'IAR安装目录:',
            'mdk_installation_path': 'MDK安装目录:',
            'fw_publish_directory': '本地发布目录:',
            'remote_publish_directory': '远程发布目录:',
            'enable_remote_publish': '启用远程发布',
            'bin_start_address': 'bin起始地址:',
            'config_file': '配置文件:',
            'language': '语言:',
            'select_directory': '选择目录',
            'select': '选择',
            'save': '保存',
            'cancel': '取消',
            'example_bin_address': '(例如: 0x8000000)',
            'browse': '浏览',
            'log_output': '日志输出',
            'success': '成功',
            'error': '错误',
            'warning': '警告',
            'info': '信息',
            'not_checked': '未检查',
            'not_configured': '未配置',
            'msg_error': '错误',
            'msg_success': '成功',
            'msg_warning': '警告',
            'msg_info': '信息',
            'msg_config_error': '配置错误',
            'msg_config_incomplete': '配置不完整',
            'msg_compile_failed': '编译失败',
            'msg_modify_failed': '修改失败',
            'msg_file_process_failed': '文件处理失败',
            'msg_firmware_publish_failed': '固件发布失败',
            'msg_firmware_publish_error': '固件发布异常',
            'msg_cleanup_complete': '清理完成',
            'msg_cleanup_failed': '清理失败',
            'msg_settings_saved': '设置已保存',
            'msg_bin_address_format_error': 'bin起始地址格式错误',
            'msg_save_settings_failed': '保存设置失败',
            'msg_select_directory_error': '选择目录时出错',
            'msg_open_directory_failed': '打开目录失败',
            'msg_open_firmware_directory_failed': '打开固件目录失败',
            'msg_select_config_file_error': '选择配置文件时出错',
            'msg_select_iar_directory_error': '选择IAR目录时出错',
            'msg_not_git_repo': '当前目录不是Git仓库',
            'msg_cannot_get_commit_id': '无法获取commit ID',
            'feature_settings': '功能设置',
            'enable_git_commit_id': 'Git提交ID',
            'enable_file_size': '文件大小',
            'enable_bin_checksum': '二进制校验和',
            'enable_hash_value': '哈希校验和',
            'git_commit_id_keyword': 'Git提交ID变量:',
            'file_size_keyword': '文件大小变量:',
            'bin_checksum_keyword': '二进制校验和变量:',
            'hash_value_keyword': '哈希校验和变量:',
            'firmware_version_keyword': '固件版本变量:',
            'add_timestamp_to_filename': 'bin文件名添加时间戳',
            'publish_out_file': '发布.out文件',
            'feature_settings_desc': '选择要启用的功能模块，禁用后相关功能将不会执行',
            'msg_compile_success_no_bin': '编译成功但未找到输出bin文件',
            'msg_compile_complete': '编译完成！',
            'msg_compile_exception': '编译流程异常',
            'msg_firmware_directory_not_exist': '固件发布目录不存在',
            'msg_remote_publish_directory_not_exist': '远程发布目录不存在',
            'msg_remote_publish_success': '远程发布成功',
            'msg_remote_publish_failed': '远程发布失败',
            'msg_config_file_analysis_failed': '配置文件分析失败',
            'msg_check_config_file_pragma': '请检查配置文件是否包含正确的#pragma location定义。',
            'git_commit_dialog_title': '提交信息 & Release Notes',
            'git_commit_dialog_message': '请输入本次提交的更新信息（将同时用于Git提交和Release Notes）：',
            'git_commit_dialog_placeholder': '例如：修复了某个bug，添加了新功能等...\n\n注意：提交描述会自动添加"发布xxxx版本"前缀\n\n快捷键：Ctrl+Enter 确认，Escape 取消',
            'git_commit_dialog_ok': '确定',
            'git_commit_dialog_cancel': '取消',
            'release_note_title': 'Release Notes',
            'release_note_created': 'Release note文件已创建',
            'release_note_updated': 'Release note文件已更新',
            'enabled': '启用',
            'disabled': '未启用',
            'bin_address_auto_note': '注意：bin起始地址现在从ICF文件自动获取，无需手动配置',
            'build_configuration': '编译配置:',
            'not_selected': '未选择',
            'refresh_config': '刷新配置',
            'no_valid_configs': '未找到有效配置',
            'no_configs_found': '未找到有效的编译配置',
            'refresh_config_failed': '刷新配置失败',
            'invalid_project_path': '项目路径无效，无法刷新配置',
            'config_parse_failed': '解析项目配置失败',
            'no_project_file': '未找到项目文件',
            'configs_found': '找到 {count} 个配置: {names}',
            'current_selection': '当前选择: {name}',
            'config_selected': '选择配置: {name}',
            'output_directory': '输出目录: {dir}',
            'debug_mode': 'Debug模式: {mode}',
            'config_selection_failed': '配置选择失败',
            'checking_git_status': '检查Git状态中...',
            'not_git_repo_status': '当前目录不是Git仓库',
            'has_uncommitted_changes': '检测到未提交的更改',
            'git_workdir_clean': 'Git工作区干净，可以编译',
            'git_check_complete': 'Git状态检查完成',
            'checking_firmware_version': '检查固件版本中...',
            'version_check_complete': '版本检查完成',
            'start_build_process': '开始编译流程...',
            'input_update_info': '输入更新信息...',
            'committing_changes': '提交更改...',
            'updating_version': '更新版本号...',
            'updating_release_notes': '更新Release Notes...',
            'committing_version_changes': '提交版本号更改和Release Notes...',
            'compiling_project': '编译项目中...',
            'modifying_binary': '修改二进制文件...',
            'processing_files': '处理输出文件...',
            'publishing_firmware': '发布固件...',
            'publishing_remote': '发布到远程目录...',
            'build_process_complete': '编译流程完成',
            'language_options': {
                'zh_CN': 'zh_CN 简体中文',
                'zh_TW': 'zh_TW 繁體中文',
                'en_US': 'en_US English'
            }
        }
    },
    'zh_TW': {
        'name': '繁體中文',
        'texts': {
            'app_title': 'IAR固件發布工具',
            'project_path': '專案路徑:',
            'iar_path': '編譯工具路徑:',
            'check_git': '檢查Git狀態',
            'check_version': '檢查版本',
            'start_build': '開始編譯',
            'open_settings': '設定',
            'open_firmware': '本地發布目錄',
            'status_ready': '就緒',
            'status_checking': '檢查中...',
            'status_building': '編譯中...',
            'project_info': '專案資訊',
            'firmware_version': '固件版本:',
            'git_status': 'Git狀態:',
            'iar_path_display': '編譯工具路徑:',
            'flash_start_addr': 'Flash起始位址:',
            'settings_title': '設定',
            'project_settings': '專案設定',
            'binary_settings': '二進位設定',
            'compile_tool': '編譯工具:',
            'iar_installation_path': 'IAR安裝目錄:',
            'mdk_installation_path': 'MDK安裝目錄:',
            'fw_publish_directory': '本地發布目錄:',
            'remote_publish_directory': '遠程發布目錄:',
            'enable_remote_publish': '啟用遠程發布',
            'bin_start_address': 'bin起始位址:',
            'config_file': '配置檔案:',
            'language': '語言:',
            'select_directory': '選擇目錄',
            'select': '選擇',
            'save': '儲存',
            'cancel': '取消',
            'example_bin_address': '(例如: 0x8000000)',
            'browse': '瀏覽',
            'log_output': '日誌輸出',
            'success': '成功',
            'error': '錯誤',
            'warning': '警告',
            'info': '資訊',
            'not_checked': '未檢查',
            'not_configured': '未配置',
            'msg_error': '錯誤',
            'msg_success': '成功',
            'msg_warning': '警告',
            'msg_info': '資訊',
            'msg_config_error': '配置錯誤',
            'msg_config_incomplete': '配置不完整',
            'msg_compile_failed': '編譯失敗',
            'msg_modify_failed': '修改失敗',
            'msg_file_process_failed': '檔案處理失敗',
            'msg_firmware_publish_failed': '固件發布失敗',
            'msg_firmware_publish_error': '固件發布異常',
            'msg_cleanup_complete': '清理完成',
            'msg_cleanup_failed': '清理失敗',
            'msg_settings_saved': '設定已儲存',
            'msg_bin_address_format_error': 'bin起始位址格式錯誤',
            'msg_save_settings_failed': '儲存設定失敗',
            'msg_select_directory_error': '選擇目錄時出錯',
            'msg_open_directory_failed': '開啟目錄失敗',
            'msg_open_firmware_directory_failed': '開啟固件目錄失敗',
            'msg_select_config_file_error': '選擇配置檔案時出錯',
            'msg_select_iar_directory_error': '選擇IAR目錄時出錯',
            'msg_not_git_repo': '當前目錄不是Git倉庫',
            'msg_cannot_get_commit_id': '無法獲取commit ID',
            'feature_settings': '功能設置',
            'enable_git_commit_id': 'Git提交ID',
            'enable_file_size': '檔案大小',
            'enable_bin_checksum': '二進制校驗和',
            'enable_hash_value': '哈希校驗和',
            'git_commit_id_keyword': 'Git提交ID變數:',
            'file_size_keyword': '文件大小變數:',
            'bin_checksum_keyword': '二進制校驗和變數:',
            'hash_value_keyword': '哈希校驗和變數:',
            'firmware_version_keyword': '固件版本變數:',
            'add_timestamp_to_filename': 'bin檔案名添加時間戳',
            'publish_out_file': '發布.out檔案',
            'feature_settings_desc': '選擇要啟用的功能模組，禁用後相關功能將不會執行',
            'msg_compile_success_no_bin': '編譯成功但未找到輸出bin檔案',
            'msg_compile_complete': '編譯完成！',
            'msg_compile_exception': '編譯流程異常',
            'msg_firmware_directory_not_exist': '固件發布目錄不存在',
            'msg_remote_publish_directory_not_exist': '遠程發布目錄不存在',
            'msg_remote_publish_success': '遠程發布成功',
            'msg_remote_publish_failed': '遠程發布失敗',
            'msg_config_file_analysis_failed': '配置檔案分析失敗',
            'msg_check_config_file_pragma': '請檢查配置檔案是否包含正確的#pragma location定義。',
            'git_commit_dialog_title': '提交資訊 & Release Notes',
            'git_commit_dialog_message': '請輸入本次提交的更新資訊（將同時用於Git提交和Release Notes）：',
            'git_commit_dialog_placeholder': '例如：修復了某個bug，添加了新功能等...\n\n注意：提交描述會自動添加"發布xxxx版本"前綴\n\n快捷鍵：Ctrl+Enter 確認，Escape 取消',
            'git_commit_dialog_ok': '確定',
            'git_commit_dialog_cancel': '取消',
            'release_note_title': 'Release Notes',
            'release_note_created': 'Release note檔案已建立',
            'release_note_updated': 'Release note檔案已更新',
            'enabled': '啟用',
            'disabled': '未啟用',
            'bin_address_auto_note': '注意：bin起始位址現在從ICF檔案自動獲取，無需手動配置',
            'build_configuration': '編譯配置:',
            'not_selected': '未選擇',
            'refresh_config': '刷新配置',
            'no_valid_configs': '未找到有效配置',
            'no_configs_found': '未找到有效的編譯配置',
            'refresh_config_failed': '刷新配置失敗',
            'invalid_project_path': '項目路徑無效，無法刷新配置',
            'config_parse_failed': '解析項目配置失敗',
            'no_project_file': '未找到項目檔案',
            'configs_found': '找到 {count} 個配置: {names}',
            'current_selection': '當前選擇: {name}',
            'config_selected': '選擇配置: {name}',
            'output_directory': '輸出目錄: {dir}',
            'debug_mode': 'Debug模式: {mode}',
            'config_selection_failed': '配置選擇失敗',
            'checking_git_status': '檢查Git狀態中...',
            'not_git_repo_status': '當前目錄不是Git倉庫',
            'has_uncommitted_changes': '檢測到未提交的更改',
            'git_workdir_clean': 'Git工作區乾淨，可以編譯',
            'git_check_complete': 'Git狀態檢查完成',
            'checking_firmware_version': '檢查固件版本中...',
            'version_check_complete': '版本檢查完成',
            'start_build_process': '開始編譯流程...',
            'input_update_info': '輸入更新資訊...',
            'committing_changes': '提交更改...',
            'updating_version': '更新版本號...',
            'updating_release_notes': '更新Release Notes...',
            'committing_version_changes': '提交版本號更改和Release Notes...',
            'compiling_project': '編譯專案中...',
            'modifying_binary': '修改二進制檔案...',
            'processing_files': '處理輸出檔案...',
            'publishing_firmware': '發布固件...',
            'publishing_remote': '發布到遠程目錄...',
            'build_process_complete': '編譯流程完成',
            'language_options': {
                'zh_CN': 'zh_CN 简体中文',
                'zh_TW': 'zh_TW 繁體中文',
                'en_US': 'en_US English'
            }
        }
    },
    'en_US': {
        'name': 'English',
        'texts': {
            'app_title': 'Embedded Firmware Manager',
            'project_path': 'Project Path:',
            'iar_path': 'Compile Tool Path:',
            'check_git': 'Check Git Status',
            'check_version': 'Check Version',
            'start_build': 'Start Build',
            'open_settings': 'Settings',
            'open_firmware': 'Local Publish Directory',
            'status_ready': 'Ready',
            'status_checking': 'Checking...',
            'status_building': 'Building...',
            'project_info': 'Project Info',
            'firmware_version': 'Firmware Version:',
            'git_status': 'Git Status:',
            'iar_path_display': 'Compile Tool Path:',
            'flash_start_addr': 'Flash Start Address:',
            'settings_title': 'Settings',
            'project_settings': 'Project Settings',
            'binary_settings': 'Binary Settings',
            'compile_tool': 'Compile Tool:',
            'iar_installation_path': 'IAR Installation Path:',
            'mdk_installation_path': 'MDK Installation Path:',
            'fw_publish_directory': 'Local Publish Directory:',
            'remote_publish_directory': 'Remote Publish Directory:',
            'enable_remote_publish': 'Enable Remote Publish',
            'bin_start_address': 'Bin Start Address:',
            'config_file': 'Config File:',
            'language': 'Language:',
            'select_directory': 'Select Directory',
            'select': 'Select',
            'save': 'Save',
            'cancel': 'Cancel',
            'example_bin_address': '(e.g.: 0x8000000)',
            'browse': 'Browse',
            'log_output': 'Log Output',
            'success': 'Success',
            'error': 'Error',
            'warning': 'Warning',
            'info': 'Info',
            'not_checked': 'Not Checked',
            'not_configured': 'Not Configured',
            'msg_error': 'Error',
            'msg_success': 'Success',
            'msg_warning': 'Warning',
            'msg_info': 'Info',
            'msg_config_error': 'Configuration Error',
            'msg_config_incomplete': 'Configuration Incomplete',
            'msg_compile_failed': 'Compilation Failed',
            'msg_modify_failed': 'Modification Failed',
            'msg_file_process_failed': 'File Processing Failed',
            'msg_firmware_publish_failed': 'Firmware Publish Failed',
            'msg_firmware_publish_error': 'Firmware Publish Error',
            'msg_cleanup_complete': 'Cleanup Complete',
            'msg_cleanup_failed': 'Cleanup Failed',
            'msg_settings_saved': 'Settings Saved',
            'msg_bin_address_format_error': 'Bin Start Address Format Error',
            'msg_save_settings_failed': 'Save Settings Failed',
            'msg_select_directory_error': 'Error Selecting Directory',
            'msg_open_directory_failed': 'Failed to Open Directory',
            'msg_open_firmware_directory_failed': 'Failed to Open Firmware Directory',
            'msg_select_config_file_error': 'Error Selecting Config File',
            'msg_select_iar_directory_error': 'Error Selecting IAR Directory',
            'msg_not_git_repo': 'Current directory is not a Git repository',
            'msg_cannot_get_commit_id': 'Cannot get commit ID',
            'feature_settings': 'Feature Settings',
            'enable_git_commit_id': 'Git Commit ID',
            'enable_file_size': 'File Size',
            'enable_bin_checksum': 'Binary Checksum',
            'enable_hash_value': 'Hash Value',
            'git_commit_id_keyword': 'Git Commit ID Variable:',
            'file_size_keyword': 'File Size Variable:',
            'bin_checksum_keyword': 'Binary Checksum Variable:',
            'hash_value_keyword': 'Hash Value Variable:',
            'firmware_version_keyword': 'Firmware Version Variable:',
            'add_timestamp_to_filename': 'Add timestamp to bin filename',
            'publish_out_file': 'Publish .out file',
            'feature_settings_desc': 'Select which feature modules to enable. Disabled features will not be executed.',
            'msg_compile_success_no_bin': 'Compilation successful but no output bin file found',
            'msg_compile_complete': 'Compilation Complete!',
            'msg_compile_exception': 'Compilation Process Exception',
            'msg_firmware_directory_not_exist': 'Firmware publish directory does not exist',
            'msg_remote_publish_directory_not_exist': 'Remote publish directory does not exist',
            'msg_remote_publish_success': 'Remote publish successful',
            'msg_remote_publish_failed': 'Remote publish failed',
            'msg_config_file_analysis_failed': 'Config file analysis failed',
            'msg_check_config_file_pragma': 'Please check if the config file contains correct #pragma location definitions.',
            'git_commit_dialog_title': 'Commit Message & Release Notes',
            'git_commit_dialog_message': 'Please enter the update information for this commit (will be used for both Git commit and Release Notes):',
            'git_commit_dialog_placeholder': 'e.g.: Fixed a bug, added new feature, etc...\n\nNote: "Release xxxx version" prefix will be added automatically\n\nShortcuts: Ctrl+Enter to confirm, Escape to cancel',
            'git_commit_dialog_ok': 'OK',
            'git_commit_dialog_cancel': 'Cancel',
            'release_note_title': 'Release Notes',
            'release_note_created': 'Release note file created',
            'release_note_updated': 'Release note file updated',
            'enabled': 'Enabled',
            'disabled': 'Disabled',
            'bin_address_auto_note': 'Note: Bin start address is now automatically obtained from ICF file, no manual configuration needed',
            'build_configuration': 'Build Configuration:',
            'not_selected': 'Not Selected',
            'refresh_config': 'Refresh Config',
            'no_valid_configs': 'No Valid Configs Found',
            'no_configs_found': 'No Valid Build Configurations Found',
            'refresh_config_failed': 'Refresh Config Failed',
            'invalid_project_path': 'Invalid project path, cannot refresh configurations',
            'config_parse_failed': 'Failed to parse project configurations',
            'no_project_file': 'No Project File Found',
            'configs_found': 'Found {count} configurations: {names}',
            'current_selection': 'Current selection: {name}',
            'config_selected': 'Configuration selected: {name}',
            'output_directory': 'Output directory: {dir}',
            'debug_mode': 'Debug mode: {mode}',
            'config_selection_failed': 'Configuration selection failed',
            'checking_git_status': 'Checking Git status...',
            'not_git_repo_status': 'Current directory is not a Git repository',
            'has_uncommitted_changes': 'Uncommitted changes detected',
            'git_workdir_clean': 'Git working directory is clean, ready to build',
            'git_check_complete': 'Git status check complete',
            'checking_firmware_version': 'Checking firmware version...',
            'version_check_complete': 'Version check complete',
            'start_build_process': 'Starting build process...',
            'input_update_info': 'Input update information...',
            'committing_changes': 'Committing changes...',
            'updating_version': 'Updating version...',
            'updating_release_notes': 'Updating Release Notes...',
            'committing_version_changes': 'Committing version changes and Release Notes...',
            'compiling_project': 'Compiling project...',
            'modifying_binary': 'Modifying binary file...',
            'processing_files': 'Processing output files...',
            'publishing_firmware': 'Publishing firmware...',
            'publishing_remote': 'Publishing to remote directory...',
            'build_process_complete': 'Build process complete',
            'language_options': {
                'zh_CN': 'zh_CN 简体中文',
                'zh_TW': 'zh_TW 繁體中文',
                'en_US': 'en_US English'
            }
        }
    }
}


class MCUAutoBuildApp:
    """MCU自动编译工具主应用程序"""
    
    def __init__(self):
        """初始化应用程序"""
        self.root = tk.Tk()
        self.config = {}
        self.log_queue = queue.Queue()
        
        # 初始化语言设置
        self.current_language = 'zh_CN'  # 默认简体中文
        self.texts = LANGUAGES[self.current_language]['texts']
        
        # 初始化组件
        self.git_manager = None
        self.builder = None
        self.binary_modifier = None
        self.file_manager = None
        self.version_manager = None
        self.info_manager = None
        self.path_manager = None
        self.tool_version_manager = ToolVersionManager()
        
        # 缓存信息文件路径，避免重复查找
        self.cached_info_file_path = None
        
        # 配置相关变量
        self.available_configurations = []
        self.selected_configuration = None
        
        # 操作成功标志位
        self.git_status_checked = False
        self.version_checked = False
        
        # 设置窗口
        self.setup_window()
        
        # 加载配置（包括语言设置）
        self.load_config()
        
        # 创建界面（语言设置已生效）
        self.create_widgets()
        
        # 加载用户配置到界面
        self._load_user_config_to_ui()
        
        # 初始化flash起始地址显示
        self._update_flash_start_addr_display()
        
        # 初始化日志
        self.setup_logging()
        
        # 启动日志处理
        self.process_log_queue()
    
    def set_language(self, language_code: str):
        """设置语言"""
        if language_code in LANGUAGES:
            self.current_language = language_code
            self.texts = LANGUAGES[language_code]['texts']
            # 只有在logger初始化后才记录日志
            if hasattr(self, 'logger'):
                logger.info(f"语言已切换为: {LANGUAGES[language_code]['name']}")
            else:
                logger.info(f"语言已切换为: {LANGUAGES[language_code]['name']}")
            return True
        return False
    
    def get_text(self, key: str) -> str:
        """获取本地化文本"""
        return self.texts.get(key, key)
    
    def setup_window(self):
        """设置主窗口"""
        # 获取工具版本
        self.root.title(f"{self.get_text('app_title')} v{VERSION}")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # 设置窗口图标
        try:
            icon_path = os.path.join(self._get_script_dir(), "icon_efm.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
                logger.info(f"设置窗口图标: {icon_path}")
            else:
                logger.warning(f"图标文件不存在: {icon_path}")
        except Exception as e:
            logger.warning(f"设置窗口图标失败: {e}")
        
        # 设置关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def _get_script_dir(self):
        """获取脚本所在目录，兼容exe和Python脚本环境"""
        if getattr(sys, 'frozen', False):
            # 如果是打包的exe，使用exe所在目录
            return os.path.dirname(os.path.abspath(sys.executable))
        else:
            # 如果是Python脚本，使用脚本所在目录
            return os.path.dirname(os.path.abspath(__file__))
    
    def load_config(self):
        """加载配置文件"""
        # 获取脚本所在目录，确保exe环境下能正确找到配置文件
        script_dir = self._get_script_dir()
        
        # 使用绝对路径加载配置文件
        default_config_path = os.path.join(script_dir, "config.json")
        user_config_path = os.path.join(script_dir, "user_config.json")
        
        try:
            # 优先加载用户配置
            if os.path.exists(user_config_path):
                with open(user_config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                self.log_message(f"用户配置文件加载成功，包含键: {list(self.config.keys())}")
                if 'compile_tool' in self.config:
                    self.log_message(f"用户配置中的compile_tool: {self.config['compile_tool']}")
                else:
                    self.log_message("警告：用户配置中缺少compile_tool字段")
            else:
                # 如果user_config.json不存在，加载默认配置
                if os.path.exists(default_config_path):
                    with open(default_config_path, 'r', encoding='utf-8') as f:
                        self.config = json.load(f)
                    self.log_message("用户配置文件不存在，加载默认配置文件")
                else:
                    self.log_message("用户配置文件和默认配置文件都不存在，使用内置默认配置")
                    self.config = self.get_default_config()
                
                # 如果默认配置也没有，尝试使用示例配置
                if not self.config or not self.config.get('compile_tool'):
                    example_config_path = os.path.join(script_dir, "user_config.example.json")
                    if os.path.exists(example_config_path):
                        with open(example_config_path, 'r', encoding='utf-8') as f:
                            self.config = json.load(f)
                        self.log_message("使用示例配置文件")
                    else:
                        self.log_message("所有配置文件都不存在，将创建新的用户配置")
                        self._create_user_config()
            
            # 优先加载语言设置（在界面创建之前）
            if 'language' in self.config:
                language = self.config['language']
                if language in LANGUAGES:
                    self.set_language(language)
                    self.log_message(f"语言设置已加载: {LANGUAGES[language]['name']}")
                else:
                    self.log_message(f"不支持的语言设置: {language}，使用默认语言")
            else:
                self.log_message("未找到语言设置，使用默认语言")
            
            # 初始化路径管理器和配置分析器 - 使用用户指定的项目路径
            project_path = self.config.get('project_path', '')
            if not project_path or not os.path.exists(project_path):
                project_path = os.path.dirname(os.path.abspath(__file__))  # 使用脚本所在目录
                self.log_message(f"使用脚本所在目录作为项目路径: {project_path}")
            else:
                self.log_message(f"使用用户指定的项目路径: {project_path}")
            
            # 根据编译工具创建相应的路径管理器和信息管理器
            compile_tool = self.config.get('compile_tool')
            if not compile_tool:
                self.log_message("错误：配置文件中缺少compile_tool字段，请检查配置文件")
                self.log_message(f"当前配置键: {list(self.config.keys())}")
                return
            
            self.log_message(f"使用编译工具: {compile_tool}")
            self.path_manager = PathManagerFactory.create_path_manager(compile_tool, project_path)
            self.info_manager = InfoManagerFactory.create_manager(compile_tool, self.config)
            self.config = self.path_manager.auto_find_paths(self.config)
            
            # 自动查找配置文件
            if not self.config.get('binary_settings', {}).get('config_file'):
                info_file_name = self.config.get('info_file', '')
                if info_file_name:
                    config_file, _ = self.get_info_file_path_with_details(project_path)
                if config_file:
                    self.config['config_file'] = config_file
                    self.log_message(f"自动找到配置文件: {config_file}")
                else:
                    self.log_message("未设置配置文件名称，跳过自动查找")
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            self.config = self.get_default_config()
    
    
    def _create_user_config(self):
        """创建用户配置文件"""
        try:
            user_config = {
                    "iar_installation_path": "",
                    "project_path": "",
                    "fw_publish_directory": "./fw_publish",
                    "remote_publish_directory": "",
                    "enable_remote_publish": False,
                "info_file": "",
                "language": "zh_CN",
                "enable_git_commit_id": True,
                "enable_file_size": True,
                "enable_bin_checksum": True,
                "enable_hash_value": True,
                "git_commit_id_keyword": "__git_commit_id",
                "file_size_keyword": "__file_size",
                "bin_checksum_keyword": "__bin_checksum",
                "hash_value_keyword": "__hash_value",
                "firmware_version_keyword": "__Firmware_Version",
                "add_timestamp_to_filename": False,
                "publish_out_file": False
            }
            
            # 获取脚本所在目录
            script_dir = self._get_script_dir()
            user_config_path = os.path.join(script_dir, "user_config.json")
            with open(user_config_path, 'w', encoding='utf-8') as f:
                json.dump(user_config, f, indent=4, ensure_ascii=False)
            
            self.log_message("用户配置文件创建成功")
        except Exception as e:
            self.log_message(f"创建用户配置文件失败: {e}")
    
    def _load_user_config_to_ui(self):
        """将用户配置加载到界面"""
        try:
            # 加载项目路径（只有在界面还没有设置时才从配置文件加载）
            current_ui_path = self.project_path_var.get()
            project_path = ''
            if not current_ui_path or current_ui_path.strip() == '':
                project_path = self.config.get('project_path', '')
            if project_path:
                self.project_path_var.set(project_path)
                self.log_message(f"已加载项目路径: {project_path}")
            else:
                self.log_message(f"保持当前项目路径设置: {current_ui_path}")
            
            # 加载编译工具路径并显示
            compile_tool = self.config.get('compile_tool', 'IAR')
            if compile_tool == 'IAR':
                tool_path = self.config.get('iar_installation_path', '')
                tool_name = "IAR"
            else:  # MDK
                tool_path = self.config.get('mdk_installation_path', '')
                tool_name = "MDK"
            
            if tool_path:
                self.iar_path_display_var.set(tool_path)
                self.log_message(f"已加载{tool_name}路径: {tool_path}")
            else:
                self.iar_path_display_var.set("未配置")
                self.log_message(f"{tool_name}路径未配置")
            
            # 加载信息文件信息
            info_file = self.config.get('info_file', '')
            if info_file:
                self.log_message(f"已加载信息文件: {info_file}")
            
            # 加载功能设置信息
            enable_git_commit_id = self.config.get('enable_git_commit_id', True)
            enable_file_size = self.config.get('enable_file_size', True)
            enable_bin_checksum = self.config.get('enable_bin_checksum', True)
            self.log_message(f"功能设置 - Git提交ID: {enable_git_commit_id}, 文件大小: {enable_file_size}, 校验和: {enable_bin_checksum}")
            
        except Exception as e:
            self.log_message(f"加载用户配置到界面失败: {e}")
    
    def get_default_config(self):
        """获取默认配置"""
        return {
            "compile_tool": "IAR",
            "binary_settings": {
                "firmware_version_offset": 0,
                "git_commit_id_offset": 0,
                "file_size_offset": 0,
                "bin_checksum_offset": 0,
                "commit_id_size": 7,
                "crc_size": 4,
                "reserved_area_size": 512
            },
            "git_settings": {
                "check_uncommitted_changes": True,
                "auto_commit": False,
                "commit_message_template": "Auto build: {timestamp}"
            },
            "build_settings": {
                "build_configuration": "Debug",
                "clean_before_build": False,
                "timeout_seconds": 300
            },
            "ui_settings": {
                "window_title": "嵌入式固件管理工具",
                "window_size": "1000x700",
                "theme": "default"
            },
            "version_settings": {
                "version_pattern": r"V(\d)\.(\d)\.(\d)\.(\d)",
                "max_version_parts": [9, 9, 9, 9],
                "auto_increment": True,
                "keep_firmware_count": 10
            }
        }
    
    def setup_logging(self):
        """设置日志系统"""
        # 使用统一的logger，无需额外设置
        logger.info("应用程序启动")
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(7, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text=self.get_text('app_title'), 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 项目信息框架
        info_frame = ttk.LabelFrame(main_frame, text=self.get_text('project_info'), padding="10")
        info_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)
        
        # 项目路径
        ttk.Label(info_frame, text=self.get_text('project_path')).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        # 优先使用配置中的项目路径，如果没有则使用脚本所在目录
        initial_project_path = self.config.get('project_path', os.path.dirname(os.path.abspath(__file__)))
        self.project_path_var = tk.StringVar(value=initial_project_path)
        ttk.Entry(info_frame, textvariable=self.project_path_var, state="readonly").grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(info_frame, text=self.get_text('browse'), command=self.browse_project_path).grid(row=0, column=2)
        
        # 编译配置选择
        ttk.Label(info_frame, text=self.get_text('build_configuration')).grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.configuration_var = tk.StringVar(value=self.get_text('not_selected'))
        self.configuration_combo = ttk.Combobox(info_frame, textvariable=self.configuration_var, 
                                              state="readonly", width=20)
        self.configuration_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.configuration_combo.bind('<<ComboboxSelected>>', self.on_configuration_selected)
        ttk.Button(info_frame, text=self.get_text('refresh_config'), command=self.refresh_configurations).grid(row=1, column=2)
        
        # IAR路径
        ttk.Label(info_frame, text=self.get_text('iar_path_display')).grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        self.iar_path_display_var = tk.StringVar(value=self.get_text('not_configured'))
        iar_path_label = ttk.Label(info_frame, textvariable=self.iar_path_display_var, foreground="green")
        iar_path_label.grid(row=2, column=1, sticky=(tk.W, tk.E))
        
        # Flash起始地址
        ttk.Label(info_frame, text=self.get_text('flash_start_addr')).grid(row=3, column=0, sticky=tk.W, padx=(0, 10))
        self.flash_start_addr_var = tk.StringVar(value=self.get_text('not_checked'))
        ttk.Label(info_frame, textvariable=self.flash_start_addr_var, foreground="purple").grid(
            row=3, column=1, sticky=tk.W)
        
        # Git状态
        ttk.Label(info_frame, text=self.get_text('git_status')).grid(row=4, column=0, sticky=tk.W, padx=(0, 10))
        self.git_status_var = tk.StringVar(value=self.get_text('not_checked'))
        ttk.Label(info_frame, textvariable=self.git_status_var, foreground="orange").grid(
            row=4, column=1, sticky=tk.W)
        
        # 固件版本
        ttk.Label(info_frame, text=self.get_text('firmware_version')).grid(row=5, column=0, sticky=tk.W, padx=(0, 10))
        self.firmware_version_var = tk.StringVar(value=self.get_text('not_checked'))
        ttk.Label(info_frame, textvariable=self.firmware_version_var, foreground="blue").grid(
            row=5, column=1, sticky=tk.W)
        
        # 操作按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=(0, 10))
        
        # 按钮
        ttk.Button(button_frame, text=self.get_text('check_git'), command=self.check_git_status).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text=self.get_text('check_version'), command=self.check_version).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text=self.get_text('start_build'), command=self.start_build).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text=self.get_text('open_firmware'), command=self.open_firmware_directory).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text=self.get_text('open_settings'), command=self.open_settings).pack(side=tk.LEFT)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                          mode='indeterminate')
        self.progress_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 日志输出框架
        log_frame = ttk.LabelFrame(main_frame, text=self.get_text('log_output'), padding="5")
        log_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, state="disabled")
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 状态栏
        self.status_var = tk.StringVar(value=self.get_text('status_ready'))
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E))
    
    def log_message(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        # 添加到队列
        self.log_queue.put(log_entry)
    
    def process_log_queue(self):
        """处理日志队列"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.config(state="normal")
                self.log_text.insert(tk.END, message)
                self.log_text.see(tk.END)
                self.log_text.config(state="disabled")
        except queue.Empty:
            pass
        
        # 每100ms检查一次
        self.root.after(100, self.process_log_queue)
    
    def update_status(self, message):
        """更新状态栏"""
        self.status_var.set(message)
        self.log_message(message)
    
    def browse_project_path(self):
        """浏览项目路径"""
        try:
            # 获取当前项目路径作为初始目录
            initial_dir = self.project_path_var.get() or os.path.dirname(os.path.abspath(__file__))
            self.log_message(f"文件对话框初始目录: {initial_dir}")
            
            directory = filedialog.askdirectory(
                title="选择项目目录",
                initialdir=initial_dir
            )
            if directory:
                self.project_path_var.set(directory)
                self.clear_info_file_cache()  # 清除信息文件缓存
                self.log_message(f"选择项目路径: {directory}")
                
                # 更新配置
                self.config['project_path'] = directory
                
                # 重新初始化PathManager以使用新的项目路径
                compile_tool = self.config.get('compile_tool', 'IAR')
                self.path_manager = PathManagerFactory.create_path_manager(compile_tool, directory)
                self.config = self.path_manager.auto_find_paths(self.config)
                self.log_message("已重新搜索项目文件")
                
                # 刷新配置列表
                self.refresh_configurations()
                
                # 自动获取flash偏移地址
                flash_offset = self.path_manager.get_flash_offset_from_configuration(self.selected_configuration)
                if flash_offset:
                    # 更新配置中的bin起始地址
                    if 'binary_settings' not in self.config:
                        self.config['binary_settings'] = {}
                    self.config['binary_settings']['bin_start_address'] = flash_offset
                    self.log_message(f"自动获取flash偏移地址: 0x{flash_offset:X}")
                else:
                    self.log_message("无法自动获取flash偏移地址，请手动设置")
                
                # 保存到配置文件
                self.save_config()
            else:
                self.log_message("用户取消了目录选择")
        except Exception as e:
            self.log_message(f"选择目录时出错: {e}")
            messagebox.showerror(self.get_text('msg_error'), f"{self.get_text('msg_select_directory_error')}: {e}")
    
    def find_iar_executable(self, iar_dir: str) -> str:
        """
        在IAR安装目录中查找IarBuild.exe
        
        Args:
            iar_dir: IAR安装目录
            
        Returns:
            str: IarBuild.exe的完整路径，未找到返回空字符串
        """
        possible_paths = [
            os.path.join(iar_dir, "bin", "IarBuild.exe"),
            os.path.join(iar_dir, "IarBuild.exe"),
            os.path.join(iar_dir, "arm", "bin", "IarBuild.exe"),
            os.path.join(iar_dir, "EWARM", "bin", "IarBuild.exe")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return ""
    
    def find_mdk_executable(self, mdk_dir: str) -> str:
        """
        在MDK安装目录中查找UV4.exe
        
        Args:
            mdk_dir: MDK安装目录
            
        Returns:
            str: UV4.exe的完整路径，未找到返回空字符串
        """
        possible_paths = [
            os.path.join(mdk_dir, "UV4", "UV4.exe"),
            os.path.join(mdk_dir, "UV4.exe"),
            os.path.join(mdk_dir, "bin", "UV4.exe"),
            os.path.join(mdk_dir, "ARM", "UV4", "UV4.exe"),
            os.path.join(mdk_dir, "ARM", "bin", "UV4.exe")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return ""
    
    
    def get_info_file_path_with_details(self, project_path: str) -> tuple[Optional[str], str]:
        """
        获取信息文件路径，并返回详细的错误信息
        
        Args:
            project_path: 项目路径
            
        Returns:
            tuple: (文件路径, 错误信息)
        """
        if self.cached_info_file_path and os.path.exists(self.cached_info_file_path):
            return self.cached_info_file_path, ""
        
        if not self.path_manager:
            compile_tool = self.config.get('compile_tool', 'IAR')
            self.path_manager = PathManagerFactory.create_path_manager(compile_tool, project_path)
        
        info_file_name = self.config.get('info_file', 'main.c')
        file_path, error_msg = self.path_manager.find_info_file_with_details(info_file_name)
        if file_path:
            self.cached_info_file_path = file_path
        return file_path, error_msg
    
    def clear_info_file_cache(self):
        """清除信息文件路径缓存"""
        self.cached_info_file_path = None
    
    
    def save_config(self):
        """保存用户配置到文件"""
        try:
            # 读取现有的用户配置文件
            script_dir = self._get_script_dir()
            user_config_path = os.path.join(script_dir, "user_config.json")
            
            if os.path.exists(user_config_path):
                with open(user_config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
            else:
                user_config = {}
            
            # 只更新项目路径
            user_config["project_path"] = self.project_path_var.get()
            
            # 保存信息文件文件名（只存储文件名，不存储路径）
            info_file_path = self.config.get('info_file', '')
            if info_file_path:
                info_file_name = os.path.basename(info_file_path)
                user_config['info_file'] = info_file_name
            
            # 保存到用户配置文件
            script_dir = self._get_script_dir()
            user_config_path = os.path.join(script_dir, "user_config.json")
            with open(user_config_path, 'w', encoding='utf-8') as f:
                json.dump(user_config, f, indent=4, ensure_ascii=False)
            
            # 更新内存中的配置
            self.config.update(user_config)
            
            self.log_message("用户配置已保存")
        except Exception as e:
            self.log_message(f"保存用户配置失败: {e}")
    
    def check_git_status(self):
        """检查Git状态"""
        def check_thread():
            try:
                self.update_status(self.get_text('checking_git_status'))
                self.progress_bar.start()
                
                # 初始化Git管理器
                project_path = self.project_path_var.get()
                self.git_manager = GitManager(project_path)
                
                # 重新初始化路径管理器并更新配置
                compile_tool = self.config.get('compile_tool', 'IAR')
                self.path_manager = PathManagerFactory.create_path_manager(compile_tool, project_path)
                self.config = self.path_manager.auto_find_paths(self.config)
                
                # 从IAR项目文件中提取项目名称
                iar_project_path = self.config.get('project_settings', {}).get('iar_project_path') or self.config.get('iar_project_path')
                if iar_project_path and os.path.exists(iar_project_path):
                    project_name = os.path.splitext(os.path.basename(iar_project_path))[0]
                    self.config['project_name'] = project_name
                    self.log_message(f"检测到项目名称: {project_name}")
                
                # 检查是否为Git仓库
                if not self.git_manager.is_git_repo():
                    self.git_status_var.set("不是Git仓库")
                    self.update_status(self.get_text('not_git_repo_status'))
                    return
                
                # 检查未提交更改
                has_changes = self.git_manager.has_uncommitted_changes()
                if has_changes:
                    self.git_status_var.set("有未提交更改")
                    self.update_status(self.get_text('has_uncommitted_changes'))
                else:
                    self.git_status_var.set("工作区干净")
                    self.update_status(self.get_text('git_workdir_clean'))
                
                # 获取commit信息
                commit_info = self.git_manager.get_commit_info()
                if commit_info['commit_id']:
                    self.log_message(f"当前commit: {commit_info['short_commit_id']}")
                    self.log_message(f"分支: {commit_info['branch']}")
                    self.log_message(f"作者: {commit_info['author']}")
                
                # 设置Git状态检查成功标志位
                self.git_status_checked = True
                self.log_message("Git状态检查完成")
                
            except Exception as e:
                self.log_message(f"检查Git状态失败: {e}")
                self.git_status_var.set("检查失败")
                self.git_status_checked = False
            finally:
                self.progress_bar.stop()
                self.update_status(self.get_text('git_check_complete'))
        
        threading.Thread(target=check_thread, daemon=True).start()
    
    def check_version(self):
        """检查固件版本"""
        def check_thread():
            try:
                self.update_status(self.get_text('checking_firmware_version'))
                self.progress_bar.start()
                
                # 初始化版本管理器和main.c更新器
                project_path = self.project_path_var.get()
                fw_publish_dir = self.config.get('fw_publish_directory', './fw_publish')
                
                # 获取当前git分支
                current_branch = None
                if self.git_manager and self.git_manager.is_git_repo():
                    git_info = self.git_manager.get_commit_info()
                    current_branch = git_info.get('branch')
                    if current_branch:
                        logger.info(f"版本管理器初始化，检测到Git分支: {current_branch}")
                    else:
                        logger.warning("版本管理器初始化，无法获取Git分支信息")
                
                self.version_manager = VersionManager(self.config.get('version_settings', {}), project_path, fw_publish_dir, current_branch)
                # 根据编译工具选择相应的信息管理器
                compile_tool = self.config.get('compile_tool', 'IAR')
                self.info_manager = InfoManagerFactory.create_manager(compile_tool, self.config)
                
                # 从信息文件中读取当前版本
                main_file_path, _ = self.get_info_file_path_with_details(self.project_path_var.get())
                if main_file_path:
                    current_version = self.info_manager.extract_version_from_info_file(main_file_path)
                else:
                    current_version = None
                
                if current_version:
                    self.log_message(f"当前代码版本: {current_version}")
                    
                    # 获取下一个版本号
                    next_version, explanation = self.version_manager.get_next_version(current_version)
                    self.log_message(f"建议下一个版本: {next_version}")
                    self.log_message(explanation)
                    
                    # 更新界面显示
                    self.firmware_version_var.set(f"{current_version} -> {next_version}")
                else:
                    self.log_message("无法从main.c中提取版本号")
                    self.firmware_version_var.set("版本提取失败")
                
                # 更新flash起始地址显示
                self._update_flash_start_addr_display()
                
                # 列出已发布的固件
                published_firmware = self.version_manager.list_published_firmware()
                if published_firmware:
                    self.log_message(f"已发布固件数量: {len(published_firmware)}")
                    for i, fw in enumerate(published_firmware[:5]):  # 只显示前5个
                        self.log_message(f"  {i+1}. {fw['filename']} (版本: {fw['version']})")
                else:
                    self.log_message("没有已发布的固件")
                
                # 设置版本检查成功标志位
                self.version_checked = True
                self.log_message("版本检查完成")
                
            except Exception as e:
                self.log_message(f"检查版本失败: {e}")
                self.firmware_version_var.set("检查失败")
                self.version_checked = False
            finally:
                self.progress_bar.stop()
                self.update_status(self.get_text('version_check_complete'))
        
        threading.Thread(target=check_thread, daemon=True).start()
    
    
    def _check_build_config(self):
        """检查编译配置是否完整"""
        missing_configs = []
        
        self.log_message("开始检查编译配置...")
        
        # 检查编译工具安装路径
        compile_tool = self.config.get('compile_tool', 'IAR')
        if compile_tool == 'IAR':
            tool_path = self.config.get('iar_installation_path', '')
            tool_name = "IAR"
        else:  # MDK
            tool_path = self.config.get('mdk_installation_path', '')
            tool_name = "MDK"
        
        self.log_message(f"{tool_name}路径: {tool_path}")
        if not tool_path:
            missing_configs.append(f"{tool_name}安装路径")
        
        # 检查bin起始地址
        binary_settings = self.config.get('binary_settings', {})
        self.log_message(f"binary_settings配置: {binary_settings}")
        bin_start_address = binary_settings.get('bin_start_address', 0)
        self.log_message(f"检查bin起始地址: 0x{bin_start_address:08X}")
        if bin_start_address == 0:
            missing_configs.append("bin起始地址")
            self.log_message("警告: bin起始地址未设置，这可能导致编译失败")
        
        # 检查编译配置选择
        if not self.selected_configuration:
            missing_configs.append("编译配置选择")
            self.log_message("错误: 未选择编译配置")
        else:
            self.log_message(f"选择的编译配置: {self.selected_configuration.get('name', 'N/A')}")
            self.log_message(f"配置中的bin文件: {self.selected_configuration.get('bin_file', 'N/A')}")
        
        # 检查信息文件
        info_file_name = self.config.get('info_file', '')
        self.log_message(f"信息文件名: {info_file_name}")
        if not info_file_name:
            missing_configs.append("信息文件")
        else:
            # 基于文件名查找完整路径
            project_path = self.config.get('project_path', '')
            self.log_message(f"项目路径: {project_path}")
            if not project_path:
                missing_configs.append("项目路径")
            else:
                # 查找信息文件
                info_file_path, error_msg = self.get_info_file_path_with_details(project_path)
                if info_file_path:
                    self.log_message(f"找到的信息文件路径: {info_file_path}")
                    # 尝试分析配置文件
                    if not self.info_manager:
                        # 根据编译工具创建相应的信息管理器
                        compile_tool = self.config.get('compile_tool', 'IAR')
                        self.info_manager = InfoManagerFactory.create_manager(compile_tool, self.config)
                    
                    try:
                        feature_settings = {
                            'enable_git_commit_id': self.config.get('enable_git_commit_id', True),
                            'enable_file_size': self.config.get('enable_file_size', True),
                            'enable_bin_checksum': self.config.get('enable_bin_checksum', True),
                            'enable_hash_value': self.config.get('enable_hash_value', True),
                            'git_commit_id_keyword': self.config.get('git_commit_id_keyword', '__git_commit_id'),
                            'file_size_keyword': self.config.get('file_size_keyword', '__file_size'),
                            'bin_checksum_keyword': self.config.get('bin_checksum_keyword', '__bin_checksum'),
                            'hash_value_keyword': self.config.get('hash_value_keyword', '__hash_value'),
                            'firmware_version_keyword': self.config.get('firmware_version_keyword', '__Firmware_Version')
                        }
                        binary_config = self.info_manager.analyze_config_file(info_file_path, feature_settings)
                        # 更新配置
                        if 'binary_settings' not in self.config:
                            self.config = {}
                        self.config.update(binary_config)
                        
                        # 检查地址是否已解析
                        missing_fields = []
                        if binary_config.get('firmware_version_offset', 0) == 0:
                            missing_fields.append(f"{feature_settings.get('firmware_version_keyword', '__Firmware_Version')}地址")
                        if binary_config.get('git_commit_id_offset', 0) == 0:
                            missing_fields.append(f"{feature_settings.get('git_commit_id_keyword', '__git_commit_id')}地址")
                        if binary_config.get('file_size_offset', 0) == 0:
                            missing_fields.append(f"{feature_settings.get('file_size_keyword', '__file_size')}地址")
                        if binary_config.get('bin_checksum_offset', 0) == 0:
                            missing_fields.append(f"{feature_settings.get('bin_checksum_keyword', '__bin_checksum')}地址")
                        
                        if missing_fields:
                            missing_configs.extend(missing_fields)
                    except Exception as e:
                        missing_configs.append(f"配置文件分析失败: {e}")
                else:
                    # 显示详细的错误信息
                    self.log_message(error_msg)
                    # 根据错误类型添加不同的错误信息
                    if "找到多个信息文件" in error_msg:
                        missing_configs.append("找到多个信息文件")
                    elif "未找到信息文件" in error_msg:
                        missing_configs.append("未找到信息文件")
                    else:
                        missing_configs.append("信息文件查找失败")
        
        if missing_configs:
            error_msg = f"编译配置不完整，缺少以下配置:\n{', '.join(missing_configs)}\n\n"
            error_msg += "请查看日志输出获取详细错误信息，然后点击'设置'按钮进行配置:\n"
            
            # 根据具体的错误类型提供针对性的建议
            if "找到多个信息文件" in missing_configs:
                error_msg += "1. 删除项目中的重复信息文件，只保留一个\n"
                error_msg += "2. 建议保留源代码目录中的文件，删除构建系统生成的临时文件\n"
                error_msg += "3. 在'项目设置'中指定具体的信息文件路径"
            elif "未找到信息文件" in missing_configs:
                error_msg += "1. 在'项目设置'中选择信息文件（如main.c）\n"
                error_msg += "2. 确保信息文件中包含正确的#pragma location定义"
            else:
                error_msg += "1. 在'项目设置'中配置IAR安装目录和bin起始地址\n"
                error_msg += "2. 在'项目设置'中选择信息文件（如main.c）\n"
                error_msg += "3. 确保信息文件中包含正确的#pragma location定义"
            
            self.log_message(f"配置检查失败: {', '.join(missing_configs)}")
            messagebox.showerror(self.get_text('msg_config_incomplete'), error_msg)
            return False
        
        return True
    
    def _update_flash_start_addr_display(self):
        """更新flash起始地址显示"""
        try:
            # 从配置中获取flash起始地址
            bin_start_address = self.config.get('binary_settings', {}).get('bin_start_address', 0)
            if bin_start_address > 0:
                self.flash_start_addr_var.set(f"0x{bin_start_address:08X}")
                self.log_message(f"Flash起始地址: 0x{bin_start_address:08X}")
            else:
                self.flash_start_addr_var.set("未设置")
                self.log_message("Flash起始地址未设置")
        except Exception as e:
            self.flash_start_addr_var.set("获取失败")
            self.log_message(f"获取Flash起始地址失败: {e}")
    
    
    
    def start_build(self):
        """开始编译流程"""
        def build_thread():
            try:
                
                # 检查配置是否完整
                if not self._check_build_config():
                    return
                
                self.update_status(self.get_text('start_build_process'))
                self.progress_bar.start()
                
                # 1. 检查Git状态（如果用户没有手动检查过）
                if not self.git_status_checked:
                    self.log_message("自动执行Git状态检查...")
                    # 模拟点击Git状态检查按钮
                    self.check_git_status()
                    # 等待Git状态检查完成
                    import time
                    while not self.git_status_checked:
                        time.sleep(0.1)  # 每100ms检查一次
                    self.log_message("Git状态检查完成")
                else:
                    self.log_message("使用已完成的Git状态检查结果")
                
                # 2. 检查版本（如果用户没有手动检查过）
                if not self.version_checked:
                    self.log_message("自动执行版本检查...")
                    # 模拟点击版本检查按钮
                    self.check_version()
                    # 等待版本检查完成
                    import time
                    while not self.version_checked:
                        time.sleep(0.1)  # 每100ms检查一次
                    self.log_message("版本检查完成")
                else:
                    self.log_message("使用已完成的版本检查结果")
                
                # 3. 获取项目路径和初始化管理器
                project_path = self.project_path_var.get()
                
                # 确保Git管理器已初始化
                if not self.git_manager:
                    self.git_manager = GitManager(project_path)
                
                # 确保路径管理器已初始化
                if not self.path_manager:
                    compile_tool = self.config.get('compile_tool', 'IAR')
                    self.path_manager = PathManagerFactory.create_path_manager(compile_tool, project_path)
                    
                self.config = self.path_manager.auto_find_paths(self.config)
                
                # 更新flash起始地址显示
                self._update_flash_start_addr_display()
                
                # 从IAR项目文件中提取项目名称
                iar_project_path = self.config.get('project_settings', {}).get('iar_project_path') or self.config.get('iar_project_path')
                if iar_project_path and os.path.exists(iar_project_path):
                    project_name = os.path.splitext(os.path.basename(iar_project_path))[0]
                    self.config['project_name'] = project_name
                    self.log_message(f"检测到项目名称: {project_name}")
                
                if not self.git_manager.is_git_repo():
                    messagebox.showerror(self.get_text('msg_error'), self.get_text('msg_not_git_repo'))
                    return
                
                # 4. 获取版本信息（使用已检查的结果）
                fw_publish_dir = self.config.get('fw_publish_directory', './fw_publish')
                
                # 获取当前git分支
                current_branch = None
                if self.git_manager and self.git_manager.is_git_repo():
                    git_info = self.git_manager.get_commit_info()
                    current_branch = git_info.get('branch')
                    if current_branch:
                        logger.info(f"编译时检测到Git分支: {current_branch}")
                    else:
                        logger.warning("编译时无法获取Git分支信息")
                
                # 确保版本管理器已初始化
                if not self.version_manager:
                    self.version_manager = VersionManager(self.config.get('version_settings', {}), project_path, fw_publish_dir, current_branch)
                    # 根据编译工具选择相应的信息管理器
                    compile_tool = self.config.get('compile_tool', 'IAR')
                    self.info_manager = InfoManagerFactory.create_manager(compile_tool, self.config)
                
                # 从已检查的结果中获取版本信息
                main_file_path, _ = self.get_info_file_path_with_details(project_path)
                if main_file_path:
                    current_version = self.info_manager.extract_version_from_info_file(main_file_path)
                else:
                    current_version = None
                
                if current_version:
                    next_version, explanation = self.version_manager.get_next_version(current_version)
                    self.log_message(f"当前版本: {current_version}")
                    self.log_message(f"下一个版本: {next_version}")
                    self.log_message(explanation)
                else:
                    next_version = "V0.0.0.1"
                    self.log_message(f"无法提取版本，使用默认版本: {next_version}")
                
                # 更新界面显示
                self.firmware_version_var.set(f"{current_version or '未知'} -> {next_version}")
                
                # 3. 检查是否有未提交的更改并提交
                has_changes = self.git_manager.has_uncommitted_changes()
                commit_message = ""  # 用于存储最终的提交信息
                
                # 总是显示Git提交信息输入弹窗，让用户输入更新信息
                self.update_status(self.get_text('input_update_info'))
                default_message = f"发布{next_version}版本"
                commit_message = self.show_git_commit_dialog(default_message)
                
                if not commit_message:  # 用户取消输入
                    self.log_message("用户取消了更新信息输入")
                    result = messagebox.askyesno("确认", 
                                               "未输入更新信息，是否继续编译？\n建议输入更新信息用于Release Notes。")
                    if not result:
                        return
                    # 如果用户选择继续，使用默认信息
                    commit_message = default_message
                
                # 如果有未提交的更改，进行Git提交
                if has_changes:
                    self.update_status(self.get_text('committing_changes'))
                    self.log_message(f"准备提交: {commit_message}")
                    if self.git_manager.commit_changes(commit_message):
                        self.log_message(f"Git提交成功: {commit_message}")
                    else:
                        self.log_message("Git提交失败，但继续编译流程")
                else:
                    self.log_message("没有未提交的更改，跳过Git提交")
                
                # 4. 如果版本号需要更新，更新信息文件
                version_updated = False
                if current_version and next_version != current_version:
                    self.update_status(self.get_text('updating_version'))
                    main_file_path, error_msg = self.get_info_file_path_with_details(project_path)
                    if main_file_path:
                        success, message = self.info_manager.update_version_in_info_file(main_file_path, next_version)
                    else:
                        success, message = False, f"未找到信息文件\n\n{error_msg}"
                    if success:
                        self.log_message(f"版本号更新成功: {message}")
                        version_updated = True
                    else:
                        self.log_message(f"版本号更新失败: {message}")
                        # 继续使用原版本号
                        next_version = current_version
                
                # 5. 创建或更新Release Note（无论版本号是否更新都执行）
                self.update_status(self.get_text('updating_release_notes'))
                self.create_or_update_release_note(next_version, commit_message)
                
                # 6. 如果有未提交的更改（包括版本号更新和Release Note），再次提交
                if self.git_manager.has_uncommitted_changes():
                    self.update_status(self.get_text('committing_version_changes'))
                    # 使用相同的提交信息，或者如果用户之前取消了，则使用默认信息
                    if not commit_message:
                        commit_message = f"发布{next_version}版本"
                    
                    self.log_message(f"准备提交: {commit_message}")
                    if self.git_manager.commit_changes(commit_message):
                        self.log_message(f"Git提交成功: {commit_message}")
                    else:
                        self.log_message("Git提交失败，但继续编译流程")
                
                # 7. 检查是否还有其他未提交的更改
                has_changes = self.git_manager.has_uncommitted_changes()
                if has_changes:
                    result = messagebox.askyesno("确认", 
                                               "检测到未提交的更改，是否继续编译？\n建议先提交更改。")
                    if not result:
                        return
                
                # 8. 获取commit ID（使用7位短ID，与SourceTree一致）
                commit_id = self.git_manager.get_short_commit_id(7)
                if not commit_id:
                    messagebox.showerror(self.get_text('msg_error'), self.get_text('msg_cannot_get_commit_id'))
                    return
                
                self.log_message(f"使用commit ID: {commit_id}")
                
                # 9. 根据编译工具初始化相应的编译器
                compile_tool = self.config.get('compile_tool', 'IAR')
                self.builder = BuilderFactory.create_builder(compile_tool, self.config, self.selected_configuration)
                
                # 10. 智能编译项目
                self.update_status(self.get_text('compiling_project'))
                # 记录编译开始时间
                compile_start_time = datetime.now()
                # 判断是否只有版本号变化
                # 如果版本号相同，说明没有版本号变化，应该使用增量编译
                # 如果版本号不同，说明有版本号变化，也应该使用增量编译
                # 只有在没有版本号信息时才使用清理编译
                only_version_changed = current_version is not None
                
                # 调用构建器进行智能编译
                success, message = self.builder.smart_build(only_version_changed)
                
                if not success:
                    messagebox.showerror(self.get_text('msg_compile_failed'), message)
                    return
                
                # 获取bin文件信息
                bin_info = self.builder.get_bin_file_info(self.selected_configuration)
                
                if not bin_info['exists']:
                    messagebox.showerror(self.get_text('msg_compile_failed'), self.get_text('msg_compile_success_no_bin'))
                    return
                
                self.log_message("编译成功")
                
                # 11. 修改二进制文件
                self.update_status(self.get_text('modifying_binary'))
                feature_settings = {
                    'enable_git_commit_id': self.config.get('enable_git_commit_id', True),
                    'enable_file_size': self.config.get('enable_file_size', True),
                    'enable_bin_checksum': self.config.get('enable_bin_checksum', True),
                    'enable_hash_value': self.config.get('enable_hash_value', True),
                    'git_commit_id_keyword': self.config.get('git_commit_id_keyword', '__git_commit_id'),
                    'file_size_keyword': self.config.get('file_size_keyword', '__file_size'),
                    'bin_checksum_keyword': self.config.get('bin_checksum_keyword', '__bin_checksum'),
                    'hash_value_keyword': self.config.get('hash_value_keyword', '__hash_value'),
                    'firmware_version_keyword': self.config.get('firmware_version_keyword', '__Firmware_Version')
                }
                self.binary_modifier = BinaryModifier(self.config, feature_settings)
                
                # 记录二进制文件信息
                self.log_message(f"准备修改二进制文件: {bin_info['path']}")
                self.log_message(f"文件大小: {bin_info['size']} 字节")
                self.log_message(f"Commit ID: {commit_id}")
                
                # 获取固件版本
                firmware_version = self.firmware_version_var.get()
                if firmware_version == "未检查":
                    firmware_version = None
                
                success, message, mod_info = self.binary_modifier.modify_binary_file(
                    bin_info['path'], commit_id, firmware_version)
                
                if not success:
                    self.log_message(f"二进制文件修改失败: {message}")
                    messagebox.showerror(self.get_text('msg_modify_failed'), message)
                    return
                
                self.log_message("二进制文件修改成功")
                self.log_message(f"修改详情: {message}")
                
                # 12. 处理文件
                self.update_status(self.get_text('processing_files'))
                compile_tool = self.config.get('compile_tool', 'IAR')
                self.file_manager = FileManagerFactory.create_file_manager(compile_tool, self.config, project_path, self.path_manager)
                
                success, message, file_info = self.file_manager.process_bin_file(
                    bin_info['path'], commit_id, version=next_version)
                
                if not success:
                    messagebox.showerror(self.get_text('msg_file_process_failed'), message)
                    return
                
                self.log_message("文件处理成功")
                
                # 13. 发布固件到fw_publish目录
                self.update_status(self.get_text('publishing_firmware'))
                try:
                    add_timestamp = self.config.get('add_timestamp_to_filename', False)
                    publish_out_file = self.config.get('publish_out_file', False)
                    current_timestamp = datetime.now() if add_timestamp else None
                    success, message, publish_info = self.file_manager.publish_firmware(
                        bin_info['path'], commit_id, next_version, timestamp=current_timestamp, 
                        add_timestamp=add_timestamp, publish_out_file=publish_out_file, 
                        configuration=self.selected_configuration, branch_name=current_branch or "main")
                    
                    if not success:
                        self.log_message(f"固件发布失败: {message}")
                        messagebox.showerror(self.get_text('msg_firmware_publish_failed'), message)
                        return
                    
                    self.log_message("固件发布成功")
                    self.log_message(f"发布详情: {message}")
                    
                    # 14. 发布到远程目录（如果启用了）
                    enable_remote_publish = self.config.get('enable_remote_publish', False)
                    remote_publish_dir = self.config.get('remote_publish_directory', '').strip()
                    self.log_message(f"检查远程发布配置: 启用={enable_remote_publish}, 目录='{remote_publish_dir}'")
                    
                    if enable_remote_publish and remote_publish_dir:
                        self.update_status(self.get_text('publishing_remote'))
                        try:
                            # 获取当前分支名称
                            git_info = self.git_manager.get_commit_info()
                            branch_name = git_info.get('branch')
                            if not branch_name:
                                error_msg = "无法获取Git分支信息，请检查Git仓库状态"
                                logger.error(error_msg)
                                self.log_message(error_msg)
                                return
                            else:
                                logger.info(f"检测到Git分支: {branch_name}")
                                self.log_message(f"当前Git分支: {branch_name}")
                            
                            # 使用重命名后的bin文件路径
                            renamed_bin_path = publish_info.get('destination_path')
                            if not renamed_bin_path or not os.path.exists(renamed_bin_path):
                                self.log_message("重命名后的bin文件不存在，使用原始文件")
                                renamed_bin_path = bin_info['path']
                            
                            # 获取Release Notes文件路径（在项目根目录）
                            project_root = self.project_path_var.get()
                            if not project_root:
                                # 如果没有设置项目路径，使用当前脚本所在目录
                                project_root = os.path.dirname(os.path.abspath(__file__))
                            else:
                                project_root = os.path.abspath(project_root)
                            release_note_path = os.path.join(project_root, "RELEASE_NOTES.md")
                            
                            self.log_message(f"远程发布文件: bin={renamed_bin_path}, release_note={release_note_path}")
                            
                            # 发布到远程目录
                            publish_out_file = self.config.get('publish_out_file', False)
                            remote_success, remote_message, remote_info = self.file_manager.publish_to_remote(
                                renamed_bin_path, release_note_path, branch_name, publish_out_file, 
                                configuration=self.selected_configuration)
                            
                            if remote_success:
                                self.log_message("远程发布成功")
                                self.log_message(f"远程发布详情: {remote_message}")
                            else:
                                self.log_message(f"远程发布失败: {remote_message}")
                                # 远程发布失败不影响主流程，只记录日志
                        except Exception as e:
                            self.log_message(f"远程发布异常: {e}")
                            # 远程发布异常不影响主流程，只记录日志
                    
                except Exception as e:
                    error_msg = f"发布固件时发生异常: {e}"
                    self.log_message(error_msg)
                    messagebox.showerror(self.get_text('msg_firmware_publish_error'), error_msg)
                    return
                
                # 15. 完成
                self.update_status(self.get_text('build_process_complete'))
                # 计算编译时间
                compile_end_time = datetime.now()
                compile_duration = compile_end_time - compile_start_time
                compile_time_str = f"{compile_duration.total_seconds():.1f}秒"
                
                success_message = f"{self.get_text('msg_compile_complete')}\n\n编译时间: {compile_time_str}\n\n{message}"
                messagebox.showinfo(self.get_text('msg_success'), success_message)
                
            except Exception as e:
                self.log_message(f"编译流程异常: {e}")
                messagebox.showerror(self.get_text('msg_error'), f"{self.get_text('msg_compile_exception')}: {e}")
            finally:
                self.progress_bar.stop()
                # 编译完成后重置标志位，准备下一轮循环
                self.git_status_checked = False
                self.version_checked = False
                self.log_message("标志位已重置，准备下一轮编译")
        
        threading.Thread(target=build_thread, daemon=True).start()
    
    
    def open_firmware_directory(self):
        """打开固件发布目录"""
        try:
            fw_publish_dir = self.config.get('fw_publish_directory', './fw_publish')
            
            # 使用与FileManager相同的路径解析逻辑
            project_path = self.project_path_var.get()
            if project_path:
                project_root = os.path.abspath(project_path)
            else:
                # 如果没有提供项目路径，使用工具目录的上级目录作为默认值
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            if os.path.isabs(fw_publish_dir):
                # 如果是绝对路径，直接使用
                fw_publish_dir = os.path.abspath(fw_publish_dir)
            else:
                # 如果是相对路径，基于项目根目录解析
                fw_publish_dir = os.path.join(project_root, fw_publish_dir)
                fw_publish_dir = os.path.abspath(fw_publish_dir)
            
            logger.info(f"尝试打开固件发布目录: {fw_publish_dir}")
            
            if os.path.exists(fw_publish_dir):
                os.startfile(fw_publish_dir)
                logger.info(f"成功打开固件发布目录: {fw_publish_dir}")
            else:
                logger.warning(f"固件发布目录不存在: {fw_publish_dir}")
                # 尝试创建目录
                try:
                    os.makedirs(fw_publish_dir, exist_ok=True)
                    logger.info(f"已创建固件发布目录: {fw_publish_dir}")
                    os.startfile(fw_publish_dir)
                    logger.info(f"成功打开固件发布目录: {fw_publish_dir}")
                except Exception as create_error:
                    logger.error(f"创建固件发布目录失败: {create_error}")
                    messagebox.showwarning(self.get_text('msg_warning'), f"固件发布目录不存在且无法创建:\n{fw_publish_dir}\n\n错误: {create_error}")
        except Exception as e:
            logger.error(f"打开固件发布目录失败: {e}")
            messagebox.showerror(self.get_text('msg_error'), f"{self.get_text('msg_open_firmware_directory_failed')}: {e}")
    
    def open_settings(self):
        """打开设置窗口"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title(self.get_text('settings_title'))
        # 使设置窗口居中
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # 设置设置窗口图标
        try:
            icon_path = os.path.join(self._get_script_dir(), "icon_efm.ico")
            if os.path.exists(icon_path):
                settings_window.iconbitmap(icon_path)
        except Exception as e:
            logger.warning(f"设置设置窗口图标失败: {e}")
        
        # 计算设置窗口位置（跟随主窗口中心）
        self._center_settings_dialog(settings_window)
        
        # 创建主框架
        main_frame = ttk.Frame(settings_window, padding="20")
        main_frame.pack(fill=tk.X, expand=False)
        
        # 设置项列表
        row = 0
        
        # 编译工具选择
        ttk.Label(main_frame, text=self.get_text('compile_tool')).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.settings_compile_tool_var = tk.StringVar(value=self.config.get('compile_tool', 'IAR'))
        compile_tool_combo = ttk.Combobox(main_frame, textvariable=self.settings_compile_tool_var, values=['IAR', 'MDK'], state="readonly", width=32)
        compile_tool_combo.grid(row=row, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        compile_tool_combo.bind('<<ComboboxSelected>>', self.on_compile_tool_changed)
        row += 1
        
        # IAR安装路径
        ttk.Label(main_frame, text=self.get_text('iar_installation_path')).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.settings_iar_path_var = tk.StringVar(value=self.config.get('iar_installation_path', ''))
        ttk.Entry(main_frame, textvariable=self.settings_iar_path_var, state="readonly", width=35).grid(row=row, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        ttk.Button(main_frame, text=self.get_text('select_directory'), command=self.browse_iar_path_settings).grid(row=row, column=2, sticky=tk.W, padx=(10, 0), pady=5)
        row += 1
        
        # MDK安装路径
        ttk.Label(main_frame, text=self.get_text('mdk_installation_path')).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.settings_mdk_path_var = tk.StringVar(value=self.config.get('mdk_installation_path', ''))
        ttk.Entry(main_frame, textvariable=self.settings_mdk_path_var, state="readonly", width=35).grid(row=row, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        ttk.Button(main_frame, text=self.get_text('select_directory'), command=self.browse_mdk_path_settings).grid(row=row, column=2, sticky=tk.W, padx=(10, 0), pady=5)
        row += 1
        
        # 固件发布目录
        ttk.Label(main_frame, text=self.get_text('fw_publish_directory')).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.settings_fw_publish_dir_var = tk.StringVar(value=self.config.get('fw_publish_directory', './fw_publish'))
        ttk.Entry(main_frame, textvariable=self.settings_fw_publish_dir_var, width=35).grid(row=row, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        ttk.Button(main_frame, text=self.get_text('select_directory'), command=self.browse_fw_publish_dir_settings).grid(row=row, column=2, sticky=tk.W, padx=(10, 0), pady=5)
        row += 1
        
        # 远程发布开关
        self.settings_enable_remote_publish_var = tk.BooleanVar(value=self.config.get('enable_remote_publish', False))
        ttk.Checkbutton(main_frame, text=self.get_text('enable_remote_publish'), variable=self.settings_enable_remote_publish_var, command=self.on_remote_publish_toggle).grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=5)
        row += 1
        
        # 远程发布目录
        ttk.Label(main_frame, text=self.get_text('remote_publish_directory')).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.settings_remote_publish_dir_var = tk.StringVar(value=self.config.get('remote_publish_directory', ''))
        self.settings_remote_publish_dir_entry = ttk.Entry(main_frame, textvariable=self.settings_remote_publish_dir_var, width=35)
        self.settings_remote_publish_dir_entry.grid(row=row, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        self.settings_remote_publish_dir_button = ttk.Button(main_frame, text=self.get_text('select_directory'), command=self.browse_remote_publish_dir_settings)
        self.settings_remote_publish_dir_button.grid(row=row, column=2, sticky=tk.W, padx=(10, 0), pady=5)
        row += 1
        
        # 初始化远程发布目录控件的状态
        self.update_remote_publish_controls_state()
        
        # 配置文件路径
        ttk.Label(main_frame, text=self.get_text('config_file')).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.settings_config_file_var = tk.StringVar(value=self.config.get('info_file', ''))
        ttk.Entry(main_frame, textvariable=self.settings_config_file_var, state="readonly", width=35).grid(row=row, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        ttk.Button(main_frame, text=self.get_text('select'), command=self.browse_config_file_settings).grid(row=row, column=2, sticky=tk.W, padx=(10, 0), pady=5)
        row += 1
        
        # bin文件名添加时间戳和发布.out文件（同一行）
        self.settings_add_timestamp_var = tk.BooleanVar(value=self.config.get('add_timestamp_to_filename', False))
        ttk.Checkbutton(main_frame, text=self.get_text('add_timestamp_to_filename'), variable=self.settings_add_timestamp_var).grid(row=row, column=0, sticky=tk.W, pady=5)
        
        self.settings_publish_out_file_var = tk.BooleanVar(value=self.config.get('publish_out_file', False))
        ttk.Checkbutton(main_frame, text=self.get_text('publish_out_file'), variable=self.settings_publish_out_file_var).grid(row=row, column=1, sticky=tk.W, padx=(20, 0), pady=5)
        row += 1
        
        # 固件版本变量名称（永远开启）
        ttk.Label(main_frame, text=self.get_text('firmware_version_keyword')).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.settings_firmware_version_keyword_var = tk.StringVar(value=self.config.get('firmware_version_keyword', '__Firmware_Version'))
        ttk.Entry(main_frame, textvariable=self.settings_firmware_version_keyword_var, width=20).grid(row=row, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        row += 1
        
        # Git提交ID变量名称
        ttk.Label(main_frame, text=self.get_text('git_commit_id_keyword')).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.settings_git_commit_id_keyword_var = tk.StringVar(value=self.config.get('git_commit_id_keyword', '__git_commit_id'))
        ttk.Entry(main_frame, textvariable=self.settings_git_commit_id_keyword_var, width=20).grid(row=row, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        self.settings_enable_git_commit_id_var = tk.BooleanVar(value=self.config.get('enable_git_commit_id', True))
        self.git_commit_id_checkbox = ttk.Checkbutton(main_frame, text=self.get_text('enabled'), variable=self.settings_enable_git_commit_id_var, command=lambda: self.update_checkbox_text(self.git_commit_id_checkbox, self.settings_enable_git_commit_id_var))
        self.git_commit_id_checkbox.grid(row=row, column=2, sticky=tk.W, padx=(10, 0), pady=5)
        row += 1
        
        # 文件大小变量名称
        ttk.Label(main_frame, text=self.get_text('file_size_keyword')).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.settings_file_size_keyword_var = tk.StringVar(value=self.config.get('file_size_keyword', '__file_size'))
        ttk.Entry(main_frame, textvariable=self.settings_file_size_keyword_var, width=20).grid(row=row, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        self.settings_enable_file_size_var = tk.BooleanVar(value=self.config.get('enable_file_size', True))
        self.file_size_checkbox = ttk.Checkbutton(main_frame, text=self.get_text('enabled'), variable=self.settings_enable_file_size_var, command=lambda: self.update_checkbox_text(self.file_size_checkbox, self.settings_enable_file_size_var))
        self.file_size_checkbox.grid(row=row, column=2, sticky=tk.W, padx=(10, 0), pady=5)
        row += 1
        
        # 二进制校验和变量名称
        ttk.Label(main_frame, text=self.get_text('bin_checksum_keyword')).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.settings_bin_checksum_keyword_var = tk.StringVar(value=self.config.get('bin_checksum_keyword', '__bin_checksum'))
        ttk.Entry(main_frame, textvariable=self.settings_bin_checksum_keyword_var, width=20).grid(row=row, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        self.settings_enable_bin_checksum_var = tk.BooleanVar(value=self.config.get('enable_bin_checksum', True))
        self.bin_checksum_checkbox = ttk.Checkbutton(main_frame, text=self.get_text('enabled'), variable=self.settings_enable_bin_checksum_var, command=lambda: self.update_checkbox_text(self.bin_checksum_checkbox, self.settings_enable_bin_checksum_var))
        self.bin_checksum_checkbox.grid(row=row, column=2, sticky=tk.W, padx=(10, 0), pady=5)
        row += 1
        
        # 哈希校验和功能开关和变量名称
        ttk.Label(main_frame, text=self.get_text('hash_value_keyword')).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.settings_hash_value_keyword_var = tk.StringVar(value=self.config.get('hash_value_keyword', '__hash_value'))
        ttk.Entry(main_frame, textvariable=self.settings_hash_value_keyword_var, width=20).grid(row=row, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        self.settings_enable_hash_value_var = tk.BooleanVar(value=self.config.get('enable_hash_value', True))
        self.hash_value_checkbox = ttk.Checkbutton(main_frame, text=self.get_text('enabled'), variable=self.settings_enable_hash_value_var, command=lambda: self.update_checkbox_text(self.hash_value_checkbox, self.settings_enable_hash_value_var))
        self.hash_value_checkbox.grid(row=row, column=2, sticky=tk.W, padx=(10, 0), pady=5)
        row += 1
        
        # 说明文本
        ttk.Label(main_frame, text=self.get_text('bin_address_auto_note'), foreground="gray").grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
        row += 1
        
        # 语言设置单独一行
        ttk.Label(main_frame, text=self.get_text('language')).grid(row=row, column=0, sticky=tk.W, pady=5)
        
        # 创建语言选项列表，显示友好的文本
        language_options = []
        current_display_text = ""
        for lang_code, lang_display in self.get_text('language_options').items():
            display_text = lang_display  # 直接使用显示文本，不重复语言代码
            language_options.append(display_text)
            if lang_code == self.current_language:
                current_display_text = display_text
        
        self.settings_language_var = tk.StringVar(value=current_display_text)
        language_combo = ttk.Combobox(main_frame, textvariable=self.settings_language_var, 
                                    values=language_options, state="readonly", width=15)
        language_combo.grid(row=row, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        language_combo.bind('<<ComboboxSelected>>', lambda e: self.on_language_changed(settings_window))
        row += 1
        
        # 取消和保存按钮单独一行（取消在列1右对齐，保存在列2，与上面的选择按钮对齐）
        ttk.Button(main_frame, text=self.get_text('cancel'), command=settings_window.destroy).grid(row=row, column=1, sticky=tk.E, padx=(10, 0), pady=5)
        ttk.Button(main_frame, text=self.get_text('save'), command=lambda: self.save_settings(settings_window)).grid(row=row, column=2, sticky=tk.W, padx=(5, 0), pady=5)
        
        # 初始化勾选框文本
        self.update_checkbox_text(self.git_commit_id_checkbox, self.settings_enable_git_commit_id_var)
        self.update_checkbox_text(self.file_size_checkbox, self.settings_enable_file_size_var)
        self.update_checkbox_text(self.bin_checksum_checkbox, self.settings_enable_bin_checksum_var)
        self.update_checkbox_text(self.hash_value_checkbox, self.settings_enable_hash_value_var)
        
        # 让窗口根据内容自动调整大小
        settings_window.update_idletasks()
        settings_window.resizable(False, False)
    
    def update_checkbox_text(self, checkbox, var):
        """更新勾选框的文本显示"""
        if var.get():
            checkbox.config(text=self.get_text('enabled'))
        else:
            checkbox.config(text=self.get_text('disabled'))
    
    def on_language_changed(self, settings_window):
        """语言切换回调函数"""
        selected_display_text = self.settings_language_var.get()
        # 根据显示文本找到对应的语言代码
        new_language = None
        for lang_code, lang_display in self.get_text('language_options').items():
            if lang_display == selected_display_text:
                new_language = lang_code
                break
        
        if new_language and new_language != self.current_language:
            self.set_language(new_language)
            
            # 让窗口根据内容自动调整大小
            settings_window.update_idletasks()
            
            # 重新创建整个界面以应用新语言
            settings_window.destroy()
            self.refresh_ui()
            self.open_settings()
            # 重新更新勾选框文本
            if hasattr(self, 'git_commit_id_checkbox'):
                self.update_checkbox_text(self.git_commit_id_checkbox, self.settings_enable_git_commit_id_var)
                self.update_checkbox_text(self.file_size_checkbox, self.settings_enable_file_size_var)
                self.update_checkbox_text(self.bin_checksum_checkbox, self.settings_enable_bin_checksum_var)
                self.update_checkbox_text(self.hash_value_checkbox, self.settings_enable_hash_value_var)
    
    def refresh_ui(self):
        """刷新UI界面"""
        # 更新窗口标题
        self.root.title(f"{self.get_text('app_title')} v{VERSION}")
        
        # 重新创建所有组件
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.create_widgets()
        self._load_user_config_to_ui()
    
    def browse_config_file_settings(self):
        """在设置窗口中浏览配置文件"""
        try:
            # 获取当前配置文件路径作为初始目录
            current_config = self.settings_config_file_var.get()
            if current_config and os.path.exists(current_config):
                initial_dir = os.path.dirname(current_config)
            else:
                # 尝试从项目路径开始查找
                project_path = self.config.get('project_path', '')
                initial_dir = project_path if project_path and os.path.exists(project_path) else os.path.dirname(os.path.abspath(__file__))
            
            self.log_message(f"配置文件对话框初始目录: {initial_dir}")
            
            file_path = filedialog.askopenfilename(
                title="选择配置文件",
                filetypes=[
                    ("C/C++源文件", "*.c;*.cpp;*.cc;*.cxx"),
                    ("C/C++头文件", "*.h;*.hpp;*.hxx"),
                    ("C文件", "*.c"),
                    ("C++文件", "*.cpp;*.cc;*.cxx"),
                    ("头文件", "*.h;*.hpp;*.hxx"),
                    ("所有文件", "*.*")
                ],
                initialdir=initial_dir
            )
            if file_path:
                self.settings_config_file_var.set(file_path)
                self.log_message(f"选择配置文件: {file_path}")
            else:
                self.log_message("用户取消了文件选择")
        except Exception as e:
            self.log_message(f"选择配置文件时出错: {e}")
            messagebox.showerror(self.get_text('msg_error'), f"{self.get_text('msg_select_config_file_error')}: {e}")
    
    def browse_iar_path_settings(self):
        """在设置窗口中浏览IAR安装路径"""
        try:
            # 获取当前IAR路径作为初始目录
            current_iar = self.settings_iar_path_var.get()
            if current_iar and os.path.exists(current_iar):
                initial_dir = os.path.dirname(current_iar)
            else:
                # 使用常见的IAR安装路径
                common_paths = [
                    "C:/Program Files (x86)/IAR Systems",
                    "C:/Program Files/IAR Systems",
                    "D:/Program Files (x86)/IAR Systems",
                    "D:/Program Files/IAR Systems"
                ]
                initial_dir = None
                for path in common_paths:
                    if os.path.exists(path):
                        initial_dir = path
                        break
                if not initial_dir:
                    initial_dir = "C:/Program Files (x86)"
            
            self.log_message(f"IAR路径对话框初始目录: {initial_dir}")
            
            directory = filedialog.askdirectory(
                title="选择IAR安装目录",
                initialdir=initial_dir
            )
            if directory:
                # 查找IAR可执行文件
                iar_exe = self.find_iar_executable(directory)
                if iar_exe:
                    self.settings_iar_path_var.set(iar_exe)
                    self.log_message(f"找到IAR可执行文件: {iar_exe}")
                else:
                    self.settings_iar_path_var.set(directory)
                    self.log_message(f"选择IAR目录: {directory}")
            else:
                self.log_message("用户取消了目录选择")
        except Exception as e:
            self.log_message(f"选择IAR目录时出错: {e}")
            messagebox.showerror(self.get_text('msg_error'), f"{self.get_text('msg_select_iar_directory_error')}: {e}")
    
    def browse_mdk_path_settings(self):
        """在设置窗口中浏览MDK安装路径"""
        try:
            # 获取当前MDK路径作为初始目录
            current_mdk = self.settings_mdk_path_var.get()
            if current_mdk and os.path.exists(current_mdk):
                initial_dir = os.path.dirname(current_mdk)
            else:
                # 使用常见的MDK安装路径
                common_paths = [
                    "C:/Keil_v5",
                    "C:/Program Files (x86)/Keil_v5",
                    "C:/Program Files/Keil_v5",
                    "D:/Keil_v5",
                    "D:/Program Files (x86)/Keil_v5",
                    "D:/Program Files/Keil_v5"
                ]
                initial_dir = None
                for path in common_paths:
                    if os.path.exists(path):
                        initial_dir = path
                        break
                if not initial_dir:
                    initial_dir = "C:/Program Files (x86)"
            
            self.log_message(f"MDK路径对话框初始目录: {initial_dir}")
            
            directory = filedialog.askdirectory(
                title="选择MDK安装目录",
                initialdir=initial_dir
            )
            if directory:
                # 直接设置MDK安装目录路径
                self.settings_mdk_path_var.set(directory)
                self.log_message(f"选择MDK目录: {directory}")
            else:
                self.log_message("用户取消了目录选择")
        except Exception as e:
            self.log_message(f"选择MDK目录时出错: {e}")
            messagebox.showerror(self.get_text('msg_error'), f"选择MDK目录时出错: {e}")
    
    def browse_fw_publish_dir_settings(self):
        """浏览固件发布目录设置"""
        directory = filedialog.askdirectory(title=self.get_text('select_directory'))
        if directory:
            self.settings_fw_publish_dir_var.set(directory)
    
    def browse_remote_publish_dir_settings(self):
        """浏览远程发布目录设置"""
        directory = filedialog.askdirectory(title=self.get_text('select_directory'))
        if directory:
            self.settings_remote_publish_dir_var.set(directory)
    
    def auto_get_flash_address(self):
        """自动获取flash偏移地址"""
        try:
            self.log_message("正在从IAR项目文件自动获取flash偏移地址...")
            
            # 使用PathManager获取flash偏移地址
            flash_offset = self.path_manager.get_flash_offset_from_configuration(self.selected_configuration)
            
            if flash_offset:
                # 更新界面显示
                self.settings_bin_start_address_var.set(f"0x{flash_offset:X}")
                self.log_message(f"自动获取flash偏移地址成功: 0x{flash_offset:X}")
                messagebox.showinfo(self.get_text('msg_success'), f"自动获取flash偏移地址成功: 0x{flash_offset:X}")
            else:
                self.log_message("自动获取flash偏移地址失败")
                messagebox.showwarning(self.get_text('msg_warning'), "无法自动获取flash偏移地址，请检查IAR项目文件和ICF文件")
                
        except Exception as e:
            self.log_message(f"自动获取flash偏移地址异常: {e}")
            messagebox.showerror(self.get_text('msg_error'), f"自动获取flash偏移地址失败: {e}")
    
    def on_remote_publish_toggle(self):
        """远程发布开关切换事件"""
        self.update_remote_publish_controls_state()
    
    def on_compile_tool_changed(self, event=None):
        """编译工具切换事件"""
        compile_tool = self.settings_compile_tool_var.get()
        self.log_message(f"编译工具切换为: {compile_tool}")
        
        # 更新配置中的编译工具
        self.config['compile_tool'] = compile_tool
        
        # 重新创建路径管理器和信息管理器
        project_path = self.config.get('project_path', '')
        if project_path:
            self.log_message(f"重新创建管理器，项目路径: {project_path}")
            self.path_manager = PathManagerFactory.create_path_manager(compile_tool, project_path)
            self.info_manager = InfoManagerFactory.create_manager(compile_tool, self.config)
            self.log_message(f"已重新创建{compile_tool}管理器")
        else:
            self.log_message("项目路径未设置，无法重新创建管理器")
        
        # 根据选择的编译工具更新相关控件的状态
        if compile_tool == 'IAR':
            # 显示IAR路径
            self.settings_iar_path_var.set(self.config.get('iar_installation_path', ''))
            # 更新主界面路径显示
            iar_path = self.config.get('iar_installation_path', '')
            if iar_path:
                self.iar_path_display_var.set(iar_path)
            else:
                self.iar_path_display_var.set("未配置")
        elif compile_tool == 'MDK':
            # 显示MDK路径
            self.settings_mdk_path_var.set(self.config.get('mdk_installation_path', ''))
            # 更新主界面路径显示
            mdk_path = self.config.get('mdk_installation_path', '')
            if mdk_path:
                self.iar_path_display_var.set(mdk_path)
            else:
                self.iar_path_display_var.set("未配置")
    
    def update_remote_publish_controls_state(self):
        """更新远程发布目录控件的启用状态"""
        enabled = self.settings_enable_remote_publish_var.get()
        state = 'normal' if enabled else 'disabled'
        
        self.settings_remote_publish_dir_entry.config(state=state)
        self.settings_remote_publish_dir_button.config(state=state)
    
    def save_settings(self, settings_window):
        """保存设置"""
        try:
            # 更新配置
            self.config['compile_tool'] = self.settings_compile_tool_var.get()
            self.config['iar_installation_path'] = self.settings_iar_path_var.get()
            self.config['mdk_installation_path'] = self.settings_mdk_path_var.get()
            self.config['fw_publish_directory'] = self.settings_fw_publish_dir_var.get()
            self.config['remote_publish_directory'] = self.settings_remote_publish_dir_var.get()
            self.config['enable_remote_publish'] = self.settings_enable_remote_publish_var.get()
            
            # 更新功能设置
            self.config['enable_git_commit_id'] = self.settings_enable_git_commit_id_var.get()
            self.config['enable_file_size'] = self.settings_enable_file_size_var.get()
            self.config['enable_bin_checksum'] = self.settings_enable_bin_checksum_var.get()
            self.config['enable_hash_value'] = self.settings_enable_hash_value_var.get()
            self.config['git_commit_id_keyword'] = self.settings_git_commit_id_keyword_var.get()
            self.config['file_size_keyword'] = self.settings_file_size_keyword_var.get()
            self.config['bin_checksum_keyword'] = self.settings_bin_checksum_keyword_var.get()
            self.config['hash_value_keyword'] = self.settings_hash_value_keyword_var.get()
            self.config['firmware_version_keyword'] = self.settings_firmware_version_keyword_var.get()
            self.config['add_timestamp_to_filename'] = self.settings_add_timestamp_var.get()
            self.config['publish_out_file'] = self.settings_publish_out_file_var.get()
            
            # 保存语言设置到user_config.json
            if hasattr(self, 'settings_language_var'):
                self.set_language(self.settings_language_var.get())
            
            # 保存信息文件文件名（只存储文件名，不存储路径）
            info_file_path = self.settings_config_file_var.get()
            if info_file_path:
                info_file_name = os.path.basename(info_file_path)
                self.config['info_file'] = info_file_name
            
            # 创建用户配置
            user_config = {
                "compile_tool": self.config.get('compile_tool', 'IAR'),
                "iar_installation_path": self.config.get('iar_installation_path', ''),
                "mdk_installation_path": self.config.get('mdk_installation_path', ''),
                "project_path": self.config.get('project_path', ''),
                "fw_publish_directory": self.config.get('fw_publish_directory', './fw_publish'),
                "remote_publish_directory": self.config.get('remote_publish_directory', ''),
                "enable_remote_publish": self.config.get('enable_remote_publish', False),
                "info_file": self.config.get('info_file', ''),
                "language": self.current_language,
                "enable_git_commit_id": self.config.get('enable_git_commit_id', True),
                "enable_file_size": self.config.get('enable_file_size', True),
                "enable_bin_checksum": self.config.get('enable_bin_checksum', True),
                "enable_hash_value": self.config.get('enable_hash_value', True),
                "git_commit_id_keyword": self.config.get('git_commit_id_keyword', '__git_commit_id'),
                "file_size_keyword": self.config.get('file_size_keyword', '__file_size'),
                "bin_checksum_keyword": self.config.get('bin_checksum_keyword', '__bin_checksum'),
                "hash_value_keyword": self.config.get('hash_value_keyword', '__hash_value'),
                "firmware_version_keyword": self.config.get('firmware_version_keyword', '__Firmware_Version'),
                "add_timestamp_to_filename": self.config.get('add_timestamp_to_filename', True),
                "publish_out_file": self.config.get('publish_out_file', False)
            }
            
            # 保存到用户配置文件
            script_dir = self._get_script_dir()
            user_config_path = os.path.join(script_dir, "user_config.json")
            with open(user_config_path, 'w', encoding='utf-8') as f:
                json.dump(user_config, f, indent=4, ensure_ascii=False)
            
            # 更新主界面的编译工具路径显示
            compile_tool = self.config.get('compile_tool', 'IAR')
            if compile_tool == 'IAR':
                tool_path = self.config.get('iar_installation_path', '')
            else:  # MDK
                tool_path = self.config.get('mdk_installation_path', '')
            
            if tool_path:
                self.iar_path_display_var.set(tool_path)
            else:
                self.iar_path_display_var.set("未配置")
            
            self.log_message("设置已保存")
            messagebox.showinfo(self.get_text('msg_settings_saved'), self.get_text('msg_settings_saved'))
            settings_window.destroy()
            
        except Exception as e:
            messagebox.showerror(self.get_text('msg_error'), f"保存设置失败: {e}")
    
    def show_git_commit_dialog(self, default_message: str = "") -> str:
        """
        显示Git提交信息输入弹窗
        
        Args:
            default_message: 默认提交信息
            
        Returns:
            str: 用户输入的提交信息，如果取消则返回空字符串
        """
        # 创建弹窗
        dialog = tk.Toplevel(self.root)
        dialog.title(self.get_text('git_commit_dialog_title'))
        dialog.geometry("500x300")
        dialog.resizable(True, True)
        
        # 设置对话框图标
        try:
            icon_path = os.path.join(self._get_script_dir(), "icon_efm.ico")
            if os.path.exists(icon_path):
                dialog.iconbitmap(icon_path)
        except Exception as e:
            logger.warning(f"设置对话框图标失败: {e}")
        
        # 使弹窗居中并跟随主窗口
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 计算对话框位置（跟随主窗口中心）
        self._center_dialog(dialog)
        
        # 创建主框架
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 说明文本
        message_label = ttk.Label(main_frame, text=self.get_text('git_commit_dialog_message'))
        message_label.pack(anchor=tk.W, pady=(0, 10))
        
        # 文本输入框
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        text_widget = scrolledtext.ScrolledText(text_frame, height=8, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # 设置占位符文本（不显示默认信息）
        text_widget.insert(tk.END, self.get_text('git_commit_dialog_placeholder'))
        # 选中占位符文本，方便用户直接输入
        text_widget.tag_add(tk.SEL, "1.0", tk.END)
        text_widget.mark_set(tk.INSERT, "1.0")
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # 结果变量
        result = {"message": ""}
        
        def on_ok():
            """确定按钮回调"""
            user_input = text_widget.get("1.0", tk.END).strip()
            # 如果用户没有输入内容或只输入了占位符，使用默认消息
            if not user_input or user_input == self.get_text('git_commit_dialog_placeholder'):
                message = default_message
            else:
                # 在用户输入前添加"发布xxxx版本"前缀
                message = f"{default_message} - {user_input}"
            result["message"] = message
            dialog.destroy()
        
        def on_cancel():
            """取消按钮回调"""
            result["message"] = ""
            dialog.destroy()
        
        # 按钮
        ttk.Button(button_frame, text=self.get_text('git_commit_dialog_ok'), 
                  command=on_ok).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text=self.get_text('git_commit_dialog_cancel'), 
                  command=on_cancel).pack(side=tk.RIGHT)
        
        # 绑定快捷键
        # Ctrl+Enter 确认
        text_widget.bind('<Control-Return>', lambda e: on_ok())
        # Escape 取消
        dialog.bind('<Escape>', lambda e: on_cancel())
        # 注意：不绑定单独的Return键，让它在文本框中作为换行使用
        
        # 设置焦点到文本输入框
        text_widget.focus_set()
        
        # 等待弹窗关闭
        dialog.wait_window()
        
        return result["message"]
    
    def _center_dialog(self, dialog):
        """
        将对话框居中显示，跟随主窗口位置
        
        Args:
            dialog: 要居中的对话框
        """
        def center_dialog():
            """延迟居中对话框，确保主窗口位置已更新"""
            try:
                # 强制更新主窗口和对话框
                self.root.update_idletasks()
                dialog.update_idletasks()
                
                # 获取主窗口位置和尺寸
                main_x = self.root.winfo_x()
                main_y = self.root.winfo_y()
                main_width = self.root.winfo_width()
                main_height = self.root.winfo_height()
                
                # 如果主窗口尺寸为0，使用默认值
                if main_width <= 1:
                    main_width = 800
                if main_height <= 1:
                    main_height = 600
                
                # 对话框尺寸
                dialog_width, dialog_height = 500, 300
                
                # 计算居中位置
                center_x = main_x + (main_width - dialog_width) // 2
                center_y = main_y + (main_height - dialog_height) // 2
                
                # 确保对话框不会超出屏幕边界
                screen_width = dialog.winfo_screenwidth()
                screen_height = dialog.winfo_screenheight()
                
                # 对于多显示器环境，使用更宽松的边界检查
                # 允许对话框出现在主窗口所在的显示器上
                min_x = min(0, main_x - 100)  # 允许稍微超出左边界
                max_x = max(screen_width, main_x + main_width + 100)  # 允许超出右边界
                min_y = min(0, main_y - 100)  # 允许稍微超出上边界
                max_y = max(screen_height, main_y + main_height + 100)  # 允许超出下边界
                
                # 限制在合理的屏幕范围内
                center_x = max(min_x, min(center_x, max_x - dialog_width))
                center_y = max(min_y, min(center_y, max_y - dialog_height))
                
                # 设置对话框位置
                dialog.geometry(f"{dialog_width}x{dialog_height}+{center_x}+{center_y}")
                
            except Exception as e:
                # 如果计算失败，使用默认居中
                self.log_message(f"对话框居中计算失败: {e}")
                dialog.geometry("500x300+100+100")
        
        # 立即执行一次，然后延迟执行确保位置正确
        center_dialog()
        dialog.after(100, center_dialog)
    
    def _center_settings_dialog(self, dialog):
        """
        将设置对话框居中显示，跟随主窗口位置
        
        Args:
            dialog: 要居中的设置对话框
        """
        def center_dialog():
            """延迟居中设置对话框，确保主窗口位置已更新"""
            try:
                # 强制更新主窗口和对话框
                self.root.update_idletasks()
                dialog.update_idletasks()
                
                # 获取主窗口位置和尺寸
                main_x = self.root.winfo_x()
                main_y = self.root.winfo_y()
                main_width = self.root.winfo_width()
                main_height = self.root.winfo_height()
                
                # 如果主窗口尺寸为0，使用默认值
                if main_width <= 1:
                    main_width = 800
                if main_height <= 1:
                    main_height = 600
                
                # 获取对话框的实际尺寸
                dialog.update_idletasks()
                dialog_width = dialog.winfo_reqwidth()
                dialog_height = dialog.winfo_reqheight()
                
                # 计算居中位置
                center_x = main_x + (main_width - dialog_width) // 2
                center_y = main_y + (main_height - dialog_height) // 2
                
                # 确保对话框不会超出屏幕边界
                screen_width = dialog.winfo_screenwidth()
                screen_height = dialog.winfo_screenheight()
                
                # 对于多显示器环境，使用更宽松的边界检查
                # 允许对话框出现在主窗口所在的显示器上
                min_x = min(0, main_x - 100)  # 允许稍微超出左边界
                max_x = max(screen_width, main_x + main_width + 100)  # 允许超出右边界
                min_y = min(0, main_y - 100)  # 允许稍微超出上边界
                max_y = max(screen_height, main_y + main_height + 100)  # 允许超出下边界
                
                # 限制在合理的屏幕范围内
                center_x = max(min_x, min(center_x, max_x - dialog_width))
                center_y = max(min_y, min(center_y, max_y - dialog_height))
                
                # 设置对话框位置
                dialog.geometry(f"{dialog_width}x{dialog_height}+{center_x}+{center_y}")
                
            except Exception as e:
                # 如果计算失败，使用默认居中
                self.log_message(f"设置对话框居中计算失败: {e}")
                dialog.geometry("600x500+100+100")
        
        # 立即执行一次，然后延迟执行确保位置正确
        center_dialog()
        dialog.after(100, center_dialog)
    
    def _format_changes_for_release_note(self, commit_message: str) -> str:
        """
        格式化用户输入的更新信息，以分号或句号为界换行
        
        Args:
            commit_message: 原始提交信息
            
        Returns:
            str: 格式化后的文本
        """
        try:
            # 移除可能的前缀（如"发布V1.0.0.1版本 - "）
            if " - " in commit_message:
                # 提取用户实际输入的部分
                user_input = commit_message.split(" - ", 1)[1]
            else:
                user_input = commit_message
            
            # 按分号和句号分割文本
            import re
            # 使用正则表达式分割，支持中英文标点符号
            sentences = re.split(r'[;；。.]', user_input)
            
            # 过滤空字符串并去除首尾空格
            sentences = [s.strip() for s in sentences if s.strip()]
            
            # 如果只有一个句子，直接返回
            if len(sentences) <= 1:
                return f"- {user_input}"
            
            # 多个句子，每个句子一行，添加项目符号
            formatted_lines = []
            for sentence in sentences:
                if sentence:  # 确保句子不为空
                    formatted_lines.append(f"- {sentence}")
            
            return "\n".join(formatted_lines)
            
        except Exception as e:
            # 如果格式化失败，返回原始文本
            self.log_message(f"格式化更新信息失败: {e}")
            return f"- {commit_message}"
    
    def create_or_update_release_note(self, version: str, commit_message: str, 
                                    timestamp: datetime = None) -> bool:
        """
        创建或更新release note文件
        
        Args:
            version: 版本号
            commit_message: 提交信息
            timestamp: 时间戳，如果为None则使用当前时间
            
        Returns:
            bool: 是否成功
        """
        try:
            if timestamp is None:
                timestamp = datetime.now()
            
            # 获取项目根目录
            project_root = self.project_path_var.get()
            if not project_root:
                # 如果没有设置项目路径，使用当前脚本所在目录
                project_root = os.path.dirname(os.path.abspath(__file__))
            else:
                project_root = os.path.abspath(project_root)
            
            # release note文件路径（放在项目主目录）
            release_note_path = os.path.join(project_root, "RELEASE_NOTES.md")
            
            # 检查文件是否存在
            file_exists = os.path.exists(release_note_path)
            
            # 准备新的条目
            new_entry = f"## {version} - {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            # 格式化用户输入的更新信息，以分号或句号为界换行
            formatted_changes = self._format_changes_for_release_note(commit_message)
            new_entry += f"**Changes:**\n{formatted_changes}\n\n"
            
            if file_exists:
                # 读取现有内容
                with open(release_note_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 在文件开头插入新条目
                if content.strip():
                    content = new_entry + content
                else:
                    content = new_entry
                
                # 写入更新后的内容
                with open(release_note_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.log_message(self.get_text('release_note_updated'))
            else:
                # 创建新文件
                header = f"# {self.get_text('release_note_title')}\n\n"
                header += "本文档记录了固件版本的更新历史。\n\n"
                header += "---\n\n"
                
                content = header + new_entry
                
                with open(release_note_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.log_message(self.get_text('release_note_created'))
            
            self.log_message(f"Release note文件路径: {release_note_path}")
            return True
            
        except Exception as e:
            self.log_message(f"创建/更新release note失败: {e}")
            return False
    
    def on_closing(self):
        """关闭应用程序"""
        logger.info("应用程序关闭")
        self.root.destroy()
    
    def run(self):
        """运行应用程序"""
        self.log_message("MCU自动编译工具启动")
        self.root.mainloop()
    
    def refresh_configurations(self):
        """刷新编译配置列表"""
        try:
            project_path = self.project_path_var.get()
            if not project_path or not os.path.exists(project_path):
                self.log_message(self.get_text('invalid_project_path'))
                return
            
            # 根据编译工具选择相应的项目分析器
            compile_tool = self.config.get('compile_tool', 'IAR')
            
            # 根据编译工具查找相应的项目文件
            file_extension = ProjectAnalyzerFactory.get_file_extension(compile_tool)
            project_files = []
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    if file.endswith(file_extension):
                        project_files.append(os.path.join(root, file))
            
            if not project_files:
                self.log_message(f"未找到{compile_tool}项目文件({file_extension})")
                self.available_configurations = []
                self.configuration_combo['values'] = []
                self.configuration_var.set("未找到项目文件")
                return
            
            # 解析第一个项目文件（通常只有一个）
            project_file = project_files[0]
            analyzer = ProjectAnalyzerFactory.create_analyzer(compile_tool)
            analyze_method = getattr(analyzer, ProjectAnalyzerFactory.get_analyze_method_name(compile_tool))
            result = analyze_method(project_file)
            
            if result and result.get('configurations'):
                self.available_configurations = result['configurations']
                config_names = [config['name'] for config in self.available_configurations]
                self.configuration_combo['values'] = config_names
                
                # 保存项目文件路径到config中
                if compile_tool == 'IAR':
                    self.config['iar_project_path'] = project_file
                elif compile_tool == 'MDK':
                    self.config['mdk_project_path'] = project_file
                
                if config_names:
                    # 默认选择第一个配置
                    self.configuration_var.set(config_names[0])
                    self.selected_configuration = self.available_configurations[0]
                    self.log_message(self.get_text('configs_found').format(count=len(config_names), names=', '.join(config_names)))
                    self.log_message(self.get_text('current_selection').format(name=config_names[0]))
                else:
                    self.configuration_var.set(self.get_text('no_valid_configs'))
                    self.log_message(self.get_text('no_configs_found'))
            else:
                self.available_configurations = []
                self.configuration_combo['values'] = []
                self.configuration_var.set(self.get_text('config_parse_failed'))
                self.log_message(self.get_text('config_parse_failed'))
                
        except Exception as e:
            self.log_message(f"{self.get_text('refresh_config_failed')}: {e}")
    
    def on_configuration_selected(self, event):
        """配置选择事件处理"""
        try:
            selected_name = self.configuration_var.get()
            if selected_name and selected_name != self.get_text('not_selected') and selected_name != self.get_text('no_project_file') and selected_name != self.get_text('config_parse_failed'):
                # 找到对应的配置信息
                for config in self.available_configurations:
                    if config['name'] == selected_name:
                        self.selected_configuration = config
                        self.log_message(self.get_text('config_selected').format(name=selected_name))
                        self.log_message(self.get_text('output_directory').format(dir=config['output_dir_abs']))
                        self.log_message(self.get_text('debug_mode').format(mode=config['debug']))
                        break
        except Exception as e:
            self.log_message(f"{self.get_text('config_selection_failed')}: {e}")


def main():
    """主函数"""
    try:
        app = MCUAutoBuildApp()
        app.run()
    except Exception as e:
        logger.error(f"应用程序启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
