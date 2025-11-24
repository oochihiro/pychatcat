# -*- coding: utf-8 -*-
"""
文件管理器
处理文件的新建、打开、保存等操作
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil
from datetime import datetime

try:
    # 延迟导入，避免在无数据采集环境下出错
    from integrations.sqlite_integration import sqlite_integration
except Exception:
    sqlite_integration = None


class FileManager:
    """文件管理器类"""
    
    def __init__(self):
        """初始化文件管理器"""
        self.current_file = None
        self.is_modified = False
        self.backup_dir = "data/backups"
        self.recent_files = []
        
        # 创建备份目录
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # 加载最近文件列表
        self.load_recent_files()

    def _log_file_behavior(self, behavior_code: str):
        """内部工具：记录文件相关行为到学习行为表"""
        if sqlite_integration is None or not getattr(sqlite_integration, "enabled", False):
            return
        info = self.get_file_info() or {}
        try:
            sqlite_integration.log_behavior(behavior_code, additional_data={
                'filename': info.get('filename'),
                'path': info.get('path'),
                'size': info.get('size'),
                'modified': info.get('modified'),
                'created': info.get('created'),
            })
        except Exception as e:
            print(f"记录文件行为失败: {e}")
        
    def new_file(self, code_editor=None):
        """
        创建新文件
        
        Args:
            code_editor: 代码编辑器实例（可选）
        """
        # 检查当前文件是否需要保存
        if self.is_modified and self.current_file:
            result = messagebox.askyesnocancel(
                "保存文件",
                "当前文件已修改，是否保存？"
            )
            if result is True:
                self.save_file(code_editor)
            elif result is None:
                return False
                
        self.current_file = None
        self.is_modified = False
        
        if code_editor:
            code_editor.clear_code()
        
        # 记录新建文件行为
        self._log_file_behavior('NF')

        return True
        
    def open_file(self, code_editor=None):
        """
        打开文件
        
        Args:
            code_editor: 代码编辑器实例（可选）
        """
        # 检查当前文件是否需要保存
        if self.is_modified and self.current_file:
            result = messagebox.askyesnocancel(
                "保存文件",
                "当前文件已修改，是否保存？"
            )
            if result is True:
                self.save_file(code_editor)
            elif result is None:
                return False
                
        # 选择文件
        filename = filedialog.askopenfilename(
            title="打开Python文件",
            defaultextension=".py",
            filetypes=[
                ("Python文件", "*.py"),
                ("文本文件", "*.txt"),
                ("所有文件", "*.*")
            ]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                self.current_file = filename
                self.is_modified = False
                
                if code_editor:
                    code_editor.set_code(content)
                    
                # 添加到最近文件列表
                self.add_to_recent_files(filename)

                # 记录打开文件行为
                self._log_file_behavior('OF')

                return True
                
            except Exception as e:
                messagebox.showerror("打开文件失败", f"无法打开文件：{str(e)}")
                return False
                
        return False
        
    def save_file(self, code_editor=None):
        """
        保存文件
        
        Args:
            code_editor: 代码编辑器实例（可选）
        """
        if not self.current_file:
            return self.save_as_file(code_editor)
            
        try:
            content = code_editor.get_code() if code_editor else ""
            
            # 创建备份
            self.create_backup(self.current_file, content)
            
            # 保存文件
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.is_modified = False
            
            # 添加到最近文件列表
            self.add_to_recent_files(self.current_file)

            # 记录保存文件行为
            self._log_file_behavior('SV')
            
            return True
            
        except Exception as e:
            messagebox.showerror("保存文件失败", f"无法保存文件：{str(e)}")
            return False
            
    def save_as_file(self, code_editor=None):
        """
        另存为文件
        
        Args:
            code_editor: 代码编辑器实例（可选）
        """
        filename = filedialog.asksaveasfilename(
            title="另存为",
            defaultextension=".py",
            filetypes=[
                ("Python文件", "*.py"),
                ("文本文件", "*.txt"),
                ("所有文件", "*.*")
            ]
        )
        
        if filename:
            try:
                content = code_editor.get_code() if code_editor else ""
                
                # 创建备份
                self.create_backup(filename, content)
                
                # 保存文件
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                self.current_file = filename
                self.is_modified = False
                
                # 添加到最近文件列表
                self.add_to_recent_files(filename)

                # 记录另存为行为
                self._log_file_behavior('SA')
                
                return True
                
            except Exception as e:
                messagebox.showerror("保存文件失败", f"无法保存文件：{str(e)}")
                return False
                
        return False
        
    def create_backup(self, filename, content):
        """
        创建文件备份
        
        Args:
            filename: 文件名
            content: 文件内容
        """
        try:
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir)
                
            # 生成备份文件名
            basename = os.path.basename(filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{basename}_{timestamp}.bak"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # 保存备份
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            # 限制备份文件数量（最多保留10个）
            self.cleanup_old_backups(basename)
            
        except Exception as e:
            print(f"创建备份失败：{e}")
            
    def cleanup_old_backups(self, basename):
        """
        清理旧的备份文件
        
        Args:
            basename: 基础文件名
        """
        try:
            backup_files = []
            for filename in os.listdir(self.backup_dir):
                if filename.startswith(basename) and filename.endswith('.bak'):
                    filepath = os.path.join(self.backup_dir, filename)
                    backup_files.append((filepath, os.path.getmtime(filepath)))
                    
            # 按修改时间排序，删除最旧的备份
            backup_files.sort(key=lambda x: x[1])
            
            while len(backup_files) > 10:
                old_backup = backup_files.pop(0)
                os.remove(old_backup[0])
                
        except Exception as e:
            print(f"清理旧备份失败：{e}")
            
    def get_file_info(self):
        """
        获取当前文件信息
        
        Returns:
            dict: 文件信息字典
        """
        if not self.current_file:
            return None
            
        try:
            stat = os.stat(self.current_file)
            return {
                'filename': os.path.basename(self.current_file),
                'path': self.current_file,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                'created': datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            print(f"获取文件信息失败：{e}")
            return None
            
    def add_to_recent_files(self, filename):
        """
        添加到最近文件列表
        
        Args:
            filename: 文件名
        """
        if filename in self.recent_files:
            self.recent_files.remove(filename)
            
        self.recent_files.insert(0, filename)
        
        # 限制最近文件数量
        if len(self.recent_files) > 10:
            self.recent_files = self.recent_files[:10]
            
        # 保存最近文件列表
        self.save_recent_files()
        
    def get_recent_files(self):
        """
        获取最近文件列表
        
        Returns:
            list: 最近文件列表
        """
        # 过滤掉不存在的文件
        existing_files = []
        for filename in self.recent_files:
            if os.path.exists(filename):
                existing_files.append(filename)
                
        self.recent_files = existing_files
        return self.recent_files.copy()
        
    def load_recent_files(self):
        """加载最近文件列表"""
        try:
            recent_file = "data/recent_files.txt"
            if os.path.exists(recent_file):
                with open(recent_file, 'r', encoding='utf-8') as f:
                    self.recent_files = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"加载最近文件列表失败：{e}")
            
    def save_recent_files(self):
        """保存最近文件列表"""
        try:
            recent_file = "data/recent_files.txt"
            os.makedirs(os.path.dirname(recent_file), exist_ok=True)
            
            with open(recent_file, 'w', encoding='utf-8') as f:
                for filename in self.recent_files:
                    f.write(filename + '\n')
        except Exception as e:
            print(f"保存最近文件列表失败：{e}")
            
    def is_modified(self):
        """
        检查文件是否已修改
        
        Returns:
            bool: 是否已修改
        """
        return self.is_modified
        
    def mark_modified(self):
        """标记文件为已修改"""
        self.is_modified = True
        
    def mark_saved(self):
        """标记文件为已保存"""
        self.is_modified = False
        
    def get_current_file(self):
        """
        获取当前文件名
        
        Returns:
            str: 当前文件名，如果没有则返回"未命名"
        """
        if self.current_file:
            return os.path.basename(self.current_file)
        return "未命名"
        
    def get_current_path(self):
        """
        获取当前文件路径
        
        Returns:
            str: 当前文件路径，如果没有则返回None
        """
        return self.current_file
        
    def close_file(self, code_editor=None):
        """
        关闭当前文件
        
        Args:
            code_editor: 代码编辑器实例（可选）
        """
        if self.is_modified:
            result = messagebox.askyesnocancel(
                "保存文件",
                "当前文件已修改，是否保存？"
            )
            if result is True:
                if not self.save_file(code_editor):
                    return False
            elif result is None:
                return False
                
        if code_editor:
            code_editor.clear_code()
            
        self.current_file = None
        self.is_modified = False
        return True
