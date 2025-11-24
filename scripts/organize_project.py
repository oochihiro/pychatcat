#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目整理脚本 - 将文件移动到合适的目录
"""

import os
import shutil
from pathlib import Path

def organize_files():
    """整理项目文件"""
    base_dir = Path(__file__).parent.parent
    
    # 确保目录存在
    docs_dir = base_dir / "docs"
    scripts_dir = base_dir / "scripts"
    docs_dir.mkdir(exist_ok=True)
    scripts_dir.mkdir(exist_ok=True)
    
    # 移动文档文件
    doc_files = [
        "使用指南.txt",
        "项目说明.md",
        "数据分析方案.md",
        "SQLite数据分析系统说明.md",
        "技术方案总结.md",
        "最终版本说明.txt",
        "deployment_guide.md",
        "README.txt"
    ]
    
    for file in doc_files:
        src = base_dir / file
        if src.exists():
            if file == "deployment_guide.md":
                dst = docs_dir / "部署指南.md"
            else:
                dst = docs_dir / file
            print(f"移动: {file} -> docs/{dst.name}")
            shutil.move(str(src), str(dst))
    
    # 移动脚本文件（如果还在根目录）
    script_files = [
        "start_sqlite_system.py",
        "start_analytics_system.py",
        "test_sqlite_system.py",
        "simple_test.py"
    ]
    
    for file in script_files:
        src = base_dir / file
        if src.exists() and src.parent == base_dir:
            dst = scripts_dir / file
            print(f"移动: {file} -> scripts/{file}")
            shutil.move(str(src), str(dst))
    
    # 移动配置文件
    config_files = {
        "nginx.conf": "backend/nginx.conf"
    }
    
    for file, dst_path in config_files.items():
        src = base_dir / file
        if src.exists():
            dst = base_dir / dst_path
            dst.parent.mkdir(parents=True, exist_ok=True)
            print(f"移动: {file} -> {dst_path}")
            shutil.move(str(src), str(dst))
    
    # 清理临时文件
    temp_files = [
        "analytics_export_*.json",
        "conversation_*.txt",
        "init.sql"
    ]
    
    print("\n整理完成！")
    print("\n建议清理的文件：")
    print("- data/*.db (测试数据库)")
    print("- logs/*.log (日志文件)")
    print("- __pycache__/ (Python缓存)")

if __name__ == "__main__":
    organize_files()




