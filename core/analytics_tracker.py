#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学生行为数据追踪器
集成到Python学习助手中，收集学习行为数据
"""

import json
import time
import threading
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
import os
import uuid
from collections import defaultdict, deque

class AnalyticsTracker:
    """学生行为数据追踪器"""
    
    def __init__(self, user_id: str = None, offline_mode: bool = True):
        """
        初始化追踪器
        
        Args:
            user_id: 用户ID，如果为None则自动生成
            offline_mode: 是否启用离线模式
        """
        self.user_id = user_id or str(uuid.uuid4())
        self.offline_mode = offline_mode
        self.session_id = str(uuid.uuid4())
        self.start_time = datetime.now()
        
        # 数据存储
        self.local_data_file = "data/analytics_data.jsonl"
        self.events_buffer = deque(maxlen=1000)  # 限制内存使用
        
        # 统计数据
        self.stats = {
            'code_operations': defaultdict(int),
            'ai_interactions': defaultdict(int),
            'learning_behavior': defaultdict(int),
            'session_start': self.start_time.isoformat(),
            'last_activity': self.start_time.isoformat()
        }
        
        # API配置
        self.api_base_url = "http://localhost:8000/api"  # 可配置
        self.batch_size = 50
        self.flush_interval = 30  # 秒
        
        # 确保数据目录存在
        os.makedirs(os.path.dirname(self.local_data_file), exist_ok=True)
        
        # 启动后台线程
        self.start_background_threads()
    
    def start_background_threads(self):
        """启动后台线程"""
        # 数据上传线程
        if not self.offline_mode:
            upload_thread = threading.Thread(target=self._upload_worker, daemon=True)
            upload_thread.start()
        
        # 数据持久化线程
        save_thread = threading.Thread(target=self._save_worker, daemon=True)
        save_thread.start()
    
    def track_code_run(self, code: str, success: bool, error_msg: str = None, 
                      execution_time: float = None):
        """追踪代码运行行为"""
        event = {
            'event_type': 'code_run',
            'timestamp': datetime.now().isoformat(),
            'user_id': self.user_id,
            'session_id': self.session_id,
            'data': {
                'code_length': len(code),
                'code_lines': len(code.split('\n')),
                'success': success,
                'error_message': error_msg,
                'execution_time': execution_time,
                'has_imports': 'import ' in code,
                'has_functions': 'def ' in code,
                'has_classes': 'class ' in code,
                'has_loops': any(keyword in code for keyword in ['for ', 'while ']),
                'has_conditions': any(keyword in code for keyword in ['if ', 'elif ', 'else:'])
            }
        }
        self._add_event(event)
        self.stats['code_operations']['total_runs'] += 1
        if success:
            self.stats['code_operations']['successful_runs'] += 1
        else:
            self.stats['code_operations']['failed_runs'] += 1
    
    def track_debug_operation(self, operation_type: str, line_number: int = None,
                            breakpoints: List[int] = None, duration: float = None):
        """追踪调试操作"""
        event = {
            'event_type': 'debug_operation',
            'timestamp': datetime.now().isoformat(),
            'user_id': self.user_id,
            'session_id': self.session_id,
            'data': {
                'operation_type': operation_type,  # 'breakpoint_set', 'step_over', 'step_into', etc.
                'line_number': line_number,
                'breakpoints_count': len(breakpoints) if breakpoints else 0,
                'duration': duration
            }
        }
        self._add_event(event)
        self.stats['code_operations'][f'debug_{operation_type}'] += 1
    
    def track_copy_paste(self, action: str, source: str, content_length: int,
                        content_type: str = None):
        """
        追踪复制粘贴行为
        
        Args:
            action: 'copy' 或 'paste'
            source: 来源 ('internal' 程序内部, 'external' 外部)
            content_length: 内容长度
            content_type: 内容类型 ('code', 'text', 'ai_response')
        """
        event = {
            'event_type': 'copy_paste',
            'timestamp': datetime.now().isoformat(),
            'user_id': self.user_id,
            'session_id': self.session_id,
            'data': {
                'action': action,
                'source': source,
                'content_length': content_length,
                'content_type': content_type
            }
        }
        self._add_event(event)
        self.stats['learning_behavior'][f'{action}_{source}'] += 1
    
    def track_code_input(self, input_type: str, code_length: int, 
                        typing_duration: float = None, auto_complete_used: bool = False):
        """
        追踪代码输入行为
        
        Args:
            input_type: 'manual' 手动输入, 'template' 模板, 'example' 示例
            code_length: 代码长度
            typing_duration: 输入耗时
            auto_complete_used: 是否使用了自动补全
        """
        event = {
            'event_type': 'code_input',
            'timestamp': datetime.now().isoformat(),
            'user_id': self.user_id,
            'session_id': self.session_id,
            'data': {
                'input_type': input_type,
                'code_length': code_length,
                'typing_duration': typing_duration,
                'auto_complete_used': auto_complete_used,
                'is_original': input_type == 'manual'
            }
        }
        self._add_event(event)
        self.stats['learning_behavior'][f'input_{input_type}'] += 1
    
    def track_ai_interaction(self, question: str, response_time: float = None,
                           response_length: int = None, suggestion_used: bool = False):
        """追踪AI交互行为"""
        event = {
            'event_type': 'ai_interaction',
            'timestamp': datetime.now().isoformat(),
            'user_id': self.user_id,
            'session_id': self.session_id,
            'data': {
                'question_length': len(question),
                'question_type': self._classify_question_type(question),
                'response_time': response_time,
                'response_length': response_length,
                'suggestion_used': suggestion_used,
                'has_code_example': '```' in question or 'code' in question.lower()
            }
        }
        self._add_event(event)
        self.stats['ai_interactions']['total_questions'] += 1
        if suggestion_used:
            self.stats['ai_interactions']['suggestions_used'] += 1
    
    def track_learning_behavior(self, behavior_type: str, duration: float = None,
                              frequency: int = 1, details: Dict = None):
        """
        追踪学习行为
        
        Args:
            behavior_type: 行为类型 ('example_view', 'help_usage', 'error_fix', etc.)
            duration: 行为持续时间
            frequency: 行为频率
            details: 详细信息
        """
        event = {
            'event_type': 'learning_behavior',
            'timestamp': datetime.now().isoformat(),
            'user_id': self.user_id,
            'session_id': self.session_id,
            'data': {
                'behavior_type': behavior_type,
                'duration': duration,
                'frequency': frequency,
                'details': details or {}
            }
        }
        self._add_event(event)
        self.stats['learning_behavior'][behavior_type] += frequency
    
    def track_error_analysis(self, error_type: str, error_line: int, 
                           fix_attempts: int, success: bool):
        """追踪错误分析和修复过程"""
        event = {
            'event_type': 'error_analysis',
            'timestamp': datetime.now().isoformat(),
            'user_id': self.user_id,
            'session_id': self.session_id,
            'data': {
                'error_type': error_type,
                'error_line': error_line,
                'fix_attempts': fix_attempts,
                'fix_success': success,
                'learning_progress': self._calculate_learning_progress()
            }
        }
        self._add_event(event)
        self.stats['learning_behavior']['errors_encountered'] += 1
        if success:
            self.stats['learning_behavior']['errors_fixed'] += 1
    
    def _classify_question_type(self, question: str) -> str:
        """分类问题类型"""
        question_lower = question.lower()
        if any(keyword in question_lower for keyword in ['语法', 'syntax', '怎么', 'how']):
            return 'syntax_help'
        elif any(keyword in question_lower for keyword in ['错误', 'error', 'bug', '问题']):
            return 'error_help'
        elif any(keyword in question_lower for keyword in ['例子', 'example', '示例']):
            return 'example_request'
        elif any(keyword in question_lower for keyword in ['解释', 'explain', '为什么']):
            return 'explanation'
        else:
            return 'general'
    
    def _calculate_learning_progress(self) -> float:
        """计算学习进度"""
        total_operations = sum(self.stats['code_operations'].values())
        successful_operations = self.stats['code_operations'].get('successful_runs', 0)
        
        if total_operations == 0:
            return 0.0
        
        return min(1.0, successful_operations / total_operations)
    
    def _add_event(self, event: Dict[str, Any]):
        """添加事件到缓冲区"""
        self.events_buffer.append(event)
        self.stats['last_activity'] = datetime.now().isoformat()
    
    def _save_worker(self):
        """后台保存线程"""
        while True:
            time.sleep(self.flush_interval)
            self._flush_to_disk()
    
    def _upload_worker(self):
        """后台上传线程"""
        while True:
            time.sleep(self.flush_interval * 2)
            if not self.offline_mode:
                self._upload_batch()
    
    def _flush_to_disk(self):
        """将事件刷新到磁盘"""
        if not self.events_buffer:
            return
        
        try:
            with open(self.local_data_file, 'a', encoding='utf-8') as f:
                while self.events_buffer:
                    event = self.events_buffer.popleft()
                    f.write(json.dumps(event, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"保存分析数据失败: {e}")
    
    def _upload_batch(self):
        """批量上传数据"""
        try:
            # 这里实现API上传逻辑
            # 暂时跳过，因为需要后端API支持
            pass
        except Exception as e:
            print(f"上传分析数据失败: {e}")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """获取当前会话统计"""
        session_duration = (datetime.now() - self.start_time).total_seconds()
        
        return {
            'user_id': self.user_id,
            'session_id': self.session_id,
            'session_duration': session_duration,
            'stats': dict(self.stats),
            'events_count': len(self.events_buffer)
        }
    
    def export_data(self, file_path: str = None) -> str:
        """导出数据"""
        if not file_path:
            file_path = f"analytics_export_{self.user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            'metadata': {
                'user_id': self.user_id,
                'session_id': self.session_id,
                'export_time': datetime.now().isoformat(),
                'session_duration': (datetime.now() - self.start_time).total_seconds()
            },
            'statistics': dict(self.stats),
            'events': list(self.events_buffer)
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return file_path

# 全局追踪器实例
analytics_tracker = AnalyticsTracker()



