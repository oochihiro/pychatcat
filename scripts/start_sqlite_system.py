#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite数据分析系统启动脚本
"""

import os
import sys
import subprocess
import time
import threading
from pathlib import Path

def check_dependencies():
    """检查依赖"""
    print("🔍 检查系统依赖...")
    
    required_packages = [
        'flask',
        'flask_cors', 
        'pandas',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 已安装")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} 未安装")
    
    if missing_packages:
        print(f"\n📦 需要安装以下依赖包: {', '.join(missing_packages)}")
        install_cmd = f"pip install {' '.join(missing_packages)}"
        print(f"请运行: {install_cmd}")
        return False
    
    return True

def check_directories():
    """检查必要目录"""
    print("\n📁 检查目录结构...")
    
    required_dirs = [
        'data',
        'logs',
        'backend',
        'core',
        'integrations',
        'ui'
    ]
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ {dir_name}/ 目录存在")
        else:
            print(f"❌ {dir_name}/ 目录不存在")
            if dir_name in ['data', 'logs']:
                os.makedirs(dir_name, exist_ok=True)
                print(f"✅ 已创建 {dir_name}/ 目录")

def start_backend():
    """启动后端服务"""
    print("\n🚀 启动后端API服务...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ backend目录不存在")
        return None
    
    try:
        # 启动Flask应用
        backend_process = subprocess.Popen([
            sys.executable, "app.py"
        ], cwd=backend_dir)
        
        print("✅ 后端服务启动成功")
        print("📍 API地址: http://localhost:5000")
        return backend_process
        
    except Exception as e:
        print(f"❌ 启动后端服务失败: {e}")
        return None

def start_frontend():
    """启动前端应用"""
    print("\n🖥️ 启动前端应用...")
    
    try:
        # 启动主应用
        frontend_process = subprocess.Popen([
            sys.executable, "main.py"
        ])
        
        print("✅ 前端应用启动成功")
        return frontend_process
        
    except Exception as e:
        print(f"❌ 启动前端应用失败: {e}")
        return None

def show_system_info():
    """显示系统信息"""
    print("\n" + "="*60)
    print("🎓 Python学习助手 - SQLite数据分析系统")
    print("="*60)
    print("📊 数据采集: SQLite + Logging")
    print("🖥️ 前端界面: Tkinter")
    print("🌐 后端API: Flask")
    print("📈 数据分析: Pandas + NumPy")
    print("="*60)

def main():
    """主函数"""
    show_system_info()
    
    # 检查依赖
    if not check_dependencies():
        print("\n❌ 依赖检查失败，请安装缺失的包后重试")
        return
    
    # 检查目录
    check_directories()
    
    # 启动服务
    backend_process = None
    frontend_process = None
    
    try:
        # 启动后端（可选）
        start_backend_choice = input("\n是否启动后端API服务？(y/N): ").strip().lower()
        if start_backend_choice in ['y', 'yes']:
            backend_process = start_backend()
        
        # 启动前端
        frontend_process = start_frontend()
        
        if frontend_process:
            print("\n🎉 系统启动完成！")
            print("📱 前端应用已启动")
            if backend_process:
                print("🌐 后端API已启动 (http://localhost:5000)")
            print("\n💡 提示:")
            print("- 数据将自动保存到 data/learning_analytics.db")
            print("- 日志将保存到 logs/ 目录")
            print("- 按 Ctrl+C 退出系统")
            
            # 等待进程结束
            try:
                frontend_process.wait()
            except KeyboardInterrupt:
                print("\n\n🛑 正在关闭系统...")
                
                if frontend_process:
                    frontend_process.terminate()
                if backend_process:
                    backend_process.terminate()
                
                print("✅ 系统已关闭")
        
    except KeyboardInterrupt:
        print("\n\n🛑 用户中断，正在关闭系统...")
        
        if frontend_process:
            frontend_process.terminate()
        if backend_process:
            backend_process.terminate()
        
        print("✅ 系统已关闭")
    
    except Exception as e:
        print(f"\n❌ 系统启动失败: {e}")
        
        if frontend_process:
            frontend_process.terminate()
        if backend_process:
            backend_process.terminate()

if __name__ == "__main__":
    main()
