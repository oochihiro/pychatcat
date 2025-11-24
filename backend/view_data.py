#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速查看学生行为数据
在服务器上直接运行，无需下载数据库
"""

import sys
import io

# Windows 控制台编码修复
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except:
        pass

import sqlite3
import json
from datetime import datetime
import os

# 数据库路径 - 支持本地和服务器两种路径
# 1. 先尝试项目根目录的 data/learning_analytics.db（本地开发）
# 2. 再尝试 backend/data/learning_analytics.db（服务器部署）
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path_local = os.path.join(project_root, 'data', 'learning_analytics.db')
db_path_server = os.path.join(os.path.dirname(__file__), 'data', 'learning_analytics.db')

if os.path.exists(db_path_local):
    db_path = db_path_local
elif os.path.exists(db_path_server):
    db_path = db_path_server
else:
    # 如果都不存在，使用本地路径（会在首次使用时创建）
    db_path = db_path_local

if not os.path.exists(db_path):
    print(f"❌ 数据库文件不存在: {db_path}")
    print("请检查数据库路径是否正确")
    exit(1)

print(f"📊 正在查看数据库: {db_path}\n")
print("=" * 60)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. 查看会话数
    cursor.execute("SELECT COUNT(*) FROM user_sessions")
    session_count = cursor.fetchone()[0]
    print(f"📈 总会话数: {session_count}")
    
    # 2. 查看唯一用户数
    cursor.execute("SELECT COUNT(DISTINCT user_id) FROM user_sessions")
    user_count = cursor.fetchone()[0]
    print(f"👥 唯一用户数: {user_count}")
    
    # 3. 查看最近10条学习行为
    print("\n" + "=" * 60)
    print("📝 最近10条学习行为:")
    print("-" * 60)
    cursor.execute("""
        SELECT b.behavior_code,
               COALESCE(b.activity_name, 'N/A') AS activity_name,
               b.timestamp,
               b.user_id,
               s.platform
        FROM learning_behaviors b
        LEFT JOIN user_sessions s ON b.session_id = s.session_id
        ORDER BY b.timestamp DESC
        LIMIT 10
    """)
    behaviors = cursor.fetchall()
    if behaviors:
        for row in behaviors:
            raw_uid = row[3] or "unknown"
            device = row[4] or "unknown-device"
            print(f"  [{row[2]}] {row[0]} - {row[1]} (用户: {raw_uid} | 设备: {device})")
    else:
        print("  (暂无数据)")
    
    # 4. 查看代码操作统计
    print("\n" + "=" * 60)
    print("💻 代码操作统计:")
    print("-" * 60)
    cursor.execute("""
        SELECT operation_type, 
               COUNT(*) as count,
               SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count,
               ROUND(100.0 * SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate
        FROM code_operations
        GROUP BY operation_type
    """)
    code_stats = cursor.fetchall()
    if code_stats:
        for row in code_stats:
            print(f"  {row[0]}: 总数={row[1]}, 成功={row[2]}, 成功率={row[3]}%")
    else:
        print("  (暂无数据)")
    
    # 5. 查看AI交互统计
    print("\n" + "=" * 60)
    print("🤖 AI交互统计:")
    print("-" * 60)
    cursor.execute("""
        SELECT interaction_type,
               COUNT(*) as count,
               ROUND(AVG(response_time), 2) as avg_response_time,
               ROUND(AVG(question_length), 0) as avg_question_length
        FROM ai_interactions
        GROUP BY interaction_type
    """)
    ai_stats = cursor.fetchall()
    if ai_stats:
        for row in ai_stats:
            print(f"  {row[0]}: 总数={row[1]}, 平均响应时间={row[2]}秒, 平均问题长度={int(row[3])}字符")
    else:
        print("  (暂无数据)")
    
    # 6. 查看错误分析统计
    print("\n" + "=" * 60)
    print("🐛 错误分析统计:")
    print("-" * 60)
    cursor.execute("""
        SELECT error_type,
               COUNT(*) as count,
               SUM(CASE WHEN fix_success = 1 THEN 1 ELSE 0 END) as fixed_count,
               ROUND(AVG(fix_attempts), 2) as avg_fix_attempts
        FROM error_analysis
        GROUP BY error_type
        ORDER BY count DESC
        LIMIT 10
    """)
    error_stats = cursor.fetchall()
    if error_stats:
        for row in error_stats:
            print(f"  {row[0]}: 总数={row[1]}, 已修复={row[2]}, 平均修复尝试={row[3]}次")
    else:
        print("  (暂无数据)")
    
    # 7. 查看最近的活动时间
    print("\n" + "=" * 60)
    print("⏰ 最近活动时间:")
    print("-" * 60)
    cursor.execute("""
        SELECT MAX(timestamp) as last_activity
        FROM learning_behaviors
    """)
    last_activity = cursor.fetchone()[0]
    if last_activity:
        print(f"  最后活动时间: {last_activity}")
    else:
        print("  (暂无数据)")
    
    print("\n" + "=" * 60)
    print("✅ 数据查看完成！")
    print("\n💡 提示:")
    print("  - 要查看更详细的数据，可以使用 sqlite3 命令行工具")
    print("  - 要导出数据，可以下载数据库文件到本地")
    print("  - 要查看实时数据，可以访问: http://pychatcat.cloud/api/analytics/overview")
    
    conn.close()
    
except sqlite3.Error as e:
    print(f"❌ 数据库错误: {e}")
except Exception as e:
    print(f"❌ 发生错误: {e}")

