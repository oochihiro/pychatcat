# -*- coding: utf-8 -*-
"""
优化的AI助手界面
DeepSeek品牌风格，圆角气泡，清晰配色
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, Canvas, filedialog
import threading
from datetime import datetime
import json
import os
from core.deepseek_client import AIClientManager
from integrations.sqlite_integration import sqlite_integration

class PixelAIAssistant(tk.Frame):
    """优化的AI助手"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # 对话历史
        self.conversation_history = []
        self.ai_client = AIClientManager()
        
        # 加载状态
        self.is_loading = False
        self.loading_animation_running = False
        self.loading_dots = 0
        
        self.setup_ui()
        self.setup_conversation_context_menu()
        # 暂时禁用对话历史加载，避免损坏文件导致崩溃
        # self.load_conversation_history()
        
    def setup_ui(self):
        """设置用户界面"""
        # 主容器
        main_frame = tk.Frame(self, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 顶部控制栏 - DeepSeek品牌蓝色
        top_frame = tk.Frame(main_frame, bg='#2563EB', height=35)
        top_frame.pack(fill=tk.X)
        top_frame.pack_propagate(False)
        
        # 左侧：AI服务状态
        left_frame = tk.Frame(top_frame, bg='#2563EB')
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=5)
        
        tk.Label(
            left_frame,
            text="🤖 AI服务:",
            font=('Microsoft YaHei', 9, 'bold'),
            bg='#2563EB',
            fg='white'
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.service_label = tk.Label(
            left_frame,
            text="DeepSeek AI",
            font=('Microsoft YaHei', 9, 'bold'),
            bg='#2563EB',
            fg='#FCD34D'
        )
        self.service_label.pack(side=tk.LEFT, padx=(0, 8))
        
        # 状态指示器
        self.status_canvas = Canvas(left_frame, width=12, height=12, bg='#2563EB', highlightthickness=0)
        self.status_canvas.pack(side=tk.LEFT)
        self.status_indicator = self.status_canvas.create_oval(2, 2, 10, 10, fill='#10B981', outline='')
        
        # 中间：学习模式
        middle_frame = tk.Frame(top_frame, bg='#2563EB')
        middle_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        
        tk.Label(
            middle_frame,
            text="📚 模式:",
            font=('Microsoft YaHei', 9),
            bg='#2563EB',
            fg='white'
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.learning_mode = tk.StringVar(value="基础")
        mode_combo = ttk.Combobox(
            middle_frame,
            textvariable=self.learning_mode,
            values=["基础", "进阶", "实战", "调试"],
            state="readonly",
            width=8,
            font=('Microsoft YaHei', 9)
        )
        mode_combo.pack(side=tk.LEFT)
        
        # 右侧：操作按钮
        right_frame = tk.Frame(top_frame, bg='#2563EB')
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=8, pady=5)
        
        # 服务状态按钮
        status_btn = tk.Button(
            right_frame,
            text="📡 状态",
            command=self.show_service_status,
            font=('Microsoft YaHei', 8),
            bg='#60A5FA',
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=8,
            pady=2,
            borderwidth=0
        )
        status_btn.pack(side=tk.RIGHT, padx=2)
        
        # 保存对话按钮
        save_btn = tk.Button(
            right_frame,
            text="💾 保存",
            command=self.save_conversation,
            font=('Microsoft YaHei', 8),
            bg='#34D399',
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=8,
            pady=2,
            borderwidth=0
        )
        save_btn.pack(side=tk.RIGHT, padx=2)
        
        # 清空对话按钮
        clear_btn = tk.Button(
            right_frame,
            text="🗑️ 清空",
            command=self.clear_conversation,
            font=('Microsoft YaHei', 8),
            bg='#F87171',
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=8,
            pady=2,
            borderwidth=0
        )
        clear_btn.pack(side=tk.RIGHT, padx=2)
        
        # 创建可调整大小的面板
        self.ai_paned = ttk.PanedWindow(main_frame, orient='vertical')
        self.ai_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 对话记录区域 - 可调整大小
        conv_frame = tk.Frame(self.ai_paned, bg='#F9FAFB', relief='solid', borderwidth=1)
        self.ai_paned.add(conv_frame, weight=3)  # 给对话区域更多权重
        
        # 对话文本区域 - 可扩展
        self.conversation_text = tk.Text(
            conv_frame,
            wrap=tk.WORD,
            font=('Microsoft YaHei', 10),
            bg='#F9FAFB',
            fg='#1F2937',
            state=tk.NORMAL,
            relief='flat',
            borderwidth=0,
            padx=10,
            pady=10,
            cursor='arrow',
            exportselection=True
        )
        
        # 滚动条
        scrollbar = tk.Scrollbar(conv_frame, command=self.conversation_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.conversation_text.config(yscrollcommand=scrollbar.set)
        self.conversation_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 配置文本标签
        self.setup_text_tags()
        
        # ============ 用户输入区域 - 固定在底部 ============
        # 输入区域容器 - 固定在PanedWindow底部
        input_outer_container = tk.Frame(self.ai_paned, bg='white', relief='solid', borderwidth=1)
        self.ai_paned.add(input_outer_container, weight=1)  # 给输入区域固定权重
        
        # 输入提示（简化版，无图标）
        tk.Label(
            input_outer_container,
            text="请在下方输入框中输入您的问题：",
            font=('Microsoft YaHei', 10),
            bg='white',
            fg='#374151'
        ).pack(anchor='w', padx=10, pady=(8, 5))
        
        # 输入框和按钮的容器 - 使用grid布局实现响应式
        input_container = tk.Frame(input_outer_container, bg='white')
        input_container.pack(fill=tk.X, padx=10, pady=(0, 8))
        
        # 配置grid权重
        input_container.grid_columnconfigure(0, weight=1)  # 输入框列权重为1
        input_container.grid_columnconfigure(1, weight=0)  # 按钮列固定宽度
        input_container.grid_rowconfigure(0, weight=1)     # 行权重
        
        # 输入框 - 使用grid布局
        self.input_text = tk.Text(
            input_container,
            height=3,  # 减少高度以适应小窗口
            font=('Microsoft YaHei', 10),  # 稍微减小字体
            bg='white',
            fg='#1F2937',
            relief='solid',
            borderwidth=1,  # 减少边框宽度
            padx=8,
            pady=5,
            wrap=tk.WORD,
            insertbackground='#3B82F6',
            insertwidth=2
        )
        self.input_text.grid(row=0, column=0, sticky='ew', padx=(0, 8), pady=0)
        
        # 发送按钮 - 使用grid布局，固定尺寸
        self.send_button = tk.Button(
            input_container,
            text="发送",
            command=self.send_message,
            font=('Microsoft YaHei', 10, 'bold'),
            bg='#3B82F6',
            fg='white',
            activebackground='#2563EB',
            activeforeground='white',
            relief='raised',
            cursor='hand2',
            width=6,
            borderwidth=1  # 减少边框宽度
        )
        self.send_button.grid(row=0, column=1, sticky='nsew', padx=(0, 0), pady=0)
        
        # 绑定事件
        self.input_text.bind('<KeyPress>', self.on_key_press)
        self.input_text.bind('<Control-Return>', self.on_ctrl_enter)
        self.input_text.bind('<Control-Key-Return>', self.on_ctrl_enter)
        
        # 焦点效果 - 输入框获得焦点时边框变化
        self.input_text.bind('<FocusIn>', lambda e: self.input_text.config(borderwidth=3, relief='solid'))
        self.input_text.bind('<FocusOut>', lambda e: self.input_text.config(borderwidth=2, relief='solid'))
        
        # 设置初始面板大小比例
        self.setup_panel_sizes()
        
        # 绑定窗口大小变化事件
        self.bind('<Configure>', self.on_window_resize)
        
        # 添加欢迎消息
        self.add_welcome_message()
        
        # 更新服务状态
        self.update_status_display()
    
    def setup_panel_sizes(self):
        """设置初始面板大小比例"""
        try:
            # 等待界面真正映射后再调整，避免 sashpos 报错
            self.bind('<Map>', lambda e: self.after_idle(self._adjust_panel_sizes))
            self.after(150, self._adjust_panel_sizes)
        except Exception as e:
            print(f"设置面板大小失败: {e}")
    
    def _adjust_panel_sizes(self):
        """调整面板大小"""
        try:
            if not self.ai_paned.winfo_ismapped():
                # 未映射时再延迟一次
                self.after(120, self._adjust_panel_sizes)
                return
            
            self.ai_paned.update_idletasks()
            ai_height = self.ai_paned.winfo_height()
            if ai_height <= 100:
                # 太早了，再等一等
                self.after(120, self._adjust_panel_sizes)
                return

            # 设置对话区域占80%，输入区域占20%，并设置下限
            min_conv_height = 200
            min_input_height = 80
            if ai_height < min_conv_height + min_input_height:
                conv_height = int(ai_height * 0.7)
            else:
                conv_height = max(min_conv_height, int(ai_height * 0.8))

            # ttk.PanedWindow 使用 sashpos(index, newpos)
            self.ai_paned.sashpos(0, conv_height)
        except Exception as e:
            print(f"调整面板大小失败: {e}")
    
    def on_window_resize(self, event):
        """窗口大小变化时的处理"""
        # 只处理主窗口的大小变化
        if event.widget == self:
            # 延迟调整，避免频繁调整
            self.after(200, self._adjust_panel_sizes)
    
    def on_key_press(self, event):
        """按键事件处理 - 检测 Ctrl+Enter"""
        # Windows: state=12 或 state=4 表示Ctrl键
        # 检测 Ctrl+Enter 组合键
        if (event.state & 0x4 or event.state & 0xC) and event.keysym == 'Return':
            self.after(10, self.send_message)  # 延迟执行避免冲突
            return 'break'
    
    def on_ctrl_enter(self, event):
        """Ctrl+Enter事件处理"""
        self.after(10, self.send_message)  # 延迟执行
        return 'break'  # 阻止默认行为
        
    def setup_text_tags(self):
        """设置文本标签样式 - 圆角气泡"""
        # 用户消息气泡 - 灰色系（进一步缩小间距）
        self.conversation_text.tag_configure("user_bubble",
                                            background='#E5E7EB',
                                            foreground='#1F2937',
                                            font=('Microsoft YaHei', 10),
                                            lmargin1=10,
                                            lmargin2=10,
                                            rmargin=200,  # 右边距较大，形成左对齐效果
                                            spacing1=1,
                                            spacing3=1,
                                            borderwidth=1,
                                            relief='solid')
        
        # AI消息气泡 - 浅蓝渐变系（进一步缩小间距）
        self.conversation_text.tag_configure("ai_bubble",
                                            background='#DBEAFE',
                                            foreground='#1E40AF',
                                            font=('Microsoft YaHei', 10),
                                            lmargin1=15,
                                            lmargin2=15,
                                            rmargin=100,
                                            spacing1=1,  # 进一步缩小
                                            spacing2=0,  # 进一步缩小
                                            spacing3=1,  # 进一步缩小
                                            borderwidth=1,
                                            relief='solid')
        
        # 用户标签
        self.conversation_text.tag_configure("user_label",
                                            foreground='#6B7280',
                                            font=('Microsoft YaHei', 9, 'bold'))
        
        # AI标签
        self.conversation_text.tag_configure("ai_label",
                                            foreground='#3B82F6',
                                            font=('Microsoft YaHei', 9, 'bold'))
        
        # 时间戳
        self.conversation_text.tag_configure("timestamp",
                                            foreground='#9CA3AF',
                                            font=('Microsoft YaHei', 8))
        
        # 加载状态
        self.conversation_text.tag_configure("loading",
                                            foreground='#F59E0B',
                                            font=('Microsoft YaHei', 10, 'bold'),
                                            justify='center')
        
        # 分隔线
        self.conversation_text.tag_configure("separator",
                                            foreground='#E5E7EB')
    
    def add_welcome_message(self):
        """添加欢迎消息 - 简洁版"""
        welcome_msg = """✨ 欢迎使用AI学习助手！我是您的Python学习伙伴，基于 DeepSeek AI 驱动。

我可以帮您：
💡 解答Python语法问题
📝 提供适合左侧编辑器的代码示例
🐛 调试代码
🎯 分享编程最佳实践

请在下方输入框中输入您的问题，按 Ctrl+Enter 或点击发送按钮即可开始对话~"""
        
        self.add_assistant_message(welcome_msg)
        
    def send_message(self):
        """发送用户消息"""
        if self.is_loading:
            return
            
        message = self.input_text.get(1.0, tk.END).strip()
        
        if not message:
            return
        
        # 清空输入框
        self.input_text.delete(1.0, tk.END)
        
        # 添加用户消息
        self.add_user_message(message)
        
        # 开始加载状态
        self.start_loading()
        
        # 异步处理AI回复
        threading.Thread(target=self.process_ai_response, args=(message,), daemon=True).start()
    
    def add_user_message(self, message):
        """添加用户消息 - 左对齐显示"""
        timestamp = datetime.now().strftime("%H:%M")
        
        # 分隔线
        self.conversation_text.insert(tk.END, "\n", "separator")
        
        # 用户标签和时间戳（左对齐）
        self.conversation_text.insert(tk.END, "👤 您 ", "user_label")
        self.conversation_text.insert(tk.END, f"[{timestamp}]\n", "timestamp")
        
        # 用户消息气泡（左对齐）
        self.conversation_text.insert(tk.END, f"{message}\n", "user_bubble")
        
        self.conversation_text.see(tk.END)
        
        # 保存到历史记录
        self.conversation_history.append({
            'type': 'user',
            'message': message,
            'timestamp': timestamp
        })
    
    def add_assistant_message(self, message):
        """添加AI助手回复 - 圆角气泡"""
        timestamp = datetime.now().strftime("%H:%M")
        
        # 分隔线
        self.conversation_text.insert(tk.END, "\n", "separator")
        
        # AI标签和时间戳 - 简化显示，避免遮挡
        self.conversation_text.insert(tk.END, f"AI助手 ", "ai_label")
        self.conversation_text.insert(tk.END, f"[{timestamp}]\n", "timestamp")
        
        # AI消息气泡
        self.conversation_text.insert(tk.END, f"{message}\n", "ai_bubble")
        
        self.conversation_text.see(tk.END)
        
        # 保存到历史记录
        self.conversation_history.append({
            'type': 'assistant',
            'message': message,
            'timestamp': timestamp
        })
        
        # 保存对话历史
        self.save_conversation_history()
    
    def process_ai_response(self, user_message):
        """处理AI回复"""
        try:
            # 构建上下文
            context = f"你是一个专业的Python学习助手，当前学习模式：{self.learning_mode.get()}。请用简洁、专业的方式回答问题。"
            
            # 获取AI回复
            response = self.ai_client.get_response(user_message, context)
            
            # 在主线程中显示回复并停止加载
            self.after(0, lambda: self.stop_loading())
            self.after(0, lambda: self.add_assistant_message(response))
            
        except Exception as e:
            error_msg = f"❌ 处理请求时出现错误：{str(e)}\n\n请检查网络连接或API设置。"
            self.after(0, lambda: self.stop_loading())
            self.after(0, lambda: self.add_assistant_message(error_msg))
            # 记录一次 FC 行为（本地AI调用失败）
            try:
                sqlite_integration.log_behavior('FC', additional_data={
                    'stage': 'ai_client',
                    'error': str(e)
                })
            except Exception:
                pass
    
    def start_loading(self):
        """开始加载状态"""
        self.is_loading = True
        self.loading_dots = 0
        
        # 禁用发送按钮（输入框保持可用，但不响应发送）
        self.send_button.config(state=tk.DISABLED, text="⏳\n\n思考中\n...", bg='#9CA3AF')
        
        # 显示加载消息
        self.show_loading_message()
        
        # 启动加载动画
        self.loading_animation_running = True
        self.animate_loading()
        
    def stop_loading(self):
        """停止加载状态"""
        self.is_loading = False
        self.loading_animation_running = False
        
        # 启用发送按钮
        self.send_button.config(state=tk.NORMAL, text="📤\n\n发送\n消息", bg='#3B82F6')
        
        # 移除加载消息
        self.remove_loading_message()
    
    def show_loading_message(self):
        """显示加载消息"""
        # 添加加载提示
        self.conversation_text.insert(tk.END, "\n🔄 AI正在思考", "loading")
        
        # 标记加载消息的位置
        self.loading_start = self.conversation_text.index("end-2c linestart")
        
        self.conversation_text.see(tk.END)
        
    def remove_loading_message(self):
        """移除加载消息"""
        try:
            if hasattr(self, 'loading_start'):
                # 删除加载消息
                end_pos = self.conversation_text.index("end-1c")
                self.conversation_text.delete(self.loading_start, end_pos)
        except:
            pass
    
    def animate_loading(self):
        """加载动画"""
        if not self.loading_animation_running:
            return
            
        # 更新加载点数
        self.loading_dots = (self.loading_dots + 1) % 4
        dots = "." * self.loading_dots
        
        try:
            if hasattr(self, 'loading_start'):
                # 找到加载文本
                thinking_text = "🔄 AI正在思考"
                current_pos = self.conversation_text.search(thinking_text, self.loading_start, tk.END)
                if current_pos:
                    # 计算点的开始位置
                    dots_start = f"{current_pos}+{len(thinking_text)}c"
                    line_end = f"{current_pos} lineend"
                    
                    # 删除旧的点
                    self.conversation_text.delete(dots_start, line_end)
                    
                    # 插入新的点
                    self.conversation_text.insert(dots_start, dots, "loading")
            
            self.conversation_text.see(tk.END)
            
        except:
            pass
        
        # 继续动画
        if self.loading_animation_running:
            self.after(500, self.animate_loading)
    
    def setup_conversation_context_menu(self):
        """设置对话区域的右键菜单"""
        self.conversation_menu = tk.Menu(self.conversation_text, tearoff=0)
        self.conversation_menu.add_command(label="📋 复制", command=self.copy_conversation_text)
        self.conversation_menu.add_command(label="🔲 全选", command=self.select_all_conversation)
        self.conversation_menu.add_separator()
        self.conversation_menu.add_command(label="🗑️ 清空对话", command=self.clear_conversation)
        self.conversation_menu.add_command(label="💾 保存对话", command=self.save_conversation)
        
        self.conversation_text.bind('<Button-3>', self.show_conversation_menu)
        
        # 绑定选中事件以改变选中颜色
        self.conversation_text.bind('<<Selection>>', self.on_selection_change)
        
        # 绑定按键事件，防止删除和修改内容
        self.conversation_text.bind('<Key>', self.on_conversation_key)
    
    def on_conversation_key(self, event):
        """对话区域按键事件 - 只允许 Ctrl+C 复制，禁止其他修改"""
        # 允许的操作：Ctrl+C (复制), Ctrl+A (全选)
        if event.state & 0x4:  # Ctrl 键按下
            if event.keysym in ['c', 'C', 'a', 'A']:
                return  # 允许复制和全选
        
        # 允许方向键和选择操作
        if event.keysym in ['Up', 'Down', 'Left', 'Right', 'Home', 'End', 'Prior', 'Next']:
            return  # 允许导航
            
        # 允许 Shift+方向键（选择文本）
        if event.state & 0x1 and event.keysym in ['Up', 'Down', 'Left', 'Right']:
            return
        
        # 禁止所有其他按键（包括删除、退格、输入等）
        return 'break'
    
    def on_selection_change(self, event=None):
        """选中文本时改变颜色"""
        try:
            # 移除之前的选中标签
            self.conversation_text.tag_remove("custom_sel", "1.0", tk.END)
            
            # 获取选中范围
            if self.conversation_text.tag_ranges(tk.SEL):
                start = self.conversation_text.index(tk.SEL_FIRST)
                end = self.conversation_text.index(tk.SEL_LAST)
                
                # 添加自定义选中标签
                self.conversation_text.tag_add("custom_sel", start, end)
                self.conversation_text.tag_config("custom_sel", 
                                                 background='#0078d7', 
                                                 foreground='white')
                # 提升标签优先级
                self.conversation_text.tag_raise("custom_sel")
        except:
            pass
    
    def show_conversation_menu(self, event):
        """显示对话菜单"""
        try:
            self.conversation_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.conversation_menu.grab_release()
    
    def copy_conversation_text(self):
        """复制对话文本"""
        try:
            selected_text = self.conversation_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(selected_text)
        except:
            pass
    
    def select_all_conversation(self):
        """全选对话文本"""
        self.conversation_text.tag_add(tk.SEL, "1.0", tk.END)
        self.conversation_text.mark_set(tk.INSERT, "1.0")
        self.conversation_text.see(tk.INSERT)
    
    def clear_conversation(self):
        """清空对话"""
        result = messagebox.askyesno("确认清空", "确定要清空所有对话记录吗？")
        if result:
            self.conversation_text.delete("1.0", tk.END)
            self.conversation_history.clear()
            self.add_welcome_message()
    
    def save_conversation(self):
        """保存对话 - 让用户选择保存路径"""
        try:
            # 检查是否有对话记录
            if not self.conversation_history:
                messagebox.showwarning("提示", "没有对话记录可保存！")
                return
            
            # 生成默认文件名
            default_filename = f"Python学习助手对话记录_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            # 打开文件保存对话框
            file_path = filedialog.asksaveasfilename(
                title="保存对话记录",
                defaultextension=".txt",
                filetypes=[
                    ("文本文件", "*.txt"),
                    ("JSON文件", "*.json"),
                    ("所有文件", "*.*")
                ],
                initialfile=default_filename
            )
            
            # 如果用户取消了保存
            if not file_path:
                return
            
            # 根据文件扩展名决定保存格式
            file_extension = file_path.lower().split('.')[-1]
            
            if file_extension == 'json':
                # 保存为JSON格式
                save_data = {
                    "metadata": {
                        "title": "Python学习助手 - 对话记录",
                        "save_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "save_path": file_path,
                        "total_messages": len(self.conversation_history),
                        "user_messages": sum(1 for record in self.conversation_history if record['type'] == 'user'),
                        "ai_messages": sum(1 for record in self.conversation_history if record['type'] == 'ai')
                    },
                    "conversations": self.conversation_history
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, ensure_ascii=False, indent=2)
            else:
                # 保存为文本格式
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("=" * 60 + "\n")
                    f.write("Python学习助手 - 对话记录\n")
                    f.write(f"保存时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"保存路径: {file_path}\n")
                    f.write("=" * 60 + "\n\n")
                    
                    for record in self.conversation_history:
                        role = "您" if record['type'] == 'user' else "AI助手"
                        f.write(f"[{record['timestamp']}] {role}:\n")
                        f.write(f"{record['message']}\n")
                        f.write("-" * 60 + "\n\n")
                    
                    # 添加统计信息
                    f.write("\n" + "=" * 60 + "\n")
                    f.write("对话统计\n")
                    f.write("=" * 60 + "\n")
                    f.write(f"总对话轮数: {len(self.conversation_history)}\n")
                    user_messages = sum(1 for record in self.conversation_history if record['type'] == 'user')
                    ai_messages = sum(1 for record in self.conversation_history if record['type'] == 'ai')
                    f.write(f"用户消息: {user_messages} 条\n")
                    f.write(f"AI回复: {ai_messages} 条\n")
                    f.write("=" * 60 + "\n")
            
            messagebox.showinfo("保存成功", f"对话记录已保存到：\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("保存失败", f"保存对话记录时出错：{str(e)}")
    
    def save_conversation_history(self):
        """保存对话历史到文件"""
        try:
            history_file = "data/conversation_history.json"
            os.makedirs(os.path.dirname(history_file), exist_ok=True)
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存对话历史失败：{e}")
    
    def load_conversation_history(self):
        """加载对话历史记录"""
        try:
            history_file = "data/conversation_history.json"
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    loaded_history = json.load(f)
                    
                # 只加载最近的10条记录
                if len(loaded_history) > 10:
                    self.conversation_history = loaded_history[-10:]
                else:
                    self.conversation_history = loaded_history
                
        except Exception as e:
            print(f"加载对话历史失败：{e}")
    
    def update_status_display(self):
        """更新状态显示和指示器"""
        try:
            if self.ai_client.test_connection():
                self.service_label.config(text="DeepSeek AI", fg='#FCD34D')
                # 绿色指示器 - 连接
                self.status_canvas.itemconfig(self.status_indicator, fill='#10B981')
            else:
                self.service_label.config(text="本地助手", fg='#FCA5A5')
                # 红色指示器 - 断开
                self.status_canvas.itemconfig(self.status_indicator, fill='#EF4444')
        except:
            self.service_label.config(text="本地助手", fg='#FCA5A5')
            # 红色指示器 - 断开
            self.status_canvas.itemconfig(self.status_indicator, fill='#EF4444')
    
    def show_service_status(self):
        """显示服务状态"""
        try:
            if self.ai_client.test_connection():
                status_msg = """✅ DeepSeek AI 服务状态

🌐 连接状态: 正常
🤖 API服务: 可用
📡 模型: deepseek-chat
⚡ 响应: 实时

您可以正常使用AI功能。"""
            else:
                status_msg = """⚠️ DeepSeek AI 服务状态

🌐 连接状态: 不可用
🤖 API服务: 离线
📡 模式: 本地助手

请检查网络连接或API设置。"""
        except Exception as e:
            status_msg = f"""❌ 服务状态检查失败

错误信息：{str(e)}

请检查网络连接或联系管理员。"""
        
        messagebox.showinfo("AI服务状态", status_msg)