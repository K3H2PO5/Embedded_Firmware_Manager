#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git管理模块
负责检查Git状态、获取commit信息等
"""

import subprocess
import os
from lib_logger import logger
import sys
from datetime import datetime
from typing import Tuple, Optional, List


class GitManager:
    """Git操作管理类"""
    
    @staticmethod
    def _get_subprocess_kwargs():
        """获取subprocess调用的通用参数，用于隐藏命令行窗口"""
        kwargs = {
            'capture_output': True,
            'text': True,
            'encoding': 'utf-8',
            'errors': 'replace'
        }
        # 在Windows上隐藏命令行窗口
        if sys.platform == 'win32' and hasattr(subprocess, 'CREATE_NO_WINDOW'):
            kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
        return kwargs
    
    def __init__(self, repo_path: str = "."):
        """
        初始化Git管理器
        
        Args:
            repo_path: Git仓库路径，默认为当前目录
        """
        self.repo_path = os.path.abspath(repo_path)
        
    def is_git_repo(self) -> bool:
        """检查是否为Git仓库"""
        try:
            git_dir = os.path.join(self.repo_path, '.git')
            return os.path.exists(git_dir) or os.path.exists(git_dir + '.git')
        except Exception as e:
            logger.error(f"检查Git仓库失败: {e}")
            return False
    
    def has_uncommitted_changes(self) -> bool:
        """
        检查是否有未提交的更改
        
        Returns:
            bool: True表示有未提交的更改，False表示工作区干净
        """
        try:
            # 检查工作区状态
            kwargs = self._get_subprocess_kwargs()
            kwargs['cwd'] = self.repo_path
            kwargs['timeout'] = 30
            
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                **kwargs
            )
            
            if result.returncode != 0:
                logger.error(f"Git status命令失败: {result.stderr}")
                return True  # 出错时假设有未提交更改
            
            # 如果有输出，说明有未提交的更改
            return len(result.stdout.strip()) > 0
            
        except subprocess.TimeoutExpired:
            logger.error("Git status命令超时")
            return True
        except Exception as e:
            logger.error(f"检查未提交更改失败: {e}")
            return True
    
    def get_current_commit_id(self) -> Optional[str]:
        """
        获取当前HEAD的commit ID
        
        Returns:
            str: 完整的commit hash，失败时返回None
        """
        try:
            kwargs = self._get_subprocess_kwargs()
            kwargs['cwd'] = self.repo_path
            kwargs['timeout'] = 30
            
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                **kwargs
            )
            
            if result.returncode == 0 and result.stdout:
                commit_id = result.stdout.strip()
                logger.info(f"当前commit ID: {commit_id}")
                return commit_id
            else:
                logger.error(f"获取commit ID失败: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("获取commit ID超时")
            return None
        except Exception as e:
            logger.error(f"获取commit ID异常: {e}")
            return None
    
    def get_short_commit_id(self, length: int = 8) -> Optional[str]:
        """
        获取短commit ID
        
        Args:
            length: commit ID长度，默认8位
            
        Returns:
            str: 短commit hash，失败时返回None
        """
        full_commit_id = self.get_current_commit_id()
        if full_commit_id:
            return full_commit_id[:length]
        return None
    
    
    def get_commit_info(self) -> dict:
        """
        获取详细的commit信息
        
        Returns:
            dict: 包含commit信息的字典
        """
        info = {
            'commit_id': None,
            'short_commit_id': None,
            'author': None,
            'date': None,
            'message': None,
            'branch': None
        }
        
        try:
            # 获取commit ID
            info['commit_id'] = self.get_current_commit_id()
            info['short_commit_id'] = self.get_short_commit_id()
            
            # 获取作者信息
            kwargs = self._get_subprocess_kwargs()
            kwargs['cwd'] = self.repo_path
            kwargs['timeout'] = 30
            
            result = subprocess.run(
                ['git', 'log', '-1', '--pretty=format:%an'],
                **kwargs
            )
            if result.returncode == 0 and result.stdout:
                info['author'] = result.stdout.strip()
            
            # 获取提交日期
            result = subprocess.run(
                ['git', 'log', '-1', '--pretty=format:%ad', '--date=iso'],
                **kwargs
            )
            if result.returncode == 0 and result.stdout:
                info['date'] = result.stdout.strip()
            
            # 获取提交信息
            result = subprocess.run(
                ['git', 'log', '-1', '--pretty=format:%s'],
                **kwargs
            )
            if result.returncode == 0 and result.stdout:
                info['message'] = result.stdout.strip()
            
            # 获取当前分支
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                **kwargs
            )
            if result.returncode == 0 and result.stdout:
                branch = result.stdout.strip()
                info['branch'] = branch
                logger.info(f"Git分支检测成功: {branch}")
            else:
                logger.warning(f"Git分支检测失败: returncode={result.returncode}, stderr={result.stderr}")
                # 尝试备用方法
                result2 = subprocess.run(
                    ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                    **kwargs
                )
                if result2.returncode == 0 and result2.stdout:
                    branch = result2.stdout.strip()
                    info['branch'] = branch
                    logger.info(f"使用备用方法检测到Git分支: {branch}")
                else:
                    logger.error(f"备用Git分支检测也失败: returncode={result2.returncode}, stderr={result2.stderr}")
            
        except Exception as e:
            logger.error(f"获取commit信息失败: {e}")
        
        return info
    
    def commit_changes(self, message: str = None) -> bool:
        """
        提交当前更改
        
        Args:
            message: 提交信息，如果为None则使用默认信息
            
        Returns:
            bool: 提交是否成功
        """
        try:
            if message is None:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                message = f"Auto build: {timestamp}"
            
            # 添加所有更改
            kwargs = self._get_subprocess_kwargs()
            kwargs['cwd'] = self.repo_path
            kwargs['timeout'] = 30
            kwargs['check'] = True
            
            subprocess.run(
                ['git', 'add', '.'],
                **kwargs
            )
            
            # 提交更改
            kwargs = self._get_subprocess_kwargs()
            kwargs['cwd'] = self.repo_path
            kwargs['timeout'] = 30
            
            result = subprocess.run(
                ['git', 'commit', '-m', message],
                **kwargs
            )
            
            if result.returncode == 0:
                logger.info(f"提交成功: {message}")
                return True
            else:
                logger.error(f"提交失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Git提交超时")
            return False
        except Exception as e:
            logger.error(f"Git提交异常: {e}")
            return False
    
    def get_recent_commits(self, count: int = 5) -> List[dict]:
        """
        获取最近的提交记录
        
        Args:
            count: 获取的提交数量
            
        Returns:
            List[dict]: 提交记录列表
        """
        commits = []
        try:
            kwargs = self._get_subprocess_kwargs()
            kwargs['cwd'] = self.repo_path
            kwargs['timeout'] = 30
            
            result = subprocess.run(
                ['git', 'log', f'-{count}', '--pretty=format:%H|%an|%ad|%s', '--date=iso'],
                **kwargs
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('|', 3)
                        if len(parts) >= 4:
                            commits.append({
                                'commit_id': parts[0],
                                'author': parts[1],
                                'date': parts[2],
                                'message': parts[3]
                            })
            
        except Exception as e:
            logger.error(f"获取提交记录失败: {e}")
        
        return commits


def test_git_manager():
    """测试Git管理器功能"""
    git_mgr = GitManager()
    
    print(f"是否为Git仓库: {git_mgr.is_git_repo()}")
    print(f"是否有未提交更改: {git_mgr.has_uncommitted_changes()}")
    print(f"当前commit ID: {git_mgr.get_current_commit_id()}")
    print(f"短commit ID: {git_mgr.get_short_commit_id()}")
    
    info = git_mgr.get_commit_info()
    print(f"Commit信息: {info}")


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    test_git_manager()
