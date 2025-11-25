#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据采集功能测试脚本
测试所有数据采集点是否正常工作
"""

import sys
import io
import os
import sqlite3
import json
import time

# Windows 控制台编码修复
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except:
        pass

print("=" * 60)
print("🧪 数据采集功能测试")
print("=" * 60)
print()

# 1. 测试学生ID管理器
print("1️⃣ 测试学生ID管理器...")
try:
    from core.student_id_manager import get_student_id, update_student_id
    print("   ✅ 成功导入学生ID管理器")
    
    # 测试获取学生ID（不弹出对话框，使用已保存的）
    test_id = get_student_id()
    if test_id:
        print(f"   ✅ 获取学生ID成功: {test_id}")
    else:
        print("   ⚠️ 未获取到学生ID（可能需要首次输入）")
except Exception as e:
    print(f"   ❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

print()

# 2. 测试SQLiteAnalytics
print("2️⃣ 测试SQLiteAnalytics...")
try:
    from core.sqlite_analytics import SQLiteAnalytics
    test_db_path = "data/test_analytics.db"
    
    # 清理旧测试数据库
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    analytics = SQLiteAnalytics(db_path=test_db_path)
    print("   ✅ SQLiteAnalytics初始化成功")
    
    # 测试启动会话
    session_id = analytics.start_session("test_student_001")
    print(f"   ✅ 启动会话成功: {session_id}")
    
    # 测试记录行为
    analytics.log_behavior(session_id, "CP", additional_data={
        'line_number': 10,
        'code_length': 100
    })
    print("   ✅ 记录行为成功: CP")
    
    # 测试记录代码操作
    analytics.log_code_operation(session_id, "run", code="print('hello')", 
                                 success=True, execution_time=0.1,
                                 additional_data={'start_line': 1, 'end_line': 1})
    print("   ✅ 记录代码操作成功: run")
    
    # 测试记录AI交互
    analytics.log_ai_interaction(session_id, "ask_question", 
                                question="如何定义函数？",
                                additional_data={'question_length': 10})
    print("   ✅ 记录AI交互成功: ask_question")
    
    # 验证数据
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM learning_behaviors")
    behavior_count = cursor.fetchone()[0]
    print(f"   ✅ 行为记录数: {behavior_count}")
    
    cursor.execute("SELECT COUNT(*) FROM code_operations")
    code_op_count = cursor.fetchone()[0]
    print(f"   ✅ 代码操作记录数: {code_op_count}")
    
    cursor.execute("SELECT COUNT(*) FROM ai_interactions")
    ai_int_count = cursor.fetchone()[0]
    print(f"   ✅ AI交互记录数: {ai_int_count}")
    
    # 验证user_id是否正确
    cursor.execute("SELECT user_id FROM learning_behaviors LIMIT 1")
    row = cursor.fetchone()
    if row:
        print(f"   ✅ user_id字段正确: {row[0]}")
    
    conn.close()
    
    # 清理测试数据库（延迟清理，避免文件被占用）
    try:
        if os.path.exists(test_db_path):
            time.sleep(0.5)  # 等待数据库连接关闭
            os.remove(test_db_path)
            print("   ✅ 测试数据库已清理")
    except PermissionError:
        print("   ⚠️ 测试数据库文件被占用，稍后会自动清理")
    
except Exception as e:
    print(f"   ❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

print()

# 3. 测试SQLiteIntegration
print("3️⃣ 测试SQLiteIntegration...")
try:
    from integrations.sqlite_integration import sqlite_integration
    
    if sqlite_integration.enabled:
        print("   ✅ SQLiteIntegration已启用")
        print(f"   ✅ 当前会话ID: {sqlite_integration.current_session_id}")
        print(f"   ✅ 当前用户ID: {sqlite_integration.current_user_id}")
        
        # 测试记录行为
        sqlite_integration.log_behavior('CP', additional_data={
            'test': True,
            'line_number': 5
        })
        print("   ✅ 记录行为成功: CP")
        
        # 等待异步操作完成
        time.sleep(0.5)
        
    else:
        print("   ⚠️ SQLiteIntegration未启用")
        
except Exception as e:
    print(f"   ❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

print()

# 4. 测试新行为编码
print("4️⃣ 测试新行为编码...")
try:
    from core.sqlite_analytics import SQLiteAnalytics
    test_db_path = "data/test_behavior_codes.db"
    
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    analytics = SQLiteAnalytics(db_path=test_db_path)
    session_id = analytics.start_session("test_student")
    
    # 测试所有新行为编码
    new_codes = ['CR', 'CC', 'PC', 'VC', 'VE', 'VO', 'CAC', 'AC']
    for code in new_codes:
        try:
            analytics.log_behavior(session_id, code, additional_data={'test': True})
            print(f"   ✅ 行为编码 {code} 测试成功")
        except Exception as e:
            print(f"   ❌ 行为编码 {code} 测试失败: {e}")
    
    # 清理（延迟清理，避免文件被占用）
    try:
        if os.path.exists(test_db_path):
            time.sleep(0.5)
            os.remove(test_db_path)
    except PermissionError:
        pass
        
except Exception as e:
    print(f"   ❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

print()

# 5. 测试数据库查询
print("5️⃣ 测试数据库查询...")
try:
    db_path = "data/learning_analytics.db"
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 测试查询user_id
        cursor.execute("""
            SELECT DISTINCT user_id 
            FROM learning_behaviors 
            WHERE user_id IS NOT NULL AND user_id != 'anonymous'
            LIMIT 5
        """)
        user_ids = cursor.fetchall()
        if user_ids:
            print(f"   ✅ 找到 {len(user_ids)} 个不同的学生ID:")
            for uid in user_ids:
                print(f"      - {uid[0]}")
        else:
            print("   ⚠️ 未找到学生ID记录（可能需要先运行应用）")
        
        # 测试查询additional_data JSON
        cursor.execute("""
            SELECT behavior_code, additional_data 
            FROM learning_behaviors 
            WHERE additional_data IS NOT NULL
            LIMIT 3
        """)
        rows = cursor.fetchall()
        if rows:
            print(f"   ✅ 找到 {len(rows)} 条包含额外数据的记录:")
            for row in rows:
                try:
                    data = json.loads(row[1]) if row[1] else {}
                    print(f"      - {row[0]}: {list(data.keys())}")
                except:
                    print(f"      - {row[0]}: (JSON解析失败)")
        
        conn.close()
    else:
        print("   ⚠️ 数据库文件不存在（需要先运行应用）")
        
except Exception as e:
    print(f"   ❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

print()

# 6. 测试总结
print("=" * 60)
print("💡 测试总结:")
print("=" * 60)
print("✅ 如果所有测试都通过，说明数据采集功能正常")
print("⚠️ 如果某些测试失败，请检查错误信息")
print()
print("📝 下一步:")
print("1. 运行应用: python main.py")
print("2. 执行一些操作（输入代码、运行代码、使用AI助手）")
print("3. 查看数据库: python backend\\view_data.py")
print("4. 验证数据: python query_database.py")
print("=" * 60)

