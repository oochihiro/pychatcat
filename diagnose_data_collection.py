#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断数据采集功能
检查为什么没有行为日志记录
"""

import os
import sys

print("=" * 60)
print("🔍 数据采集功能诊断")
print("=" * 60)
print()

# 1. 检查模块导入
print("1️⃣ 检查模块导入...")
try:
    from integrations.sqlite_integration import sqlite_integration, integrate_with_app
    print("   ✅ 成功导入 sqlite_integration")
    print(f"      数据采集已启用: {sqlite_integration.enabled}")
    print(f"      会话ID: {sqlite_integration.current_session_id}")
    print(f"      云端上报已启用: {sqlite_integration.cloud_enabled}")
except Exception as e:
    print(f"   ❌ 导入失败: {e}")
    sys.exit(1)

try:
    from core.sqlite_analytics import analytics
    print("   ✅ 成功导入 sqlite_analytics")
    print(f"      数据库路径: {analytics.db_path}")
except Exception as e:
    print(f"   ❌ 导入失败: {e}")

print()

# 2. 检查数据库文件
print("2️⃣ 检查数据库文件...")
db_path = "data/learning_analytics.db"
if os.path.exists(db_path):
    print(f"   ✅ 数据库文件存在: {db_path}")
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"      数据库表: {tables}")
    
    # 检查数据
    if 'learning_behaviors' in tables:
        cursor.execute("SELECT COUNT(*) FROM learning_behaviors")
        count = cursor.fetchone()[0]
        print(f"      行为记录数: {count}")
    
    if 'user_sessions' in tables:
        cursor.execute("SELECT COUNT(*) FROM user_sessions")
        count = cursor.fetchone()[0]
        print(f"      会话记录数: {count}")
    
    conn.close()
else:
    print(f"   ⚠️ 数据库文件不存在: {db_path}")
    print(f"   💡 数据采集功能可能未初始化")

print()

# 3. 检查日志目录和文件
print("3️⃣ 检查日志目录...")
log_dir = "logs"
if os.path.exists(log_dir):
    print(f"   ✅ 日志目录存在: {log_dir}")
    log_files = [f for f in os.listdir(log_dir) if f.startswith('analytics_')]
    if log_files:
        print(f"      日志文件数: {len(log_files)}")
        latest = max(log_files)
        print(f"      最新日志: {latest}")
        
        # 查看最新日志的最后几行
        log_path = os.path.join(log_dir, latest)
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"      日志总行数: {len(lines)}")
            if lines:
                print(f"      最后5行:")
                for line in lines[-5:]:
                    print(f"        {line.strip()}")
    else:
        print(f"   ⚠️ 日志目录为空")
else:
    print(f"   ⚠️ 日志目录不存在: {log_dir}")

print()

# 4. 测试数据采集功能
print("4️⃣ 测试数据采集功能...")
if sqlite_integration.enabled:
    try:
        # 测试记录行为
        sqlite_integration.log_behavior('UT', duration=1.0, additional_data={'test': True})
        print("   ✅ 测试行为记录成功")
        
        # 检查是否写入数据库
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM learning_behaviors WHERE behavior_code = 'UT'")
        count = cursor.fetchone()[0]
        print(f"      测试行为已写入数据库: {count > 0}")
        conn.close()
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
else:
    print("   ❌ 数据采集功能未启用")

print()

# 5. 检查集成状态
print("5️⃣ 检查集成状态...")
print("   💡 要检查集成状态，需要运行 main.py")
print("   💡 查看控制台输出，应该看到:")
print("      📊 SQLite数据采集功能已启用")
print("      📊 正在集成SQLite数据采集功能...")
print("      📊 数据采集会话已开始: session_xxxxx")

print()
print("=" * 60)
print("💡 诊断建议:")
print("=" * 60)
if not sqlite_integration.enabled:
    print("❌ 数据采集功能未启用")
    print("   检查:")
    print("   1. core/sqlite_analytics.py 是否存在")
    print("   2. integrations/sqlite_integration.py 是否正确")
    print("   3. main.py 中是否正确调用 integrate_with_app")
else:
    print("✅ 数据采集功能已启用")
    print("   如果运行时没有记录，检查:")
    print("   1. 集成代码是否被正确调用")
    print("   2. 日志路径是否正确（EXE运行时的工作目录）")
    print("   3. 数据库路径是否正确")
print("=" * 60)




