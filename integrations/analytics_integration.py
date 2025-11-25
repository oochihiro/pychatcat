#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端集成代码 - 将行为追踪集成到Python学习助手中
"""

import sys
import os
import time
from typing import Dict, Any

# 添加core目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

try:
    from analytics_tracker import analytics_tracker
except ImportError:
    print("警告: 无法导入analytics_tracker，行为追踪功能将被禁用")
    analytics_tracker = None

class AnalyticsIntegration:
    """分析集成类 - 将行为追踪集成到现有组件中"""
    
    def __init__(self):
        self.tracker = analytics_tracker
        self.enabled = analytics_tracker is not None
        
        # 代码输入追踪
        self.code_input_start_time = None
        self.last_code_content = ""
    
    def track_code_editor_events(self, code_editor):
        """为代码编辑器添加行为追踪"""
        if not self.enabled:
            return
        
        # 追踪代码输入
        def on_code_change(event=None):
            if self.tracker:
                current_content = code_editor.text_area.get("1.0", tk.END).strip()
                
                # 检测输入类型
                if current_content != self.last_code_content:
                    if not self.last_code_content:  # 全新输入
                        input_type = 'manual'
                        self.code_input_start_time = time.time()
                    else:
                        # 分析输入类型
                        input_type = self._analyze_input_type(current_content, self.last_code_content)
                    
                    # 追踪输入行为
                    if self.code_input_start_time:
                        typing_duration = time.time() - self.code_input_start_time
                    else:
                        typing_duration = None
                    
                    self.tracker.track_code_input(
                        input_type=input_type,
                        code_length=len(current_content),
                        typing_duration=typing_duration,
                        auto_complete_used=False  # 可以进一步集成自动补全检测
                    )
                    
                    self.last_code_content = current_content
                    self.code_input_start_time = time.time()
        
        # 绑定事件
        if hasattr(code_editor, 'text_area'):
            code_editor.text_area.bind('<KeyRelease>', on_code_change)
            code_editor.text_area.bind('<Button-1>', lambda e: setattr(self, 'code_input_start_time', time.time()))
    
    def track_console_events(self, console):
        """为控制台添加行为追踪"""
        if not self.enabled:
            return
        
        # 保存原始的append_output方法
        original_append_output = console.append_output
        
        def tracked_append_output(text, tag="output"):
            # 调用原始方法
            result = original_append_output(text, tag)
            
            # 追踪输出事件
            if self.tracker:
                if "错误" in text or "Error" in text:
                    # 追踪错误
                    self.tracker.track_learning_behavior(
                        behavior_type='error_encountered',
                        details={'error_text': text, 'tag': tag}
                    )
                elif "建议" in text or "建议" in text:
                    # 追踪建议使用
                    self.tracker.track_learning_behavior(
                        behavior_type='suggestion_viewed',
                        details={'suggestion_text': text}
                    )
            
            return result
        
        # 替换方法
        console.append_output = tracked_append_output
    
    def track_ai_assistant_events(self, ai_assistant):
        """为AI助手添加行为追踪"""
        if not self.enabled:
            return
        
        # 保存原始的send_message方法
        original_send_message = ai_assistant.send_message
        
        def tracked_send_message():
            if self.tracker:
                # 获取用户输入
                user_input = ai_assistant.input_text.get("1.0", tk.END).strip()
                
                if user_input:
                    # 记录问题发送时间
                    start_time = time.time()
                    
                    # 追踪AI交互开始
                    self.tracker.track_ai_interaction(
                        question=user_input,
                        suggestion_used=False  # 可以根据实际情况判断
                    )
                    
                    # 包装AI响应处理
                    def on_ai_response(response_text, response_time):
                        self.tracker.track_ai_interaction(
                            question=user_input,
                            response_time=response_time,
                            response_length=len(response_text),
                            suggestion_used='建议' in response_text or '建议' in response_text
                        )
                    
                    # 这里需要根据实际的AI响应机制来集成
                    # 可能需要修改AI助手的响应处理逻辑
                
                # 调用原始方法
                return original_send_message()
        
        # 替换方法
        ai_assistant.send_message = tracked_send_message
    
    def track_debugger_events(self, debugger_panel):
        """为调试器添加行为追踪"""
        if not self.enabled:
            return
        
        # 这里需要根据实际的调试器实现来添加追踪
        # 例如追踪断点设置、单步执行等操作
        pass
    
    def track_menu_usage(self, main_app):
        """追踪菜单使用情况"""
        if not self.enabled:
            return
        
        # 为菜单项添加追踪
        def create_tracked_menu_command(original_command, menu_name):
            def tracked_command():
                if self.tracker:
                    self.tracker.track_learning_behavior(
                        behavior_type='menu_usage',
                        details={'menu': menu_name}
                    )
                return original_command()
            return tracked_command
        
        # 这里需要根据实际的菜单结构来添加追踪
        # 例如：
        # main_app.file_menu.entryconfig("新建", command=create_tracked_menu_command(original_new_command, "文件-新建"))
    
    def track_code_execution(self, code_executor):
        """追踪代码执行"""
        if not self.enabled:
            return
        
        # 保存原始的execute_code方法
        original_execute_code = code_executor.execute_code
        
        def tracked_execute_code(code):
            start_time = time.time()
            
            try:
                # 调用原始执行方法
                result = original_execute_code(code)
                
                # 计算执行时间
                execution_time = time.time() - start_time
                
                # 追踪成功的代码执行
                self.tracker.track_code_run(
                    code=code,
                    success=True,
                    execution_time=execution_time
                )
                
                return result
                
            except Exception as e:
                # 计算执行时间
                execution_time = time.time() - start_time
                
                # 追踪失败的代码执行
                self.tracker.track_code_run(
                    code=code,
                    success=False,
                    error_msg=str(e),
                    execution_time=execution_time
                )
                
                # 重新抛出异常
                raise
        
        # 替换方法
        code_executor.execute_code = tracked_execute_code
    
    def track_copy_paste_events(self, text_widget, source_type='internal'):
        """追踪复制粘贴事件"""
        if not self.enabled:
            return
        
        def on_copy(event):
            try:
                # 获取选中的文本
                selected_text = text_widget.selection_get()
                
                self.tracker.track_copy_paste(
                    action='copy',
                    source=source_type,
                    content_length=len(selected_text),
                    content_type=self._classify_content_type(selected_text)
                )
            except tk.TclError:
                pass  # 没有选中文本
        
        def on_paste(event):
            try:
                # 获取剪贴板内容
                clipboard_content = text_widget.clipboard_get()
                
                self.tracker.track_copy_paste(
                    action='paste',
                    source=source_type,
                    content_length=len(clipboard_content),
                    content_type=self._classify_content_type(clipboard_content)
                )
            except tk.TclError:
                pass  # 剪贴板为空
        
        # 绑定事件
        text_widget.bind('<Control-c>', on_copy)
        text_widget.bind('<Control-v>', on_paste)
    
    def _analyze_input_type(self, current_content, previous_content):
        """分析输入类型"""
        if not previous_content:
            return 'manual'
        
        # 简单的启发式分析
        if len(current_content) - len(previous_content) > 50:
            return 'paste'  # 大量内容可能是粘贴
        elif 'import' in current_content and 'import' not in previous_content:
            return 'template'  # 添加import语句
        elif 'def ' in current_content and 'def ' not in previous_content:
            return 'template'  # 添加函数定义
        else:
            return 'manual'
    
    def _classify_content_type(self, content):
        """分类内容类型"""
        if 'def ' in content or 'class ' in content or 'import ' in content:
            return 'code'
        elif '```' in content:
            return 'ai_response'
        else:
            return 'text'
    
    def get_session_stats(self):
        """获取当前会话统计"""
        if self.enabled and self.tracker:
            return self.tracker.get_session_stats()
        return None
    
    def export_analytics_data(self, file_path=None):
        """导出分析数据"""
        if self.enabled and self.tracker:
            return self.tracker.export_data(file_path)
        return None

# 全局集成实例
analytics_integration = AnalyticsIntegration()

# 集成函数
def integrate_analytics_with_app(main_app):
    """将分析功能集成到主应用中"""
    
    # 集成代码编辑器
    if hasattr(main_app, 'code_editor'):
        analytics_integration.track_code_editor_events(main_app.code_editor)
        analytics_integration.track_copy_paste_events(main_app.code_editor.text_area, 'internal')
    
    # 集成控制台
    if hasattr(main_app, 'console'):
        analytics_integration.track_console_events(main_app.console)
    
    # 集成AI助手
    if hasattr(main_app, 'ai_assistant'):
        analytics_integration.track_ai_assistant_events(main_app.ai_assistant)
        analytics_integration.track_copy_paste_events(main_app.ai_assistant.conversation_text, 'internal')
    
    # 集成调试器
    if hasattr(main_app, 'debugger_panel'):
        analytics_integration.track_debugger_events(main_app.debugger_panel)
    
    # 集成代码执行器
    if hasattr(main_app, 'code_executor'):
        analytics_integration.track_code_execution(main_app.code_executor)
    
    # 集成菜单使用
    analytics_integration.track_menu_usage(main_app)
    
    print("✅ 行为分析功能已集成到应用中")

# 在main.py中调用此函数来启用分析功能
def enable_analytics():
    """启用分析功能"""
    return analytics_integration.enabled



