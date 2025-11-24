#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, scrolledtext


class DebuggerPanel(tk.Frame):
    """调试器面板 - 显示变量和堆栈信息"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        
        # 调试状态
        self.current_line = 0
        self.local_vars = {}
        self.call_stack = []
        self.is_debugging = False
        
    def setup_ui(self):
        """设置调试器界面"""
        self.configure(bg='white')
        
        # 创建Notebook来组织不同的调试信息
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 变量面板
        self.setup_variables_tab(notebook)
        
        # 堆栈面板
        self.setup_stack_tab(notebook)
        
        # 调试信息面板
        self.setup_debug_info_tab(notebook)
        
    def setup_variables_tab(self, notebook):
        """设置变量标签页"""
        # 变量框架
        var_frame = ttk.Frame(notebook)
        notebook.add(var_frame, text="变量")
        
        # 变量列表
        var_container = tk.Frame(var_frame, bg='white')
        var_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 变量标题
        var_title = tk.Label(
            var_container,
            text="局部变量",
            font=('Microsoft YaHei', 10, 'bold'),
            bg='white',
            fg='#2563EB'
        )
        var_title.pack(anchor='w', pady=(0, 5))
        
        # 变量显示区域
        self.variables_text = scrolledtext.ScrolledText(
            var_container,
            height=8,
            font=('Consolas', 9),
            bg='#f8f9fa',
            fg='#212529',
            wrap=tk.WORD,
            state=tk.DISABLED,
            padx=8,
            pady=5
        )
        self.variables_text.pack(fill=tk.BOTH, expand=True)
        
    def setup_stack_tab(self, notebook):
        """设置堆栈标签页"""
        # 堆栈框架
        stack_frame = ttk.Frame(notebook)
        notebook.add(stack_frame, text="调用堆栈")
        
        # 堆栈容器
        stack_container = tk.Frame(stack_frame, bg='white')
        stack_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 堆栈标题
        stack_title = tk.Label(
            stack_container,
            text="调用堆栈",
            font=('Microsoft YaHei', 10, 'bold'),
            bg='white',
            fg='#2563EB'
        )
        stack_title.pack(anchor='w', pady=(0, 5))
        
        # 堆栈显示区域
        self.stack_text = scrolledtext.ScrolledText(
            stack_container,
            height=8,
            font=('Consolas', 9),
            bg='#f8f9fa',
            fg='#212529',
            wrap=tk.WORD,
            state=tk.DISABLED,
            padx=8,
            pady=5
        )
        self.stack_text.pack(fill=tk.BOTH, expand=True)
        
    def setup_debug_info_tab(self, notebook):
        """设置调试信息标签页"""
        # 调试信息框架
        debug_frame = ttk.Frame(notebook)
        notebook.add(debug_frame, text="调试信息")
        
        # 调试信息容器
        debug_container = tk.Frame(debug_frame, bg='white')
        debug_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 调试信息标题
        debug_title = tk.Label(
            debug_container,
            text="调试状态",
            font=('Microsoft YaHei', 10, 'bold'),
            bg='white',
            fg='#2563EB'
        )
        debug_title.pack(anchor='w', pady=(0, 5))
        
        # 调试信息显示区域
        self.debug_text = scrolledtext.ScrolledText(
            debug_container,
            height=8,
            font=('Consolas', 9),
            bg='#f8f9fa',
            fg='#212529',
            wrap=tk.WORD,
            state=tk.DISABLED,
            padx=8,
            pady=5
        )
        self.debug_text.pack(fill=tk.BOTH, expand=True)
        
        # 设置文本标签样式
        self.setup_text_tags()
        
    def update_debug_info(self, current_line, local_vars, breakpoint_hit=False):
        """更新调试信息"""
        self.current_line = current_line
        self.local_vars = local_vars.copy() if local_vars else {}
        self.is_debugging = True
        
        # 更新变量显示
        self.update_variables_display()
        
        # 更新调试信息显示
        self.update_debug_status(current_line, breakpoint_hit)
        
    def update_variables_display(self):
        """更新变量显示"""
        self.variables_text.config(state=tk.NORMAL)
        self.variables_text.delete(1.0, tk.END)
        
        if self.local_vars:
            # 按变量名排序显示
            for var_name, var_value in sorted(self.local_vars.items()):
                # 格式化变量值
                if isinstance(var_value, str):
                    display_value = f'"{var_value}"'
                else:
                    display_value = repr(var_value)
                
                # 显示变量信息
                var_info = f"{var_name} = {display_value}\n"
                self.variables_text.insert(tk.END, var_info)
                
                # 根据变量类型设置颜色
                if isinstance(var_value, str):
                    self.variables_text.tag_add("string", f"end-{len(var_info)}c", "end-1c")
                elif isinstance(var_value, (int, float)):
                    self.variables_text.tag_add("number", f"end-{len(var_info)}c", "end-1c")
                elif isinstance(var_value, bool):
                    self.variables_text.tag_add("boolean", f"end-{len(var_info)}c", "end-1c")
        else:
            self.variables_text.insert(tk.END, "暂无局部变量")
            
        self.variables_text.config(state=tk.DISABLED)
        
    def update_debug_status(self, current_line, breakpoint_hit=False):
        """更新调试状态显示"""
        self.debug_text.config(state=tk.NORMAL)
        self.debug_text.delete(1.0, tk.END)
        
        # 调试状态信息
        status_info = f"当前行号: {current_line}\n"
        status_info += f"调试状态: {'暂停' if breakpoint_hit else '运行'}\n"
        status_info += f"变量数量: {len(self.local_vars)}\n"
        
        if breakpoint_hit:
            status_info += "\n🛑 断点命中，程序暂停\n"
            status_info += "使用调试菜单继续执行\n"
        else:
            status_info += "\n▶️ 程序正在运行\n"
            
        self.debug_text.insert(tk.END, status_info)
        self.debug_text.config(state=tk.DISABLED)
        
    def show_stack_info(self):
        """显示堆栈信息"""
        self.stack_text.config(state=tk.NORMAL)
        self.stack_text.delete(1.0, tk.END)
        
        # 模拟调用堆栈信息
        stack_info = f"调用堆栈 (第 {self.current_line} 行):\n\n"
        stack_info += f"1. 主程序 - 行 {self.current_line}\n"
        stack_info += "   文件: <string>\n"
        stack_info += "   函数: <module>\n\n"
        
        if self.local_vars:
            stack_info += "局部变量:\n"
            for var_name, var_value in self.local_vars.items():
                stack_info += f"  {var_name}: {type(var_value).__name__}\n"
        
        self.stack_text.insert(tk.END, stack_info)
        self.stack_text.config(state=tk.DISABLED)
        
    def clear(self):
        """清除调试信息"""
        # 清除所有显示
        for text_widget in [self.variables_text, self.stack_text, self.debug_text]:
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            text_widget.config(state=tk.DISABLED)
        
        # 重置状态
        self.current_line = 0
        self.local_vars = {}
        self.call_stack = []
        self.is_debugging = False
        
    def add_breakpoint_info(self, line_num, code_line):
        """添加断点信息"""
        self.debug_text.config(state=tk.NORMAL)
        self.debug_text.insert(tk.END, f"\n断点: 第 {line_num} 行\n")
        self.debug_text.insert(tk.END, f"代码: {code_line.strip()}\n")
        self.debug_text.config(state=tk.DISABLED)
        
    def setup_text_tags(self):
        """设置文本标签样式"""
        # 字符串样式
        self.variables_text.tag_configure("string", foreground="#008000")
        # 数字样式
        self.variables_text.tag_configure("number", foreground="#FF8C00")
        # 布尔值样式
        self.variables_text.tag_configure("boolean", foreground="#800080")