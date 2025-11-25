#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 EXE 是否包含云端上报功能
在源代码目录运行，检查打包配置
"""

import os
import sys

print("=" * 60)
print("🔍 检查 EXE 云端上报功能")
print("=" * 60)
print()

# 1. 检查配置文件
print("1️⃣ 检查配置文件...")
config_path = "config/backend_config.py"
if os.path.exists(config_path):
    print(f"   ✅ 配置文件存在: {config_path}")
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'ENABLE_CLOUD_ANALYTICS = True' in content:
            print("   ✅ 云端上报已启用: ENABLE_CLOUD_ANALYTICS = True")
        else:
            print("   ❌ 云端上报未启用: ENABLE_CLOUD_ANALYTICS 不是 True")
        if 'BACKEND_URL' in content:
            print(f"   ✅ 后端地址配置存在")
            # 提取 BACKEND_URL
            for line in content.split('\n'):
                if 'BACKEND_URL' in line and '=' in line:
                    print(f"      {line.strip()}")
        else:
            print("   ❌ 后端地址配置不存在")
else:
    print(f"   ❌ 配置文件不存在: {config_path}")

print()

# 2. 检查云端集成模块
print("2️⃣ 检查云端集成模块...")
cloud_integration_path = "integrations/cloud_integration.py"
if os.path.exists(cloud_integration_path):
    print(f"   ✅ 云端集成模块存在: {cloud_integration_path}")
else:
    print(f"   ❌ 云端集成模块不存在: {cloud_integration_path}")

sqlite_integration_path = "integrations/sqlite_integration.py"
if os.path.exists(sqlite_integration_path):
    print(f"   ✅ SQLite集成模块存在: {sqlite_integration_path}")
    # 检查是否包含云端上报代码
    with open(sqlite_integration_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'cloud_client' in content:
            print("   ✅ 包含云端客户端代码")
        else:
            print("   ❌ 不包含云端客户端代码")
else:
    print(f"   ❌ SQLite集成模块不存在: {sqlite_integration_path}")

print()

# 3. 检查 PyInstaller 配置
print("3️⃣ 检查 PyInstaller 打包配置...")
spec_files = [f for f in os.listdir('.') if f.endswith('.spec')]
if spec_files:
    print(f"   ✅ 找到 .spec 文件: {spec_files}")
    for spec_file in spec_files:
        with open(spec_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'cloud_integration' in content or 'config' in content:
                print(f"   ✅ {spec_file} 包含云端相关模块")
            else:
                print(f"   ⚠️ {spec_file} 可能不包含云端相关模块")
else:
    print("   ⚠️ 未找到 .spec 文件（可能使用默认配置）")

print()

# 4. 检查 requirements.txt
print("4️⃣ 检查依赖...")
requirements_path = "requirements.txt"
if os.path.exists(requirements_path):
    with open(requirements_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'requests' in content:
            print("   ✅ 包含 requests 库（云端上报需要）")
        else:
            print("   ❌ 不包含 requests 库")
else:
    print("   ⚠️ requirements.txt 不存在")

print()

# 5. 测试导入
print("5️⃣ 测试模块导入...")
try:
    from config.backend_config import BACKEND_URL, ENABLE_CLOUD_ANALYTICS
    print(f"   ✅ 成功导入配置")
    print(f"      BACKEND_URL = {BACKEND_URL}")
    print(f"      ENABLE_CLOUD_ANALYTICS = {ENABLE_CLOUD_ANALYTICS}")
except Exception as e:
    print(f"   ❌ 导入配置失败: {e}")

try:
    from integrations.cloud_integration import create_cloud_client
    print(f"   ✅ 成功导入云端客户端")
    client = create_cloud_client()
    print(f"      云端客户端已启用: {client.enabled}")
    print(f"      后端地址: {client.base_url}")
except Exception as e:
    print(f"   ❌ 导入云端客户端失败: {e}")

print()
print("=" * 60)
print("💡 建议:")
print("=" * 60)
print("1. 如果配置正确但 EXE 没有云端功能，需要重新打包")
print("2. 打包时确保包含以下模块:")
print("   - config.backend_config")
print("   - integrations.cloud_integration")
print("   - integrations.sqlite_integration")
print("   - requests (依赖库)")
print("3. 使用 --hidden-import 参数:")
print("   pyinstaller --hidden-import=config.backend_config --hidden-import=integrations.cloud_integration ...")
print("=" * 60)




