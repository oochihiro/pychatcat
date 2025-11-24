#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的SQLite系统测试
"""

import os
import sys

# 添加core目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

def test_basic():
    """基本测试"""
    print("开始SQLite数据分析系统测试...")
    
    try:
        # 测试导入
        from sqlite_analytics import SQLiteAnalytics
        print("[OK] SQLiteAnalytics导入成功")
        
        # 测试创建
        analytics = SQLiteAnalytics("data/test.db")
        print("[OK] SQLiteAnalytics创建成功")
        
        # 测试会话
        session_id = analytics.start_session("test_user")
        print(f"[OK] 会话创建成功: {session_id}")
        
        # 测试行为记录
        analytics.log_behavior(session_id, 'CP', duration=1.0)
        print("[OK] 行为记录成功")
        
        # 测试代码操作
        analytics.log_code_operation(session_id, 'run', success=True)
        print("[OK] 代码操作记录成功")
        
        # 测试AI交互
        analytics.log_ai_interaction(session_id, 'ask_question')
        print("[OK] AI交互记录成功")
        
        # 测试错误分析
        analytics.log_error_analysis(session_id, 'SyntaxError', 1, 'test error')
        print("[OK] 错误分析记录成功")
        
        # 测试会话结束
        analytics.end_session(session_id)
        print("[OK] 会话结束成功")
        
        # 清理
        if os.path.exists("data/test.db"):
            os.remove("data/test.db")
            print("[OK] 测试文件清理成功")
        
        print("\n[SUCCESS] 所有基本测试通过！")
        return True
        
    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")
        return False

def test_integration():
    """测试集成"""
    print("\n测试集成功能...")
    
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'integrations'))
        from sqlite_integration import sqlite_integration
        
        if sqlite_integration.enabled:
            print("[OK] 集成模块可用")
            sqlite_integration.log_behavior('CP')
            print("[OK] 集成行为记录成功")
        else:
            print("[WARNING] 集成模块不可用")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 集成测试失败: {e}")
        return False

if __name__ == "__main__":
    success1 = test_basic()
    success2 = test_integration()
    
    if success1 and success2:
        print("\n[SUCCESS] 系统测试完成，功能正常！")
        sys.exit(0)
    else:
        print("\n[ERROR] 部分测试失败")
        sys.exit(1)
