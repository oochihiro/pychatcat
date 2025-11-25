#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的数据库查询脚本
用于快速查看最近的数据记录
"""

import sys
import io
import sqlite3
import os

# Windows 控制台编码修复
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except:
        pass

# 数据库路径
db_path = os.path.join(os.path.dirname(__file__), 'data', 'learning_analytics.db')

if not os.path.exists(db_path):
    print(f"❌ 数据库文件不存在: {db_path}")
    print("请先运行应用，数据库会在首次使用时自动创建")
    sys.exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("📊 数据库查询结果")
    print("=" * 60)
    print()
    
    # 1. 最近1小时的行为记录
    cursor.execute("""
        SELECT COUNT(*) FROM learning_behaviors
        WHERE timestamp >= datetime('now', '-1 hour')
    """)
    behavior_count = cursor.fetchone()[0]
    print(f"📝 最近1小时的行为记录: {behavior_count}")
    
    # 2. 最近1小时的代码操作
    cursor.execute("""
        SELECT COUNT(*) FROM code_operations
        WHERE timestamp >= datetime('now', '-1 hour')
    """)
    code_op_count = cursor.fetchone()[0]
    print(f"💻 最近1小时的代码操作: {code_op_count}")
    
    # 3. 最近1小时的AI交互
    cursor.execute("""
        SELECT COUNT(*) FROM ai_interactions
        WHERE timestamp >= datetime('now', '-1 hour')
    """)
    ai_int_count = cursor.fetchone()[0]
    print(f"🤖 最近1小时的AI交互: {ai_int_count}")
    
    print()
    print("=" * 60)
    
    # 4. 显示最近的行为记录详情
    if behavior_count > 0:
        print("\n📝 最近5条行为记录:")
        print("-" * 60)
        cursor.execute("""
            SELECT behavior_code, timestamp, session_id
            FROM learning_behaviors
            WHERE timestamp >= datetime('now', '-1 hour')
            ORDER BY timestamp DESC
            LIMIT 5
        """)
        for row in cursor.fetchall():
            print(f"  [{row[1]}] {row[0]} (会话: {row[2][:20]}...)")
    
    # 5. 显示最近的代码操作详情
    if code_op_count > 0:
        print("\n💻 最近5条代码操作:")
        print("-" * 60)
        cursor.execute("""
            SELECT operation_type, success, timestamp
            FROM code_operations
            WHERE timestamp >= datetime('now', '-1 hour')
            ORDER BY timestamp DESC
            LIMIT 5
        """)
        for row in cursor.fetchall():
            status = "✅ 成功" if row[1] else "❌ 失败"
            print(f"  [{row[2]}] {row[0]} - {status}")
    
    # 6. 显示最近的AI交互详情
    if ai_int_count > 0:
        print("\n🤖 最近5条AI交互:")
        print("-" * 60)
        cursor.execute("""
            SELECT interaction_type, response_time, timestamp
            FROM ai_interactions
            WHERE timestamp >= datetime('now', '-1 hour')
            ORDER BY timestamp DESC
            LIMIT 5
        """)
        for row in cursor.fetchall():
            interaction_type, resp_time, ts = row
            # 有些旧数据可能没有记录 response_time，为 None 时避免格式化错误
            if resp_time is None:
                rt_str = "未知"
            else:
                try:
                    rt_str = f"{float(resp_time):.2f}"
                except Exception:
                    rt_str = str(resp_time)
            print(f"  [{ts}] {interaction_type} - 响应时间: {rt_str}秒")
    
    conn.close()
    
except sqlite3.Error as e:
    print(f"❌ 数据库错误: {e}")
except Exception as e:
    print(f"❌ 发生错误: {e}")
    import traceback
    traceback.print_exc()

