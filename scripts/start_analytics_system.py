#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学生行为分析系统 - 快速启动脚本
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

def check_dependencies():
    """检查依赖"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pymysql',
        'pandas',
        'numpy',
        'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 缺少以下依赖包:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ 所有依赖包已安装")
    return True

def start_backend():
    """启动后端服务"""
    print("🚀 启动后端服务...")
    
    backend_dir = Path("backend_example")
    if not backend_dir.exists():
        print("❌ 后端目录不存在，请检查backend_example目录")
        return None
    
    try:
        # 启动FastAPI服务
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 等待服务启动
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ 后端服务启动成功 (http://localhost:8000)")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ 后端服务启动失败:")
            print(stderr.decode())
            return None
            
    except Exception as e:
        print(f"❌ 启动后端服务时出错: {e}")
        return None

def start_frontend():
    """启动前端应用"""
    print("🚀 启动前端应用...")
    
    try:
        process = subprocess.Popen([sys.executable, "main.py"])
        
        if process.poll() is None:
            print("✅ 前端应用启动成功")
            return process
        else:
            print("❌ 前端应用启动失败")
            return None
            
    except Exception as e:
        print(f"❌ 启动前端应用时出错: {e}")
        return None

def check_database():
    """检查数据库连接"""
    print("🔍 检查数据库连接...")
    
    try:
        import pymysql
        conn = pymysql.connect(
            host="localhost",
            port=3306,
            database="analytics_db",
            user="analytics_user",
            password="analytics_password",
            charset='utf8mb4'
        )
        conn.close()
        print("✅ MySQL数据库连接正常")
        return True
    except Exception as e:
        print(f"⚠️ MySQL数据库连接失败: {e}")
        print("请确保MySQL已启动并创建了analytics_db数据库")
        print("可以运行: python install_mysql.py 来自动安装")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🎓 学生行为分析系统 - 快速启动")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 检查数据库（可选）
    check_database()
    
    # 启动后端服务
    backend_process = start_backend()
    if not backend_process:
        print("❌ 无法启动后端服务，退出")
        return
    
    # 启动前端应用
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ 无法启动前端应用")
        backend_process.terminate()
        return
    
    print("\n" + "=" * 60)
    print("🎉 系统启动完成!")
    print("📊 后端API: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    print("💻 前端应用: 已启动")
    print("=" * 60)
    print("\n按 Ctrl+C 停止所有服务...")
    
    try:
        # 等待用户中断
        while True:
            time.sleep(1)
            
            # 检查进程是否还在运行
            if backend_process.poll() is not None:
                print("❌ 后端服务意外停止")
                break
            
            if frontend_process.poll() is not None:
                print("❌ 前端应用意外停止")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 正在停止服务...")
        
        # 停止进程
        if backend_process.poll() is None:
            backend_process.terminate()
            backend_process.wait()
            print("✅ 后端服务已停止")
        
        if frontend_process.poll() is None:
            frontend_process.terminate()
            frontend_process.wait()
            print("✅ 前端应用已停止")
        
        print("👋 系统已完全停止")

if __name__ == "__main__":
    main()
