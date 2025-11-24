#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断云端连接问题
在服务器上运行，检查云端上报是否正常工作
"""

import requests
import json
from datetime import datetime
import urllib3
import subprocess
import os

# 禁用SSL警告（用于测试）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("=" * 60)
print("🔍 云端连接诊断工具")
print("=" * 60)
print()

# 0. 检查服务状态
print("0️⃣ 检查服务状态...")
print("   检查 Flask 后端进程...")
try:
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    if 'gunicorn' in result.stdout or 'python' in result.stdout:
        print("   ✅ 发现 Python/Flask 进程")
        # 显示相关进程
        for line in result.stdout.split('\n'):
            if 'gunicorn' in line or ('python' in line and 'app.py' in line):
                print(f"      {line[:80]}")
    else:
        print("   ⚠️ 未发现 Flask 后端进程")
except:
    print("   ⚠️ 无法检查进程状态")

print("   检查端口 5000 是否监听...")
try:
    result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True)
    if ':5000' in result.stdout:
        print("   ✅ 端口 5000 正在监听")
    else:
        print("   ❌ 端口 5000 未监听")
except:
    try:
        result = subprocess.run(['ss', '-tlnp'], capture_output=True, text=True)
        if ':5000' in result.stdout:
            print("   ✅ 端口 5000 正在监听")
        else:
            print("   ❌ 端口 5000 未监听")
    except:
        print("   ⚠️ 无法检查端口状态")

print()

# 1. 测试健康检查（多个地址）
print("1️⃣ 测试健康检查接口...")
TEST_URLS = [
    ("内部地址", "http://127.0.0.1:5000"),
    ("外部域名HTTPS", "https://pychatcat.cloud"),
    ("外部域名HTTP", "http://pychatcat.cloud"),
]

working_url = None
for name, url in TEST_URLS:
    print(f"   测试 {name}: {url}...")
    try:
        response = requests.get(f"{url}/api/health", timeout=5, verify=False)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {name} 连接成功: {data}")
            working_url = url
            break
        else:
            print(f"   ❌ {name} 返回错误: HTTP {response.status_code}")
            print(f"      响应: {response.text[:100]}")
    except requests.exceptions.SSLError as e:
        print(f"   ⚠️ {name} SSL错误: {str(e)[:80]}")
    except Exception as e:
        print(f"   ❌ {name} 连接失败: {str(e)[:80]}")

if not working_url:
    print("\n   ⚠️ 所有地址都无法连接！")
    print("   💡 可能原因:")
    print("      1. Flask 后端未运行")
    print("      2. 端口 5000 未监听")
    print("      3. Nginx 配置错误")
    print("      4. 防火墙阻止")
    print("\n   🔧 修复步骤:")
    print("      1. 检查 Flask 后端: cd /www/wwwroot/pychatcat.cloud/python-learning-assistant/backend && python3 app.py")
    print("      2. 或通过宝塔 Python 项目管理器启动")
    print("      3. 检查 Nginx 配置")
else:
    BACKEND_URL = working_url
    print(f"\n   ✅ 使用可用地址: {BACKEND_URL}")

print()

# 如果找到了可用地址，继续测试
if working_url:
    BACKEND_URL = working_url
    
    # 2. 测试创建会话
    print("2️⃣ 测试创建会话接口...")
    try:
        payload = {
            "user_id": "test_user_diagnose",
            "device_label": "诊断工具"
        }
        response = requests.post(
            f"{BACKEND_URL}/api/sessions",
            json=payload,
            timeout=5,
            headers={"Content-Type": "application/json"},
            verify=False
        )
        # 检查状态码（201 或 200 都算成功）
        if response.status_code in [200, 201]:
            data = response.json()
            session_id = data.get("session_id")
            if session_id:
                print(f"   ✅ 会话创建成功: {session_id}")
            else:
                print(f"   ⚠️ 会话创建返回成功，但未获取到 session_id")
                print(f"      响应: {data}")
            
            # 3. 测试上报行为
            print("\n3️⃣ 测试上报学习行为...")
            behavior_payload = {
                "behavior_code": "CP",
                "duration": 10.5,
                "additional_data": {"test": True}
            }
            behavior_response = requests.post(
                f"{BACKEND_URL}/api/sessions/{session_id}/behaviors",
                json=behavior_payload,
                timeout=5,
                headers={"Content-Type": "application/json"},
                verify=False
            )
            if behavior_response.status_code == 201:
                print(f"   ✅ 行为上报成功")
            else:
                print(f"   ❌ 行为上报失败: HTTP {behavior_response.status_code}")
                print(f"      响应: {behavior_response.text[:200]}")
        else:
            print(f"   ❌ 会话创建失败: HTTP {response.status_code}")
            print(f"      响应: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")

print()

# 4. 检查数据库
print("4️⃣ 检查数据库最新记录...")
try:
    import sqlite3
    
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'learning_analytics.db')
    if os.path.exists(db_path):
        print(f"   ✅ 数据库文件存在: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查看最近的会话
        cursor.execute("""
            SELECT session_id, user_id, start_time, total_activities
            FROM user_sessions
            ORDER BY start_time DESC
            LIMIT 5
        """)
        sessions = cursor.fetchall()
        
        if sessions:
            print(f"   ✅ 数据库中有 {len(sessions)} 条最近会话:")
            for sess in sessions:
                print(f"      - 用户: {sess[1]}, 时间: {sess[2]}, 活动数: {sess[3]}")
        else:
            print(f"   ⚠️ 数据库中没有会话记录")
        
        # 查看最近的行为
        cursor.execute("""
            SELECT COUNT(*) FROM learning_behaviors
            WHERE timestamp >= datetime('now', '-7 days')
        """)
        recent_count = cursor.fetchone()[0]
        print(f"   📊 最近7天的行为记录数: {recent_count}")
        
        conn.close()
    else:
        print(f"   ⚠️ 数据库文件不存在: {db_path}")
        print(f"   💡 数据库文件应该在: {db_path}")
except Exception as e:
    print(f"   ❌ 检查数据库失败: {e}")

print()
print("=" * 60)
print("💡 诊断总结:")
print("=" * 60)
if not working_url:
    print("❌ Flask 后端无法连接")
    print("\n🔧 立即执行以下命令检查:")
    print("   1. ps aux | grep gunicorn")
    print("   2. netstat -tlnp | grep 5000")
    print("   3. systemctl status nginx")
    print("\n📝 如果 Flask 未运行，通过宝塔 Python 项目管理器启动")
else:
    print("✅ Flask 后端连接正常")
    print("✅ 可以接收数据")
    print("\n💡 如果桌面应用仍无法连接，检查:")
    print("   1. 桌面应用的 BACKEND_URL 配置")
    print("   2. 桌面应用的网络环境（校园网可能阻止 HTTPS）")
    print("   3. 查看桌面应用的 logs/analytics_*.log 文件")
print("=" * 60)
