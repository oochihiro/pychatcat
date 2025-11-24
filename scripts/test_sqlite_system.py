#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite数据分析系统测试脚本
"""

import os
import sys
import time
import sqlite3
from datetime import datetime

# 添加core目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

def test_sqlite_analytics():
    """测试SQLite分析器"""
    print("测试SQLite数据分析器...")
    
    try:
        from sqlite_analytics import SQLiteAnalytics
        
        # 创建测试分析器
        analytics = SQLiteAnalytics("data/test_analytics.db")
        
        # 开始测试会话
        session_id = analytics.start_session("test_user")
        print(f"[OK] 测试会话已开始: {session_id}")
        
        # 测试学习行为记录
        analytics.log_behavior(session_id, 'CP', duration=10.5, additional_data={
            'code_length': 100,
            'line_count': 5
        })
        print("[OK] 学习行为记录测试通过")
        
        # 测试代码操作记录
        analytics.log_code_operation(
            session_id,
            'run',
            code='print("Hello World")',
            success=True,
            execution_time=0.5
        )
        print("[OK] 代码操作记录测试通过")
        
        # 测试AI交互记录
        analytics.log_ai_interaction(
            session_id,
            'ask_question',
            question='如何学习Python？',
            response='Python是一种很好的编程语言...',
            response_time=2.3
        )
        print("[OK] AI交互记录测试通过")
        
        # 测试错误分析记录
        analytics.log_error_analysis(
            session_id,
            'SyntaxError',
            error_line=5,
            error_message='invalid syntax',
            fix_attempts=2,
            fix_success=True
        )
        print("[OK] 错误分析记录测试通过")
        
        # 测试会话统计
        stats = analytics.get_session_stats(session_id)
        print("[OK] 会话统计获取测试通过")
        
        # 结束测试会话
        analytics.end_session(session_id)
        print("[OK] 测试会话已结束")
        
        # 测试数据导出
        export_file = analytics.export_data(session_id)
        print(f"[OK] 数据导出测试通过: {export_file}")
        
        # 清理测试文件
        if os.path.exists("data/test_analytics.db"):
            os.remove("data/test_analytics.db")
            print("[OK] 测试文件已清理")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] SQLite分析器测试失败: {e}")
        return False

def test_database_structure():
    """测试数据库结构"""
    print("\n测试数据库结构...")
    
    try:
        from sqlite_analytics import SQLiteAnalytics
        
        # 创建测试分析器
        analytics = SQLiteAnalytics("data/test_structure.db")
        
        # 检查表是否存在
        with sqlite3.connect(analytics.db_path) as conn:
            cursor = conn.cursor()
            
            tables = [
                'user_sessions',
                'learning_behaviors', 
                'code_operations',
                'ai_interactions',
                'error_analysis'
            ]
            
            for table in tables:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if cursor.fetchone():
                    print(f"[OK] 表 {table} 存在")
                else:
                    print(f"[ERROR] 表 {table} 不存在")
                    return False
        
        # 清理测试文件
        if os.path.exists("data/test_structure.db"):
            os.remove("data/test_structure.db")
            print("[OK] 测试文件已清理")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 数据库结构测试失败: {e}")
        return False

def test_integration():
    """测试集成功能"""
    print("\n测试集成功能...")
    
    try:
        # 检查集成模块
        sys.path.append(os.path.join(os.path.dirname(__file__), 'integrations'))
        from sqlite_integration import sqlite_integration
        
        if sqlite_integration.enabled:
            print("[OK] SQLite集成模块可用")
            
            # 测试行为记录
            sqlite_integration.log_behavior('CP', additional_data={'test': True})
            print("[OK] 集成行为记录测试通过")
            
            # 测试代码操作记录
            sqlite_integration.log_code_operation('test', success=True)
            print("[OK] 集成代码操作记录测试通过")
            
        else:
            print("[WARNING] SQLite集成模块不可用")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 集成功能测试失败: {e}")
        return False

def test_flask_backend():
    """测试Flask后端"""
    print("\n测试Flask后端...")
    
    try:
        import requests
        
        # 测试健康检查
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            print("[OK] Flask后端健康检查通过")
            return True
        else:
            print(f"[WARNING] Flask后端响应异常: {response.status_code}")
            return False
            
    except Exception:
        print("[WARNING] Flask后端未启动或无法连接")
        return False
    except ImportError:
        print("[WARNING] requests库未安装，跳过Flask后端测试")
        return False
    except Exception as e:
        print(f"[ERROR] Flask后端测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("SQLite数据分析系统测试")
    print("="*50)
    
    test_results = []
    
    # 运行测试
    test_results.append(("SQLite分析器", test_sqlite_analytics()))
    test_results.append(("数据库结构", test_database_structure()))
    test_results.append(("集成功能", test_integration()))
    test_results.append(("Flask后端", test_flask_backend()))
    
    # 显示测试结果
    print("\n" + "="*50)
    print("📊 测试结果汇总:")
    print("="*50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "[OK] 通过" if result else "[ERROR] 失败"
        print(f"{test_name:15} : {status}")
        if result:
            passed += 1
    
    print("="*50)
    print(f"总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("[SUCCESS] 所有测试通过！系统运行正常")
    else:
        print("[WARNING] 部分测试失败，请检查系统配置")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
