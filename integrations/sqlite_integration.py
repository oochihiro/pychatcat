#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite数据采集集成 - 前端集成代码
将学习行为数据采集集成到Python学习助手中
"""

import sys
import os
import io
import time
import threading
from typing import Dict, Any

# Windows 控制台编码修复
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    try:
        # 检查stdout是否已关闭
        if not sys.stdout.closed:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        # 如果stdout已关闭或无法修改，使用默认编码
        pass

# 添加项目根目录与 core 目录到路径，兼容直接运行/打包
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
core_dir = os.path.join(root_dir, 'core')
for extra_path in (root_dir, core_dir):
    if extra_path not in sys.path:
        sys.path.append(extra_path)

# 优先使用包导入，静态分析工具可识别；若失败再退回旧路径
try:
    from core.sqlite_analytics import analytics  # type: ignore
    ANALYTICS_AVAILABLE = True
except ImportError:
    try:
        from sqlite_analytics import analytics  # type: ignore
        ANALYTICS_AVAILABLE = True
    except ImportError:
        ANALYTICS_AVAILABLE = False
        print("警告: 无法导入sqlite_analytics，数据采集功能将被禁用")

try:
    from core.user_identity import get_user_identity  # type: ignore
except ImportError:
    try:
        from user_identity import get_user_identity  # type: ignore
    except ImportError:
        get_user_identity = None

try:
    from integrations.cloud_integration import create_cloud_client
    CLOUD_CLIENT_AVAILABLE = True
except ImportError:
    CLOUD_CLIENT_AVAILABLE = False
    print("警告: 无法导入cloud_integration，云端日志功能将被禁用")

class SQLiteIntegration:
    """SQLite数据采集集成类"""
    
    def __init__(self):
        self.analytics = analytics if ANALYTICS_AVAILABLE else None
        self.enabled = ANALYTICS_AVAILABLE
        self.current_session_id = None
        self.current_user_id = "anonymous"
        self.cloud_client = create_cloud_client() if CLOUD_CLIENT_AVAILABLE else None
        self.cloud_enabled = (
            bool(self.cloud_client) and getattr(self.cloud_client, "enabled", False)
        )
        if self.cloud_enabled:
            try:
                if not sys.stdout.closed:
                    print("🌐 云端行为上报已启用")
            except (UnicodeEncodeError, ValueError, OSError, AttributeError):
                try:
                    if not sys.stdout.closed:
                        print("[云端] 云端行为上报已启用")
                except:
                    pass
        
        # 设备标识（用于上传到云端和本地会话记录）
        self.device_label = None
        if get_user_identity:
            try:
                identity = get_user_identity()
                if isinstance(identity, dict):
                    self.device_label = identity.get('device_label') or identity.get('user_id')
            except Exception:
                self.device_label = None
        if not self.device_label:
            self.device_label = 'Python_Learning_Assistant'

        # 行为开始时间记录
        self.behavior_start_times = {}
        
        # 如果启用，开始会话
        if self.enabled:
            self.start_session()

    def start_session(self, user_id: str = None):
        """开始新的学习会话"""
        if not self.enabled:
            return
        
        # 优先使用传入的user_id，如果没有则使用当前user_id
        if user_id:
            self.current_user_id = user_id
        elif not self.current_user_id or self.current_user_id == "anonymous":
            # 尝试从学生ID管理器获取
            try:
                from core.student_id_manager import get_student_id
                student_id = get_student_id()
                if student_id:
                    self.current_user_id = student_id
            except Exception:
                pass
        
        try:
            device_label = getattr(self, "device_label", None)
            self.current_session_id = self.analytics.start_session(
                self.current_user_id,
                device_label=device_label
            )
            print(f"📊 数据采集会话已开始: {self.current_session_id} (学生: {self.current_user_id})")
        except Exception as e:
            print(f"⚠️ 启动数据采集会话失败: {e}")

        if self.cloud_enabled:
            try:
                self.cloud_client.start_session(alias=self.current_user_id)
            except Exception as exc:
                print(f"⚠️ 云端会话启动失败: {exc}")
        
        # 最近活动时间（用于检测空闲行为）
        self.last_activity_time: float = time.time()
        # 最近一次剪贴板来源与内容，用于识别从哪里复制到哪里
        self.last_clipboard_source: str = "unknown"
        self.last_clipboard_content: str = ""
        self.last_clipboard_time: float = 0.0
    
    def end_session(self):
        """结束学习会话"""
        if not self.enabled or not self.current_session_id:
            return
        
        try:
            self.analytics.end_session(self.current_session_id)
            print(f"📊 数据采集会话已结束: {self.current_session_id}")
        except Exception as e:
            print(f"⚠️ 结束数据采集会话失败: {e}")
        
        if self.cloud_enabled:
            try:
                self.cloud_client.end_session()
            except Exception as exc:
                print(f"⚠️ 云端会话结束失败: {exc}")
    
    def _touch_activity(self):
        """更新最近活动时间并在长时间无操作时记录 Idle 行为"""
        if not self.enabled or not self.current_session_id:
            return
        now = time.time()
        # 如果距离上次事件超过 60 秒，记录一次 Idle 行为
        try:
            gap = now - getattr(self, "last_activity_time", None) if getattr(self, "last_activity_time", None) else None
            if gap is not None and gap >= 60:
                try:
                    if self.analytics:
                        self.analytics.log_behavior(
                            self.current_session_id,
                            'IO',
                            duration=gap,
                            additional_data={'idle_seconds': gap}
                        )
                except Exception as e:
                    print(f"⚠️ 记录空闲行为失败: {e}")
        finally:
            self.last_activity_time = now

    def record_clipboard(self, source: str, content: str):
        """记录最近一次剪贴板来源及内容"""
        self.last_clipboard_source = source
        self.last_clipboard_content = content or ""
        self.last_clipboard_time = time.time()

    def log_behavior_start(self, behavior_code: str, additional_data: Dict = None):
        """记录行为开始"""
        if not self.enabled or not self.current_session_id:
            return
        # 更新活动时间并检测是否需要记录 Idle
        self._touch_activity()
        
        self.behavior_start_times[behavior_code] = time.time()
        
        # 异步记录行为
        def log_async():
            try:
                self.analytics.log_behavior(
                    self.current_session_id, 
                    behavior_code, 
                    duration=0,  # 开始时不记录时长
                    additional_data=additional_data
                )
            except Exception as e:
                print(f"⚠️ 记录行为失败: {e}")
        
        threading.Thread(target=log_async, daemon=True).start()

        if self.cloud_enabled:
            try:
                self.cloud_client.log_behavior(behavior_code, additional_data=additional_data)
            except Exception as exc:
                print(f"⚠️ 云端行为记录失败: {exc}")
    
    def log_behavior_end(self, behavior_code: str, additional_data: Dict = None):
        """记录行为结束"""
        if not self.enabled or not self.current_session_id:
            return
        
        # 计算持续时间
        duration = None
        if behavior_code in self.behavior_start_times:
            duration = time.time() - self.behavior_start_times[behavior_code]
            del self.behavior_start_times[behavior_code]
        
        # 异步记录行为
        def log_async():
            try:
                self.analytics.log_behavior(
                    self.current_session_id, 
                    behavior_code, 
                    duration=duration,
                    additional_data=additional_data
                )
            except Exception as e:
                print(f"⚠️ 记录行为失败: {e}")
        
        threading.Thread(target=log_async, daemon=True).start()

        if self.cloud_enabled:
            try:
                self.cloud_client.log_behavior(behavior_code, duration=duration, additional_data=additional_data)
            except Exception as exc:
                print(f"⚠️ 云端行为记录失败: {exc}")
                # 记录一次 AI 相关的失败行为（FC）用于后续分析网络/平台问题
                try:
                    if self.analytics:
                        self.analytics.log_behavior(
                            self.current_session_id,
                            'FC',
                            additional_data={
                                'stage': 'cloud_behavior',
                                'error': str(exc)
                            }
                        )
                except Exception as e2:
                    print(f"⚠️ 记录FC行为失败: {e2}")
    
    def log_behavior(self, behavior_code: str, duration: float = None, additional_data: Dict = None):
        """记录学习行为"""
        if not self.enabled or not self.current_session_id:
            return
        # 更新活动时间并检测是否需要记录 Idle
        self._touch_activity()
        # 异步记录行为
        def log_async():
            try:
                self.analytics.log_behavior(
                    self.current_session_id, 
                    behavior_code, 
                    duration=duration,
                    additional_data=additional_data
                )
            except Exception as e:
                print(f"⚠️ 记录行为失败: {e}")
        
        threading.Thread(target=log_async, daemon=True).start()

        if self.cloud_enabled:
            try:
                self.cloud_client.log_behavior(behavior_code, duration=duration, additional_data=additional_data)
            except Exception as exc:
                print(f"⚠️ 云端行为记录失败: {exc}")
    
    def log_code_operation(self, operation_type: str, code: str = None, 
                          success: bool = True, error_message: str = None, 
                          execution_time: float = None, additional_data: Dict = None):
        """记录代码操作"""
        if not self.enabled or not self.current_session_id:
            return
        # 更新活动时间并检测是否需要记录 Idle
        self._touch_activity()
        # 异步记录代码操作
        def log_async():
            try:
                self.analytics.log_code_operation(
                    self.current_session_id,
                    operation_type,
                    code,
                    success,
                    error_message,
                    execution_time,
                    additional_data=additional_data
                )
            except Exception as e:
                print(f"⚠️ 记录代码操作失败: {e}")
        
        threading.Thread(target=log_async, daemon=True).start()

        if self.cloud_enabled:
            try:
                self.cloud_client.log_code_operation(
                    operation_type,
                    code=code,
                    success=success,
                    error_message=error_message,
                    execution_time=execution_time,
                )
            except Exception as exc:
                print(f"⚠️ 云端代码操作记录失败: {exc}")
    
    def log_ai_interaction(self, interaction_type: str, question: str = None,
                          response: str = None, response_time: float = None,
                          feedback_quality: str = None, additional_data: Dict = None):
        """记录AI交互"""
        if not self.enabled or not self.current_session_id:
            return
        # 更新活动时间并检测是否需要记录 Idle
        self._touch_activity()
        
        # 异步记录AI交互
        def log_async():
            try:
                self.analytics.log_ai_interaction(
                    self.current_session_id,
                    interaction_type,
                    question,
                    response,
                    response_time,
                    feedback_quality,
                    additional_data=additional_data
                )
            except Exception as e:
                print(f"⚠️ 记录AI交互失败: {e}")
        
        threading.Thread(target=log_async, daemon=True).start()

        if self.cloud_enabled:
            try:
                self.cloud_client.log_ai_interaction(
                    interaction_type,
                    question=question,
                    response=response,
                    response_time=response_time,
                    additional_data=additional_data or {},
                )
            except Exception as exc:
                print(f"⚠️ 云端AI交互失败: {exc}")
                # 记录一次 FC 行为（AI 上报失败）
                try:
                    if self.analytics:
                        self.analytics.log_behavior(
                            self.current_session_id,
                            'FC',
                            additional_data={
                                'stage': 'cloud_ai',
                                'error': str(exc)
                            }
                        )
                except Exception as e2:
                    print(f"⚠️ 记录FC行为失败: {e2}")
    
    def log_error_analysis(self, error_type: str, error_line: int,
                          error_message: str, fix_attempts: int = 0,
                          fix_success: bool = False, additional_data: Dict = None):
        """记录错误分析"""
        if not self.enabled or not self.current_session_id:
            return
        # 更新活动时间并检测是否需要记录 Idle
        self._touch_activity()
        
        # 异步记录错误分析
        def log_async():
            try:
                self.analytics.log_error_analysis(
                    self.current_session_id,
                    error_type,
                    error_line,
                    error_message,
                    fix_attempts,
                    fix_success,
                    additional_data=additional_data
                )
            except Exception as e:
                print(f"⚠️ 记录错误分析失败: {e}")
        
        threading.Thread(target=log_async, daemon=True).start()

        if self.cloud_enabled:
            try:
                self.cloud_client.log_error_analysis(
                    error_type,
                    error_line,
                    error_message,
                    fix_attempts,
                    fix_success,
                    additional_data=additional_data or {},
                )
            except Exception as exc:
                print(f"⚠️ 云端错误分析记录失败: {exc}")

# 全局集成实例
sqlite_integration = SQLiteIntegration()

def integrate_with_app(main_app):
    """将SQLite数据采集集成到主应用中"""
    if not sqlite_integration.enabled:
        print("⚠️ SQLite数据采集功能不可用")
        return
    
    print("📊 正在集成SQLite数据采集功能...")
    
    # 保存main_app引用，以便在集成函数中使用
    integrate_code_editor._main_app = main_app
    integrate_code_executor._main_app = main_app
    
    # 集成代码编辑器
    if hasattr(main_app, 'code_editor'):
        integrate_code_editor(main_app.code_editor)
    
    # 集成控制台
    if hasattr(main_app, 'console'):
        integrate_console(main_app.console)
    
    # 集成AI助手
    if hasattr(main_app, 'ai_assistant'):
        integrate_ai_assistant(main_app.ai_assistant)
    
    # 集成代码执行器（需要传入main_app以获取代码位置）
    if hasattr(main_app, 'code_executor'):
        # 修改integrate_code_executor以使用main_app
        integrate_code_executor_with_app(main_app.code_executor, main_app)
    
    # 集成调试器
    if hasattr(main_app, 'debugger_panel'):
        integrate_debugger(main_app.debugger_panel)
    
    print("✅ SQLite数据采集功能集成完成")

def integrate_code_editor(code_editor):
    """集成代码编辑器数据采集"""
    if not sqlite_integration.enabled:
        return
    
    # 保存原始的on_text_change / on_selection_change 方法
    original_on_text_change = getattr(code_editor, 'on_text_change', None)
    original_on_selection_change = getattr(code_editor, 'on_selection_change', None)
    
    def tracked_on_text_change(event=None):
        # 记录代码编写行为（使用防抖，避免每次按键都记录）
        if not hasattr(code_editor, '_last_log_time'):
            code_editor._last_log_time = 0
        
        import time
        current_time = time.time()
        # 每5秒最多记录一次代码编写行为
        if current_time - code_editor._last_log_time > 5:
            code_editor._last_log_time = current_time
            try:
                code_content = code_editor.text_area.get("1.0", "end-1c")
                # 获取当前光标位置
                cursor_pos = code_editor.text_area.index("insert")
                line_num = int(cursor_pos.split('.')[0])
                col_num = int(cursor_pos.split('.')[1])
                
                sqlite_integration.log_behavior('CP', additional_data={
                    'code_length': len(code_content),
                    'line_count': len(code_content.split('\n')),
                    'cursor_line': line_num,
                    'cursor_column': col_num,
                    'edit_type': 'typing'
                })
            except Exception as e:
                print(f"⚠️ 记录代码编写行为失败: {e}")
        
        # 调用原始方法
        if original_on_text_change:
            return original_on_text_change(event)
    
    # 替换文本变化处理
    code_editor.on_text_change = tracked_on_text_change

    # 集成代码选择行为
    def tracked_selection_change(event=None):
        # 记录选择行为（防抖，避免频繁记录）
        try:
            if not hasattr(code_editor, '_last_select_log_time'):
                code_editor._last_select_log_time = 0
            import time
            now = time.time()
            if now - code_editor._last_select_log_time < 2:
                # 2 秒内不重复记录
                if original_on_selection_change:
                    return original_on_selection_change(event)
                return

            if code_editor.text_area.tag_ranges("sel"):
                start = code_editor.text_area.index("sel.first")
                end = code_editor.text_area.index("sel.last")
                start_line = int(start.split('.')[0])
                end_line = int(end.split('.')[0])
                selected = code_editor.text_area.get("sel.first", "sel.last")
                if selected.strip():
                    sqlite_integration.log_behavior('SC', additional_data={
                        'source': 'editor',
                        'start_line': start_line,
                        'end_line': end_line,
                        'content_length': len(selected),
                        'line_count': end_line - start_line + 1
                    })
                    code_editor._last_select_log_time = now
        except Exception:
            pass
        if original_on_selection_change:
            return original_on_selection_change(event)

    code_editor.on_selection_change = tracked_selection_change
    
    # 集成断点设置
    original_toggle_breakpoint = getattr(code_editor, 'toggle_breakpoint', None)
    
    def tracked_toggle_breakpoint(line_number):
        sqlite_integration.log_behavior('DP', additional_data={
            'line_number': line_number,
            'action': 'toggle_breakpoint',
            'timestamp': time.time()
        })
        
        if original_toggle_breakpoint:
            original_toggle_breakpoint(line_number)
    
    code_editor.toggle_breakpoint = tracked_toggle_breakpoint
    
    # 集成复制粘贴操作
    def on_copy(event=None):
        try:
            selected = code_editor.text_area.get("sel.first", "sel.last")
            if selected:
                start_line = int(code_editor.text_area.index("sel.first").split('.')[0])
                end_line = int(code_editor.text_area.index("sel.last").split('.')[0])
                sqlite_integration.log_behavior('CC', additional_data={
                    'source': 'editor',
                    'start_line': start_line,
                    'end_line': end_line,
                    'content_length': len(selected),
                    'line_count': end_line - start_line + 1
                })
                # 记录剪贴板来源
                sqlite_integration.record_clipboard('editor', selected)
        except Exception:
            pass
    
    def on_paste(event=None):
        try:
            cursor_pos = code_editor.text_area.index("insert")
            line_num = int(cursor_pos.split('.')[0])
            col_num = int(cursor_pos.split('.')[1])
            # 获取剪贴板内容长度（近似）
            try:
                clipboard_content = code_editor.text_area.clipboard_get()
                content_length = len(clipboard_content)
            except:
                content_length = 0
            
            sqlite_integration.log_behavior('PC', additional_data={
                'target': 'editor',
                'line_number': line_num,
                'column_number': col_num,
                'source': getattr(sqlite_integration, 'last_clipboard_source', 'unknown'),
                'content_length': content_length
            })

            # 如果最近一次复制来源是 AI，则记录 CPC（从AI复制代码到编辑器）
            try:
                if getattr(sqlite_integration, 'last_clipboard_source', '') == 'ai':
                    sqlite_integration.log_behavior('CPC', additional_data={
                        'target': 'editor',
                        'line_number': line_num,
                        'column_number': col_num,
                        'content_length': content_length
                    })
            except Exception:
                pass
        except Exception:
            pass
    
    # 绑定复制粘贴事件
    code_editor.text_area.bind('<Control-c>', on_copy)
    code_editor.text_area.bind('<Control-v>', on_paste)
    
    # 集成代码查看（鼠标悬停）
    last_view_line = None
    view_start_time = None
    
    def on_mouse_motion(event):
        nonlocal last_view_line, view_start_time
        try:
            index = code_editor.text_area.index(f"@{event.x},{event.y}")
            line_num = int(index.split('.')[0])
            
            if line_num != last_view_line:
                # 记录上一个位置的查看时间
                if last_view_line and view_start_time:
                    duration = time.time() - view_start_time
                    if duration > 1:  # 只记录超过1秒的查看
                        sqlite_integration.log_behavior('VC', duration=duration, additional_data={
                            'line_number': last_view_line
                        })
                
                last_view_line = line_num
                view_start_time = time.time()
        except Exception:
            pass
    
    code_editor.text_area.bind('<Motion>', on_mouse_motion)

def integrate_console(console):
    """集成控制台数据采集"""
    if not sqlite_integration.enabled:
        return
    
    # 保存原始的方法
    original_append_output = console.append_output
    original_copy_text = getattr(console, "copy_text", None)
    
    def tracked_append_output(text, tag="output"):
        # 记录控制台消息阅读行为
        if "错误" in text or "Error" in text:
            # 提取错误行号
            error_line = None
            error_type = None
            import re
            match = re.search(r'line (\d+)', text)
            if match:
                error_line = int(match.group(1))
            
            # 提取错误类型
            if "SyntaxError" in text:
                error_type = "SyntaxError"
            elif "IndentationError" in text:
                error_type = "IndentationError"
            elif "NameError" in text:
                error_type = "NameError"
            elif "TypeError" in text:
                error_type = "TypeError"
            elif "ValueError" in text:
                error_type = "ValueError"
            
            sqlite_integration.log_behavior('VE', additional_data={
                'message_type': 'error',
                'error_type': error_type,
                'error_line': error_line,
                'message_length': len(text),
                'error_message': text[:200],
                'view_timestamp': time.time()
            })
        elif "警告" in text or "Warning" in text:
            sqlite_integration.log_behavior('RCM', additional_data={
                'message_type': 'warning',
                'message_length': len(text),
                'view_timestamp': time.time()
            })
        elif tag == "output" and text.strip():
            # 记录输出查看
            sqlite_integration.log_behavior('VO', additional_data={
                'output_type': tag,
                'output_length': len(text),
                'view_timestamp': time.time()
            })
        
        # 调用原始方法
        return original_append_output(text, tag)
    
    # 替换输出方法
    console.append_output = tracked_append_output

    # 集成控制台复制行为（用于识别从控制台复制到AI的操作）
    if original_copy_text is not None:
        def tracked_copy_text():
            try:
                import tkinter as tk
                selected = console.console_text.get(tk.SEL_FIRST, tk.END)
                if console.console_text.tag_ranges(tk.SEL):
                    selected = console.console_text.get(tk.SEL_FIRST, tk.SEL_LAST)
                if selected:
                    sqlite_integration.log_behavior('RCM', additional_data={
                        'message_type': 'copy',
                        'message_length': len(selected),
                        'source': 'console'
                    })
                    # 记录剪贴板来源为 console，便于之后在AI输入框粘贴时识别为 PCM
                    try:
                        sqlite_integration.record_clipboard('console', selected)
                    except Exception:
                        pass
            except Exception:
                pass
            return original_copy_text()

        console.copy_text = tracked_copy_text

def integrate_ai_assistant(ai_assistant):
    """集成AI助手数据采集"""
    if not sqlite_integration.enabled:
        return
    
    # 保存原始的send_message / on_selection_change / add_assistant_message 方法
    original_send_message = ai_assistant.send_message
    original_on_selection_change = getattr(ai_assistant, "on_selection_change", None)
    
    def tracked_send_message():
        if sqlite_integration.enabled:
            # 获取用户输入
            user_input = ai_assistant.input_text.get("1.0", "end-1c").strip()
            
            if user_input:
                # 保存最近的问题，供 read_feedback 使用
                ai_assistant._last_user_question = user_input
                
                # 记录提问行为
                sqlite_integration.log_ai_interaction(
                    'ask_question',
                    question=user_input,
                    additional_data={
                        'question_type': 'manual',
                        'question_length': len(user_input),
                        'timestamp': time.time()
                    }
                )
        
        # 调用原始方法
        return original_send_message()
    
    # 替换方法
    ai_assistant.send_message = tracked_send_message
    
    # 记录进入/离开聊天区的时间
    chat_enter_time = None
    chat_total_time = 0
    
    def on_chat_focus_in(event=None):
        nonlocal chat_enter_time
        chat_enter_time = time.time()
        sqlite_integration.log_behavior('AC', additional_data={
            'action': 'enter',
            'timestamp': time.time()
        })
    
    def on_chat_focus_out(event=None):
        nonlocal chat_enter_time, chat_total_time
        if chat_enter_time:
            duration = time.time() - chat_enter_time
            chat_total_time += duration
            sqlite_integration.log_behavior('AC', duration=duration, additional_data={
                'action': 'leave',
                'total_time': chat_total_time,
                'timestamp': time.time()
            })
            chat_enter_time = None
    
    # 绑定焦点事件
    if hasattr(ai_assistant, 'conversation_text'):
        ai_assistant.conversation_text.bind('<FocusIn>', on_chat_focus_in)
        ai_assistant.conversation_text.bind('<FocusOut>', on_chat_focus_out)
    if hasattr(ai_assistant, 'input_text'):
        ai_assistant.input_text.bind('<FocusIn>', on_chat_focus_in)
        ai_assistant.input_text.bind('<FocusOut>', on_chat_focus_out)
    
    # 集成复制 AI 代码
    def on_ai_copy(event=None):
        try:
            if hasattr(ai_assistant, 'conversation_text'):
                selected = ai_assistant.conversation_text.get("sel.first", "sel.last")
                if selected:
                    sqlite_integration.log_behavior('CAC', additional_data={
                        'source': 'ai',
                        'content_length': len(selected),
                        'content_preview': selected[:100],
                        'timestamp': time.time()
                    })
                    # 记录剪贴板来源为 ai，便于之后在编辑器粘贴时识别为 CPC
                    try:
                        sqlite_integration.record_clipboard('ai', selected)
                    except Exception:
                        pass
        except Exception:
            pass
    
    if hasattr(ai_assistant, 'conversation_text'):
        ai_assistant.conversation_text.bind('<Control-c>', on_ai_copy)

    # 集成在 AI 对话区域选中文本的行为（SAI）
    def tracked_ai_selection_change(event=None):
        try:
            import time as _t
            if not hasattr(ai_assistant, "_last_ai_select_log_time"):
                ai_assistant._last_ai_select_log_time = 0
            now = _t.time()
            if now - ai_assistant._last_ai_select_log_time < 2:
                if original_on_selection_change:
                    return original_on_selection_change(event)
                return

            if ai_assistant.conversation_text.tag_ranges("sel"):
                start = ai_assistant.conversation_text.index("sel.first")
                end = ai_assistant.conversation_text.index("sel.last")
                selected = ai_assistant.conversation_text.get("sel.first", "sel.last")
                if selected.strip():
                    sqlite_integration.log_behavior('SAI', additional_data={
                        'source': 'ai',
                        'start_index': start,
                        'end_index': end,
                        'content_length': len(selected)
                    })
                    ai_assistant._last_ai_select_log_time = now
        except Exception:
            pass
        if original_on_selection_change:
            return original_on_selection_change(event)

    if hasattr(ai_assistant, "on_selection_change"):
        ai_assistant.on_selection_change = tracked_ai_selection_change
    
    # 集成 AI 输入框粘贴行为：区分从编辑器/控制台粘贴的内容
    def on_input_paste(event=None):
        try:
            if not hasattr(ai_assistant, "input_text"):
                return
            clip = ai_assistant.input_text.clipboard_get()
            length = len(clip) if clip else 0
            source = getattr(sqlite_integration, "last_clipboard_source", "unknown")
            data = {
                'source': source,
                'content_length': length,
                'content_preview': (clip[:100] if clip else ""),
                'timestamp': time.time()
            }
            # 从编辑器粘贴代码到 AI -> PPC
            if source == 'editor':
                sqlite_integration.log_behavior('PPC', additional_data=data)
            # 从控制台粘贴错误信息到 AI -> PCM
            elif source == 'console':
                sqlite_integration.log_behavior('PCM', additional_data=data)
            else:
                # 未知来源，仍按 PPC 记录，以便后续分析
                sqlite_integration.log_behavior('PPC', additional_data=data)
        except Exception:
            pass
        # 保持默认粘贴行为
        return

    if hasattr(ai_assistant, 'input_text'):
        try:
            ai_assistant.input_text.bind('<Control-v>', lambda e: on_input_paste(e), add='+')
        except Exception:
            pass

    # 集成AI响应处理
    original_add_assistant_message = getattr(ai_assistant, 'add_assistant_message', None)
    if original_add_assistant_message:
        def tracked_add_assistant_message(message):
            # 调用原始方法
            result = original_add_assistant_message(message)
            
            # 记录AI回复时，获取对应的用户问题
            question = None
            if sqlite_integration.enabled:
                # 优先使用保存的最近问题（最准确）
                if hasattr(ai_assistant, '_last_user_question'):
                    question = ai_assistant._last_user_question
                # 如果找不到，从对话历史中查找最近一次用户消息
                elif hasattr(ai_assistant, 'conversation_history') and ai_assistant.conversation_history:
                    # 倒序查找最近一条用户消息
                    for record in reversed(ai_assistant.conversation_history):
                        if record.get('type') == 'user':
                            question = record.get('message', '')
                            break
                
                sqlite_integration.log_ai_interaction(
                    'read_feedback',
                    question=question,  # ✅ 传递对应的问题
                    response=message,
                    additional_data={
                        'response_length': len(message),
                        'view_timestamp': time.time()
                    }
                )
            
            return result
        
        ai_assistant.add_assistant_message = tracked_add_assistant_message

def integrate_code_executor_with_app(code_executor, main_app):
    """集成代码执行器数据采集（带main_app引用）"""
    if not sqlite_integration.enabled:
        return
    
    # 保存原始的execute_code方法
    original_execute_code = code_executor.execute_code
    
    def tracked_execute_code(code):
        start_time = time.time()
        
        # 获取代码位置信息（从main_app获取code_editor）
        code_range = "1-1"
        start_line = 1
        end_line = 1
        
        try:
            if code and hasattr(main_app, 'code_editor'):
                code_editor = main_app.code_editor
                # 获取选中的代码范围
                try:
                    sel_start = code_editor.text_area.index("sel.first")
                    sel_end = code_editor.text_area.index("sel.last")
                    start_line = int(sel_start.split('.')[0])
                    end_line = int(sel_end.split('.')[0])
                    code_range = f"{start_line}-{end_line}"
                except:
                    # 如果没有选中，使用全部代码
                    code_content = code_editor.text_area.get("1.0", "end-1c")
                    if code_content:
                        lines = code_content.split('\n')
                        end_line = len(lines)
                        code_range = f"1-{end_line}"
                    elif code:
                        lines = code.split('\n')
                        end_line = len(lines)
                        code_range = f"1-{end_line}"
        except:
            # 如果获取失败，使用代码本身的行数
            if code:
                lines = code.split('\n')
                end_line = len(lines)
                code_range = f"1-{end_line}"
        
        try:
            # 记录代码运行开始
            sqlite_integration.log_behavior_start('CR', additional_data={
                'code_length': len(code) if code else 0,
                'line_count': len(code.split('\n')) if code else 0,
                'start_line': start_line,
                'end_line': end_line,
                'code_range': code_range
            })
            
            # 调用原始执行方法
            result = original_execute_code(code)
            
            # 计算执行时间
            execution_time = time.time() - start_time
            
            # 记录成功的代码运行
            sqlite_integration.log_code_operation(
                'run',
                code=code,
                success=True,
                execution_time=execution_time,
                additional_data={
                    'start_line': start_line,
                    'end_line': end_line,
                    'code_range': code_range,
                    'timestamp': time.time()
                }
            )
            
            # 记录行为结束
            sqlite_integration.log_behavior_end('CR')
            
            return result
            
        except Exception as e:
            # 计算执行时间
            execution_time = time.time() - start_time
            
            # 提取错误行号
            error_line = 0
            error_msg = str(e)
            import re
            match = re.search(r'line (\d+)', error_msg)
            if match:
                error_line = int(match.group(1))
            
            # 记录失败的代码运行
            sqlite_integration.log_code_operation(
                'run',
                code=code,
                success=False,
                error_message=error_msg,
                execution_time=execution_time,
                additional_data={
                    'start_line': start_line,
                    'end_line': end_line,
                    'code_range': code_range,
                    'error_line': error_line,
                    'timestamp': time.time()
                }
            )
            
            # 记录错误分析
            sqlite_integration.log_error_analysis(
                error_type=type(e).__name__,
                error_line=error_line,
                error_message=error_msg
            )
            
            # 记录行为结束
            sqlite_integration.log_behavior_end('CR')
            
            # 重新抛出异常
            raise
    
    # 替换方法
    code_executor.execute_code = tracked_execute_code

def integrate_code_executor(code_executor):
    """集成代码执行器数据采集（兼容旧版本）"""
    # 这个函数保留用于向后兼容，实际使用integrate_code_executor_with_app
    pass

def integrate_debugger(debugger_panel):
    """集成调试器数据采集"""
    if not sqlite_integration.enabled:
        return

    # 预留：可以根据需要在调试状态更新时记录行为
    original_update_debug_info = getattr(debugger_panel, "update_debug_info", None)

    def tracked_update_debug_info(current_line, local_vars, breakpoint_hit=False):
        # 记录一次调试行为（DP），包含当前行号和是否命中断点
        try:
            sqlite_integration.log_behavior('DP', additional_data={
                'current_line': current_line,
                'breakpoint_hit': bool(breakpoint_hit),
                'local_var_count': len(local_vars) if isinstance(local_vars, dict) else 0
            })
        except Exception:
            pass
        if original_update_debug_info:
            return original_update_debug_info(current_line, local_vars, breakpoint_hit)

    if original_update_debug_info is not None:
        debugger_panel.update_debug_info = tracked_update_debug_info

# 在应用关闭时结束会话
def cleanup():
    """清理资源"""
    if sqlite_integration.enabled:
        sqlite_integration.end_session()
