#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地云端连接诊断工具
在桌面应用端运行，检查云端连接问题
"""

import sys
import io

# 设置标准输出为UTF-8编码（Windows兼容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import urllib3
from config import backend_config

# 禁用SSL警告（用于测试）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("=" * 60)
print("🔍 云端连接诊断工具（本地端）")
print("=" * 60)
print()

# 1. 检查配置
print("1️⃣ 检查配置...")
print(f"   BACKEND_URL: {backend_config.BACKEND_URL}")
print(f"   ENABLE_CLOUD_ANALYTICS: {backend_config.ENABLE_CLOUD_ANALYTICS}")
print(f"   REQUEST_TIMEOUT: {backend_config.REQUEST_TIMEOUT} 秒")
print()

# 2. 测试多个地址
print("2️⃣ 测试连接...")
TEST_URLS = [
    ("HTTPS (默认)", backend_config.BACKEND_URL),
    ("HTTP (备用)", backend_config.BACKEND_URL.replace("https://", "http://")),
]

working_url = None
for name, url in TEST_URLS:
    if not url:
        continue
    print(f"   测试 {name}: {url}...")
    try:
        response = requests.get(f"{url}/api/health", timeout=5, verify=False)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {name} 连接成功!")
            print(f"      响应: {data}")
            working_url = url
            break
        else:
            print(f"   ❌ {name} 返回错误: HTTP {response.status_code}")
    except requests.exceptions.SSLError as e:
        print(f"   ⚠️ {name} SSL错误: {str(e)[:80]}")
    except requests.exceptions.ConnectionError as e:
        error_msg = str(e)
        if "10061" in error_msg or "actively refused" in error_msg.lower():
            print(f"   ❌ {name} 连接被拒绝: 服务器可能未运行或端口被阻止")
        else:
            print(f"   ❌ {name} 连接失败: {str(e)[:80]}")
    except requests.exceptions.Timeout:
        print(f"   ❌ {name} 连接超时: 超过5秒未响应")
    except Exception as e:
        print(f"   ❌ {name} 未知错误: {str(e)[:80]}")

print()

# 3. DNS解析测试
print("3️⃣ 测试DNS解析...")
try:
    import socket
    hostname = backend_config.BACKEND_URL.replace("https://", "").replace("http://", "").split("/")[0]
    ip = socket.gethostbyname(hostname)
    print(f"   ✅ DNS解析成功: {hostname} -> {ip}")
except Exception as e:
    print(f"   ❌ DNS解析失败: {e}")

print()

# 4. 端口测试
print("4️⃣ 测试端口连接...")
try:
    import socket
    hostname = backend_config.BACKEND_URL.replace("https://", "").replace("http://", "").split("/")[0]
    port = 443 if "https://" in backend_config.BACKEND_URL else 80
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((hostname, port))
    sock.close()
    
    if result == 0:
        print(f"   ✅ 端口 {port} 可连接")
    else:
        print(f"   ❌ 端口 {port} 无法连接 (错误码: {result})")
        print(f"      可能原因: 1) 服务器未运行  2) 防火墙阻止  3) 网络被阻止")
except Exception as e:
    print(f"   ❌ 端口测试失败: {e}")

print()

# 5. 诊断总结
print("=" * 60)
print("💡 诊断总结:")
print("=" * 60)
if working_url:
    print("✅ 找到可用的连接地址!")
    print(f"   建议使用: {working_url}")
    print(f"   💡 如果当前配置不同，请修改 config/backend_config.py")
else:
    print("❌ 所有连接地址都无法访问")
    print()
    print("可能的原因:")
    print("1. 服务器未运行")
    print("   → 在服务器上运行: python3 backend/app.py")
    print("   → 或通过宝塔 Python 项目管理器启动")
    print()
    print("2. 网络被阻止（校园网/移动热点常见）")
    print("   → HTTPS端口443可能被阻止")
    print("   → 尝试使用HTTP: 修改 config/backend_config.py 中的 BACKEND_URL")
    print()
    print("3. 防火墙阻止")
    print("   → 检查Windows防火墙设置")
    print("   → 检查服务器防火墙（宝塔面板 -> 安全 -> 防火墙）")
    print()
    print("4. DNS解析问题")
    print("   → 检查域名是否正确解析")
    print()
    print("💡 本地数据采集不受影响，数据将保存在本地数据库")
    print("   位置: data/learning_analytics.db")

print("=" * 60)

