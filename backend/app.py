#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask后端应用 - 数据分析API
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import numpy as np

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from core.sqlite_analytics import SQLiteAnalytics

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 初始化分析器 - 使用项目根目录的数据库路径
db_path = os.path.join(project_root, 'data', 'learning_analytics.db')
analytics = SQLiteAnalytics(db_path=db_path)

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/sessions', methods=['POST'])
def create_session():
    """创建新的学习会话"""
    try:
        data = request.get_json()
        alias = data.get('alias')
        device_label = data.get('device_label') or data.get('user_id') or 'Python_Learning_Assistant'
        user_id = alias or data.get('user_id', 'anonymous')
        session_id = analytics.start_session(user_id=user_id, device_label=device_label)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Session created successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/sessions/<session_id>/behaviors', methods=['POST'])
def log_behavior(session_id):
    """记录学习行为"""
    try:
        data = request.get_json()
        behavior_code = data.get('behavior_code')
        duration = data.get('duration')
        additional_data = data.get('additional_data', {})
        
        analytics.log_behavior(session_id, behavior_code, duration, additional_data)
        
        return jsonify({
            'success': True,
            'message': 'Behavior logged successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/sessions/<session_id>/code-operations', methods=['POST'])
def log_code_operation(session_id):
    """记录代码操作"""
    try:
        data = request.get_json()
        operation_type = data.get('operation_type')
        code = data.get('code')
        success = data.get('success', True)
        error_message = data.get('error_message')
        execution_time = data.get('execution_time')
        
        analytics.log_code_operation(
            session_id, operation_type, code, success, 
            error_message, execution_time
        )
        
        return jsonify({
            'success': True,
            'message': 'Code operation logged successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/sessions/<session_id>/ai-interactions', methods=['POST'])
def log_ai_interaction(session_id):
    """记录AI交互"""
    try:
        data = request.get_json()
        interaction_type = data.get('interaction_type')
        question = data.get('question')
        response = data.get('response')
        response_time = data.get('response_time')
        feedback_quality = data.get('feedback_quality')
        
        analytics.log_ai_interaction(
            session_id, interaction_type, question, response,
            response_time, feedback_quality
        )
        
        return jsonify({
            'success': True,
            'message': 'AI interaction logged successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/sessions/<session_id>/errors', methods=['POST'])
def log_error_analysis(session_id):
    """记录错误分析"""
    try:
        data = request.get_json()
        error_type = data.get('error_type')
        error_line = data.get('error_line')
        error_message = data.get('error_message')
        fix_attempts = data.get('fix_attempts', 0)
        fix_success = data.get('fix_success', False)
        
        analytics.log_error_analysis(
            session_id, error_type, error_line, error_message,
            fix_attempts, fix_success
        )
        
        return jsonify({
            'success': True,
            'message': 'Error analysis logged successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/sessions/<session_id>/stats', methods=['GET'])
def get_session_stats(session_id):
    """获取会话统计信息"""
    try:
        stats = analytics.get_session_stats(session_id)
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analytics/overview', methods=['GET'])
def get_analytics_overview():
    """获取总体分析数据"""
    try:
        # 获取查询参数
        days = request.args.get('days', 30, type=int)
        start_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(analytics.db_path) as conn:
            # 总体统计
            cursor = conn.cursor()
            
            # 会话统计
            cursor.execute('''
                SELECT COUNT(*) as total_sessions,
                       COUNT(DISTINCT user_id) as unique_users,
                       AVG(total_activities) as avg_activities_per_session
                FROM user_sessions 
                WHERE start_time >= ?
            ''', (start_date,))
            session_stats = dict(zip([col[0] for col in cursor.description], cursor.fetchone()))
            
            # 行为统计
            cursor.execute('''
                SELECT behavior_code, activity_name, COUNT(*) as count
                FROM learning_behaviors lb
                JOIN user_sessions us ON lb.session_id = us.session_id
                WHERE us.start_time >= ?
                GROUP BY behavior_code, activity_name
                ORDER BY count DESC
            ''', (start_date,))
            behavior_stats = [
                dict(zip([col[0] for col in cursor.description], row))
                for row in cursor.fetchall()
            ]
            
            # 代码操作统计
            cursor.execute('''
                SELECT operation_type,
                       COUNT(*) as total_operations,
                       SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_operations,
                       AVG(execution_time) as avg_execution_time
                FROM code_operations co
                JOIN user_sessions us ON co.session_id = us.session_id
                WHERE us.start_time >= ?
                GROUP BY operation_type
            ''', (start_date,))
            code_stats = [
                dict(zip([col[0] for col in cursor.description], row))
                for row in cursor.fetchall()
            ]
            
            # AI交互统计
            cursor.execute('''
                SELECT interaction_type,
                       COUNT(*) as total_interactions,
                       AVG(response_time) as avg_response_time,
                       AVG(question_length) as avg_question_length,
                       AVG(response_length) as avg_response_length
                FROM ai_interactions ai
                JOIN user_sessions us ON ai.session_id = us.session_id
                WHERE us.start_time >= ?
                GROUP BY interaction_type
            ''', (start_date,))
            ai_stats = [
                dict(zip([col[0] for col in cursor.description], row))
                for row in cursor.fetchall()
            ]
            
            # 错误分析统计
            cursor.execute('''
                SELECT error_type,
                       COUNT(*) as total_errors,
                       SUM(CASE WHEN fix_success = 1 THEN 1 ELSE 0 END) as fixed_errors,
                       AVG(fix_attempts) as avg_fix_attempts
                FROM error_analysis ea
                JOIN user_sessions us ON ea.session_id = us.session_id
                WHERE us.start_time >= ?
                GROUP BY error_type
            ''', (start_date,))
            error_stats = [
                dict(zip([col[0] for col in cursor.description], row))
                for row in cursor.fetchall()
            ]
        
        return jsonify({
            'success': True,
            'overview': {
                'period': f'Last {days} days',
                'session_stats': session_stats,
                'behavior_stats': behavior_stats,
                'code_stats': code_stats,
                'ai_stats': ai_stats,
                'error_stats': error_stats
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analytics/export', methods=['GET'])
def export_data():
    """导出数据"""
    try:
        session_id = request.args.get('session_id')
        output_file = analytics.export_data(session_id)
        
        return jsonify({
            'success': True,
            'message': 'Data exported successfully',
            'file': output_file
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': analytics.db_path
    })

if __name__ == '__main__':
    # 创建templates目录
    os.makedirs('backend/templates', exist_ok=True)
    
    # 创建简单的HTML模板
    with open('backend/templates/index.html', 'w', encoding='utf-8') as f:
        f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Python学习助手 - 数据分析</title>
    <meta charset="utf-8">
</head>
<body>
    <h1>Python学习助手 - 数据分析后台</h1>
    <p>API服务正在运行中...</p>
    <p>数据库路径: data/learning_analytics.db</p>
    <p>日志路径: logs/</p>
</body>
</html>
        ''')
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=5000, debug=True)
