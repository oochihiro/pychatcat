#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXE功能验证脚本
用于验证打包后的EXE是否正常工作
"""

import sys
import io
import os
import sqlite3
import json
from datetime import datetime, timedelta

# Windows 控制台编码修复
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except:
        pass

print("=" * 60)
print("🔍 EXE功能验证工具")
print("=" * 60)
print()

# 1. 检查本地数据采集
print("1️⃣ 检查本地数据采集...")
db_path = os.path.join(os.path.dirname(__file__), 'data', 'learning_analytics.db')
if os.path.exists(db_path):
    print(f"   ✅ 数据库文件存在: {db_path}")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查最近的会话
        cursor.execute("""
            SELECT session_id, user_id, start_time, total_activities
            FROM user_sessions
            ORDER BY start_time DESC
            LIMIT 5
        """)
        sessions = cursor.fetchall()
        
        if sessions:
            print(f"   ✅ 找到 {len(sessions)} 个最近会话:")
            for sess in sessions:
                print(f"      - 会话: {sess[0]}, 用户: {sess[1]}, 时间: {sess[2]}, 活动数: {sess[3]}")
        else:
            print("   ⚠️ 数据库中没有会话记录")
        
        # 检查最近的行为记录
        cursor.execute("""
            SELECT COUNT(*) FROM learning_behaviors
            WHERE timestamp >= datetime('now', '-1 hour')
        """)
        recent_count = cursor.fetchone()[0]
        print(f"   📊 最近1小时的行为记录数: {recent_count}")
        
        conn.close()
    except Exception as e:
        print(f"   ❌ 检查数据库失败: {e}")
else:
    print(f"   ⚠️ 数据库文件不存在: {db_path}")
    print("   💡 如果刚启动应用，这是正常的，数据库会在首次使用时创建")

print()

# 2. 检查日志文件
print("2️⃣ 检查日志文件...")
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
if os.path.exists(log_dir):
    print(f"   ✅ 日志目录存在: {log_dir}")
    
    log_files = [f for f in os.listdir(log_dir) if f.startswith('analytics_') and f.endswith('.log')]
    if log_files:
        log_files.sort(reverse=True)
        latest_log = os.path.join(log_dir, log_files[0])
        print(f"   ✅ 最新日志文件: {log_files[0]}")
        
        try:
            with open(latest_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"   📊 日志总行数: {len(lines)}")
                
                # 检查关键信息
                has_session = any('Started session' in line for line in lines)
                has_behavior = any('Logged behavior' in line for line in lines)
                has_cloud = any('云端' in line or 'cloud' in line.lower() for line in lines)
                
                if has_session:
                    print("   ✅ 日志中包含会话启动记录")
                if has_behavior:
                    print("   ✅ 日志中包含行为记录")
                if has_cloud:
                    print("   ✅ 日志中包含云端相关记录")
                
                # 显示最后5行
                if lines:
                    print("   📝 最后5行日志:")
                    for line in lines[-5:]:
                        print(f"      {line.strip()}")
        except Exception as e:
            print(f"   ❌ 读取日志文件失败: {e}")
    else:
        print("   ⚠️ 日志目录中没有日志文件")
else:
    print(f"   ⚠️ 日志目录不存在: {log_dir}")

print()

# 3. 检查云端连接配置
print("3️⃣ 检查云端连接配置...")
try:
    from config import backend_config
    print(f"   ✅ 成功导入配置模块")
    print(f"      BACKEND_URL: {backend_config.BACKEND_URL}")
    print(f"      ENABLE_CLOUD_ANALYTICS: {backend_config.ENABLE_CLOUD_ANALYTICS}")
    
    if backend_config.ENABLE_CLOUD_ANALYTICS:
        print("   ✅ 云端上报已启用")
        
        # 测试连接
        try:
            import requests
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            response = requests.get(f"{backend_config.BACKEND_URL}/api/health", timeout=5, verify=False)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 云端连接成功!")
                print(f"      响应: {data.get('status', 'unknown')}")
            else:
                print(f"   ⚠️ 云端连接返回错误: HTTP {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"   ❌ 云端连接失败: 无法连接到服务器")
            print(f"      💡 可能原因: 1) 服务器未运行  2) 网络被阻止  3) 防火墙阻止")
        except Exception as e:
            print(f"   ⚠️ 云端连接测试失败: {e}")
    else:
        print("   ⚠️ 云端上报未启用")
except ImportError:
    print("   ❌ 无法导入配置模块")

print()

# 4. 检查用户身份文件
print("4️⃣ 检查用户身份...")
identity_file = os.path.join(os.path.dirname(__file__), 'data', 'user_identity.json')
if os.path.exists(identity_file):
    print(f"   ✅ 用户身份文件存在: {identity_file}")
    try:
        with open(identity_file, 'r', encoding='utf-8') as f:
            identity = json.load(f)
            print(f"      User ID: {identity.get('user_id', 'unknown')}")
            print(f"      设备标签: {identity.get('device_label', 'unknown')}")
    except Exception as e:
        print(f"   ❌ 读取用户身份文件失败: {e}")
else:
    print(f"   ⚠️ 用户身份文件不存在: {identity_file}")
    print("   💡 如果刚启动应用，这是正常的，文件会在首次使用时创建")

print()

# 5. 验证总结
print("=" * 60)
print("💡 验证总结:")
print("=" * 60)
print("✅ 本地数据采集: 检查数据库和日志文件")
print("✅ 云端连接: 检查配置和连接测试")
print("✅ 用户身份: 检查用户身份文件")
print()
print("📝 下一步操作:")
print("1. 运行应用，执行一些操作（输入代码、运行代码、使用AI助手）")
print("2. 等待1-2分钟后，再次运行此脚本查看数据")
print("3. 检查 logs/analytics_*.log 文件查看详细日志")
print("4. 检查 data/learning_analytics.db 数据库查看数据记录")
print("=" * 60)




