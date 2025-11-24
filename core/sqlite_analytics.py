#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite + Logging 数据采集系统
基于编程学习行为编码表的数据收集
"""

import sqlite3
import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import threading
import time

class SQLiteAnalytics:
    """SQLite数据分析采集器"""
    
    def __init__(self, db_path: str = "data/learning_analytics.db"):
        """
        初始化分析器
        
        Args:
            db_path: SQLite数据库文件路径
        """
        self.db_path = db_path
        self.lock = threading.Lock()
        
        # 确保数据目录存在
        db_dir = os.path.dirname(db_path)
        if db_dir:  # 只有当目录路径不为空时才创建
            os.makedirs(db_dir, exist_ok=True)
        
        # 初始化数据库
        self._init_database()
        
        # 初始化日志系统
        self._init_logging()
    
    def _init_database(self):
        """初始化SQLite数据库"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建用户会话表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    total_activities INTEGER DEFAULT 0,
                    platform TEXT DEFAULT 'Python_Learning_Assistant'
                )
            ''')
            
            # 创建学习行为表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_behaviors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    user_id TEXT,
                    behavior_code TEXT,
                    activity_name TEXT,
                    category TEXT,
                    description TEXT,
                    timestamp TIMESTAMP,
                    duration REAL,
                    additional_data TEXT,
                    FOREIGN KEY (session_id) REFERENCES user_sessions(session_id)
                )
            ''')
            
            # 创建代码操作表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS code_operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    user_id TEXT,
                    operation_type TEXT,
                    code_length INTEGER,
                    line_count INTEGER,
                    success BOOLEAN,
                    error_message TEXT,
                    execution_time REAL,
                    timestamp TIMESTAMP,
                    additional_data TEXT,
                    FOREIGN KEY (session_id) REFERENCES user_sessions(session_id)
                )
            ''')
            
            # 创建AI交互表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    user_id TEXT,
                    interaction_type TEXT,
                    question_length INTEGER,
                    response_length INTEGER,
                    response_time REAL,
                    feedback_quality TEXT,
                    timestamp TIMESTAMP,
                    additional_data TEXT,
                    FOREIGN KEY (session_id) REFERENCES user_sessions(session_id)
                )
            ''')
            
            # 创建错误分析表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS error_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    user_id TEXT,
                    error_type TEXT,
                    error_line INTEGER,
                    error_message TEXT,
                    fix_attempts INTEGER,
                    fix_success BOOLEAN,
                    timestamp TIMESTAMP,
                    additional_data TEXT,
                    FOREIGN KEY (session_id) REFERENCES user_sessions(session_id)
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_behaviors_session ON learning_behaviors(session_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_behaviors_timestamp ON learning_behaviors(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_behaviors_code ON learning_behaviors(behavior_code)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_code_session ON code_operations(session_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ai_session ON ai_interactions(session_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_error_session ON error_analysis(session_id)')
            
            conn.commit()
    
    def _init_logging(self):
        """初始化日志系统"""
        # 创建日志目录
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        # 配置日志格式
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # 创建文件处理器
        file_handler = logging.FileHandler(
            os.path.join(log_dir, f"analytics_{datetime.now().strftime('%Y%m%d')}.log"),
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(log_format))
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(logging.Formatter(log_format))
        
        # 配置根日志器
        self.logger = logging.getLogger('learning_analytics')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def start_session(self, user_id: str = None, session_id: str = None,
                     device_label: str = None) -> str:
        """
        开始新的学习会话
        
        Args:
            user_id: 用户ID
            session_id: 会话ID，如果为None则自动生成
            
        Returns:
            会话ID
        """
        if session_id is None:
            session_id = f"session_{int(time.time())}_{user_id or 'anonymous'}"

        platform_value = device_label or 'Python_Learning_Assistant'

        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO user_sessions 
                    (session_id, user_id, start_time, platform)
                    VALUES (?, ?, ?, ?)
                ''', (session_id, user_id, datetime.now(), platform_value))
                conn.commit()
        
        self.logger.info(f"Started session: {session_id} for user: {user_id}")
        return session_id
    
    def log_behavior(self, session_id: str, behavior_code: str, 
                    duration: float = None, additional_data: Dict = None):
        """
        记录学习行为
        
        Args:
            session_id: 会话ID
            behavior_code: 行为编码（如UT, RAM, CP等）
            duration: 行为持续时间（秒）
            additional_data: 额外数据
        """
        # 行为编码映射表（可拓展，至少覆盖 15 种典型学习行为）
        behavior_mapping = {
            # 任务与资源
            'UT': ('Understanding Task', '资源', '学生通过任务窗口查看编程任务详情'),
            'RAM': ('Referring to Additional Materials', '资源', '学生在参考资料中查阅内容'),

            # 代码编辑与操作
            'CP': ('Coding in Python', '编辑代码', '学生在代码编辑器中键入或修改代码'),
            'SC': ('Select Code', '编辑代码', '学生在编辑器中选中一段代码'),
            'CC': ('Copy Code', '编辑代码', '学生在代码编辑器中复制代码'),
            'PC': ('Paste Code', '粘贴代码', '学生在代码编辑器中粘贴代码'),

            # 文件操作
            'NF': ('New File', '文件操作', '学生新建代码文件'),
            'OF': ('Open File', '文件操作', '学生打开现有代码文件'),
            'SV': ('Save File', '文件操作', '学生保存当前文件'),
            'SA': ('Save As File', '文件操作', '学生将代码另存为新文件'),

            # 运行与调试
            'CR': ('Code Run', '运行代码', '学生执行代码'),
            'DP': ('Debugging in Python', '调试', '学生在调试过程中执行单步/跳过/跳出/设置断点等操作'),

            # 代码与结果阅读
            'UPC': ('Understanding Python Codes', '理解代码', '学生通过鼠标在代码上来回移动理解代码'),
            'CRC': ('Checking Result/Chart', '检查输出', '学生在控制台或图表区域检查输出结果'),
            'RCM': ('Reading Console Message', '阅读信息', '学生在阅读或复制控制台中的提示/警告信息'),
            'VE': ('Viewing Error', '查看错误', '学生在控制台中查看错误信息'),
            'VO': ('Viewing Output', '查看输出', '学生在控制台中查看普通输出'),
            'VC': ('Viewing Code', '查看代码', '学生在代码区域停留浏览'),

            # AI 相关行为
            'ANQ': ('Asking New Questions', 'AI辅助编程', '学生在AI助手中自主提出新的问题'),
            'PCM': ('Pasting Console Message', 'AI辅助编程', '学生在AI助手中粘贴控制台中的错误或输出信息'),
            'PPC': ('Pasting Python Codes', 'AI辅助编程', '学生在AI助手中粘贴自己的Python代码'),
            'CPC': ('Copy and Paste Codes', 'AI辅助编程', '学生将AI助手中的代码拷贝到编辑器'),
            'CAC': ('Copy AI Code', 'AI辅助编程', '学生从AI助手复制代码'),
            'RF': ('Reading Feedback', 'AI辅助编程', '学生在AI助手中阅读反馈信息'),
            'AC': ('AI Chat Area', 'AI交互', '学生在AI聊天区停留的时间'),
            'SAI': ('Select AI Text', 'AI交互', '学生在AI对话区域选中文本'),

            # 其他行为
            'FC': ('Failure in ChatGPT', '其他行为', '因平台/网络故障导致AI无法正常响应'),
            'IO': ('Idle Operation', '其他行为', '学生在一段时间内无任何可见操作')
        }
        
        if behavior_code not in behavior_mapping:
            self.logger.warning(f"Unknown behavior code: {behavior_code}")
            return
        
        activity_name, category, description = behavior_mapping[behavior_code]
        
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # 从会话表中获取 user_id
                cursor.execute('SELECT user_id FROM user_sessions WHERE session_id = ?', (session_id,))
                session_row = cursor.fetchone()
                user_id = session_row[0] if session_row else 'anonymous'
                
                cursor.execute('''
                    INSERT INTO learning_behaviors 
                    (session_id, user_id, behavior_code, activity_name, category, description, 
                     timestamp, duration, additional_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session_id, user_id, behavior_code, activity_name, category, description,
                    datetime.now(), duration, json.dumps(additional_data or {})
                ))
                conn.commit()
        
        self.logger.info(f"Logged behavior: {behavior_code} ({activity_name}) for session: {session_id}")
    
    def log_code_operation(self, session_id: str, operation_type: str, 
                          code: str = None, success: bool = True, 
                          error_message: str = None, execution_time: float = None,
                          additional_data: Dict = None):
        """
        记录代码操作
        
        Args:
            session_id: 会话ID
            operation_type: 操作类型（run, debug, edit等）
            code: 代码内容
            success: 是否成功
            error_message: 错误信息
            execution_time: 执行时间
            additional_data: 额外数据（如代码位置、行号等）
        """
        code_length = len(code) if code else 0
        line_count = len(code.split('\n')) if code else 0
        
        # 合并additional_data
        merged_data = {
            'code_preview': code[:100] + '...' if code and len(code) > 100 else code,
            'operation_type': operation_type
        }
        if additional_data:
            merged_data.update(additional_data)
        
        # 从会话表中获取 user_id
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT user_id FROM user_sessions WHERE session_id = ?', (session_id,))
                session_row = cursor.fetchone()
                user_id = session_row[0] if session_row else 'anonymous'
                
                cursor.execute('''
                    INSERT INTO code_operations 
                    (session_id, user_id, operation_type, code_length, line_count, success, 
                     error_message, execution_time, timestamp, additional_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session_id, user_id, operation_type, code_length, line_count, success,
                    error_message, execution_time, datetime.now(), json.dumps(merged_data)
                ))
                conn.commit()
        
        self.logger.info(f"Logged code operation: {operation_type} for session: {session_id}")
    
    def log_ai_interaction(self, session_id: str, interaction_type: str,
                          question: str = None, response: str = None,
                          response_time: float = None, feedback_quality: str = None,
                          additional_data: Dict = None):
        """
        记录AI交互
        
        Args:
            session_id: 会话ID
            interaction_type: 交互类型（ask_question, read_feedback等）
            question: 问题内容
            response: 回答内容
            response_time: 响应时间
            feedback_quality: 反馈质量
        """
        question_length = len(question) if question else 0
        response_length = len(response) if response else 0
        
        # 合并additional_data
        merged_data = {
            'question_preview': question[:100] + '...' if question and len(question) > 100 else question,
            'response_preview': response[:100] + '...' if response and len(response) > 100 else response,
            'interaction_type': interaction_type
        }
        if additional_data:
            merged_data.update(additional_data)
        
        # 从会话表中获取 user_id
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT user_id FROM user_sessions WHERE session_id = ?', (session_id,))
                session_row = cursor.fetchone()
                user_id = session_row[0] if session_row else 'anonymous'
                
                cursor.execute('''
                    INSERT INTO ai_interactions 
                    (session_id, user_id, interaction_type, question_length, response_length, 
                     response_time, feedback_quality, timestamp, additional_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session_id, user_id, interaction_type, question_length, response_length,
                    response_time, feedback_quality, datetime.now(), json.dumps(merged_data)
                ))
                conn.commit()
        
        self.logger.info(f"Logged AI interaction: {interaction_type} for session: {session_id}")
    
    def log_error_analysis(self, session_id: str, error_type: str, error_line: int,
                          error_message: str, fix_attempts: int = 0, fix_success: bool = False,
                          additional_data: Dict = None):
        """
        记录错误分析
        
        Args:
            session_id: 会话ID
            error_type: 错误类型
            error_line: 错误行号
            error_message: 错误信息
            fix_attempts: 修复尝试次数
            fix_success: 是否修复成功
        """
        # 合并additional_data
        merged_data = {
            'error_type': error_type,
            'error_line': error_line,
            'fix_attempts': fix_attempts
        }
        if additional_data:
            merged_data.update(additional_data)
        
        # 从会话表中获取 user_id
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT user_id FROM user_sessions WHERE session_id = ?', (session_id,))
                session_row = cursor.fetchone()
                user_id = session_row[0] if session_row else 'anonymous'
                
                cursor.execute('''
                    INSERT INTO error_analysis 
                    (session_id, user_id, error_type, error_line, error_message, 
                     fix_attempts, fix_success, timestamp, additional_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session_id, user_id, error_type, error_line, error_message,
                    fix_attempts, fix_success, datetime.now(), json.dumps(merged_data)
                ))
                conn.commit()
        
        self.logger.info(f"Logged error analysis: {error_type} for session: {session_id}")
    
    def end_session(self, session_id: str):
        """结束学习会话"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE user_sessions 
                    SET end_time = ?, total_activities = (
                        SELECT COUNT(*) FROM learning_behaviors WHERE session_id = ?
                    )
                    WHERE session_id = ?
                ''', (datetime.now(), session_id, session_id))
                conn.commit()
        
        self.logger.info(f"Ended session: {session_id}")
    
    def get_session_stats(self, session_id: str) -> Dict:
        """获取会话统计信息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 获取会话基本信息
            cursor.execute('SELECT * FROM user_sessions WHERE session_id = ?', (session_id,))
            session_info = cursor.fetchone()
            
            # 获取行为统计
            cursor.execute('''
                SELECT behavior_code, COUNT(*) as count 
                FROM learning_behaviors 
                WHERE session_id = ? 
                GROUP BY behavior_code
            ''', (session_id,))
            behavior_stats = dict(cursor.fetchall())
            
            # 获取代码操作统计
            cursor.execute('''
                SELECT COUNT(*) as total_operations,
                       SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_operations,
                       AVG(execution_time) as avg_execution_time
                FROM code_operations 
                WHERE session_id = ?
            ''', (session_id,))
            code_stats = cursor.fetchone()
            
            # 获取AI交互统计
            cursor.execute('''
                SELECT COUNT(*) as total_interactions,
                       AVG(response_time) as avg_response_time,
                       AVG(question_length) as avg_question_length
                FROM ai_interactions 
                WHERE session_id = ?
            ''', (session_id,))
            ai_stats = cursor.fetchone()
            
            return {
                'session_info': session_info,
                'behavior_stats': behavior_stats,
                'code_stats': code_stats,
                'ai_stats': ai_stats
            }
    
    def export_data(self, session_id: str = None, output_file: str = None) -> str:
        """
        导出数据到JSON文件
        
        Args:
            session_id: 会话ID，如果为None则导出所有数据
            output_file: 输出文件路径
            
        Returns:
            输出文件路径
        """
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"analytics_export_{timestamp}.json"
        
        export_data = {
            'export_time': datetime.now().isoformat(),
            'session_id': session_id,
            'data': {}
        }
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if session_id:
                # 导出指定会话数据
                tables = ['user_sessions', 'learning_behaviors', 'code_operations', 
                         'ai_interactions', 'error_analysis']
                for table in tables:
                    cursor.execute(f'SELECT * FROM {table} WHERE session_id = ?', (session_id,))
                    export_data['data'][table] = [dict(row) for row in cursor.fetchall()]
            else:
                # 导出所有数据
                tables = ['user_sessions', 'learning_behaviors', 'code_operations', 
                         'ai_interactions', 'error_analysis']
                for table in tables:
                    cursor.execute(f'SELECT * FROM {table}')
                    export_data['data'][table] = [dict(row) for row in cursor.fetchall()]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
        
        self.logger.info(f"Exported data to: {output_file}")
        return output_file

# 全局分析器实例
analytics = SQLiteAnalytics()
