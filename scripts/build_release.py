#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发布构建脚本
用于创建GitHub发布版本
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build_dirs():
    """清理构建目录"""
    dirs_to_clean = ['build', 'release', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"已清理目录: {dir_name}")

def build_executable():
    """构建可执行文件"""
    try:
        print("开始构建可执行文件...")
        result = subprocess.run([sys.executable, 'build_exe.py'], 
                              capture_output=True, text=True, check=True)
        print("可执行文件构建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def create_release_package():
    """创建发布包"""
    release_dir = "release_package"
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    
    os.makedirs(release_dir, exist_ok=True)
    
    # 复制必要文件
    files_to_copy = [
        'README.md',
        'LICENSE',
        'CHANGELOG.md',
        'CONTRIBUTING.md',
        'requirements.txt',
        'config.example.json',
        'user_config.example.json',
    ]
    
    for file_name in files_to_copy:
        if os.path.exists(file_name):
            shutil.copy2(file_name, release_dir)
            print(f"已复制: {file_name}")
    
    # 复制可执行文件
    exe_files = [f for f in os.listdir('release') if f.endswith('.exe')]
    for exe_file in exe_files:
        shutil.copy2(os.path.join('release', exe_file), release_dir)
        print(f"已复制可执行文件: {exe_file}")
    
    print(f"发布包已创建: {release_dir}")

def main():
    """主函数"""
    print("=== IAR固件发布工具 - 发布构建脚本 ===")
    
    # 清理构建目录
    clean_build_dirs()
    
    # 构建可执行文件
    if not build_executable():
        print("构建失败，退出")
        return 1
    
    # 创建发布包
    create_release_package()
    
    print("发布构建完成！")
    return 0

if __name__ == "__main__":
    sys.exit(main())
