# -*- coding: utf-8 -*-
"""
像素动漫风控制台
"""

import tkinter as tk
from tkinter import scrolledtext

class PixelConsole(tk.Frame):
    """像素动漫风控制台"""
    
    def __init__(self, parent, code_executor):
        super().__init__(parent)
        self.code_executor = code_executor
        
        self.setup_ui()
        self.setup_text_tags()
        
    def setup_ui(self):
        """设置用户界面"""
        # 控制台文本区域
        self.console_text = scrolledtext.ScrolledText(
            self,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg='#000000',  # 黑色背景
            fg='#00FF00',  # 绿色文字（像素风格）
            insertbackground='#00FF00',
            selectbackground='#0078d7',
            selectforeground='white',
            state=tk.NORMAL,
            padx=10,
            pady=10
        )
        self.console_text.pack(fill=tk.BOTH, expand=True)
        
        # 绑定右键菜单
        self.setup_context_menu()
        
    def setup_text_tags(self):
        """设置文本标签样式"""
        # 正常输出 - 绿色
        self.console_text.tag_configure("output", foreground='#00FF00')
        
        # 错误输出 - 红色
        self.console_text.tag_configure("error", foreground='#FF0000', font=('Consolas', 10, 'bold'))
        
        # 警告输出 - 黄色
        self.console_text.tag_configure("warning", foreground='#FFFF00')
        
        # 信息输出 - 青色
        self.console_text.tag_configure("info", foreground='#00FFFF')
        
        # 成功输出 - 亮绿色
        self.console_text.tag_configure("success", foreground='#00FF7F')
        
        # 建议 - 蓝色（AI学习建议）
        self.console_text.tag_configure("suggestion", foreground='#00BFFF', font=('Consolas', 10, 'bold'))
        
        # 代码修复 - 橙色背景
        self.console_text.tag_configure("code_fix", foreground='#FFD700', background='#333333')
        
    def setup_context_menu(self):
        """设置右键菜单"""
        self.context_menu = tk.Menu(self.console_text, tearoff=0)
        self.context_menu.add_command(label="📋 复制", command=self.copy_text)
        self.context_menu.add_command(label="🔲 全选", command=self.select_all)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ 清空控制台", command=self.clear_output)
        
        self.console_text.bind('<Button-3>', self.show_context_menu)
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def copy_text(self):
        """复制文本"""
        try:
            selected_text = self.console_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(selected_text)
        except:
            pass
    
    def select_all(self):
        """全选"""
        self.console_text.tag_add(tk.SEL, "1.0", tk.END)
        self.console_text.mark_set(tk.INSERT, "1.0")
        self.console_text.see(tk.INSERT)
    
    def clear_output(self):
        """清空输出"""
        self.console_text.delete("1.0", tk.END)
    
    def append_output(self, text, tag="output"):
        """添加输出"""
        self.console_text.config(state=tk.NORMAL)
        
        # 智能分析文本颜色
        if "💡 智能分析:" in text or "【建议】" in text:
            # 分段处理，让建议部分显示为蓝色
            lines = text.split('\n')
            for line in lines:
                if line.strip() == "":
                    self.console_text.insert(tk.END, line + '\n', tag)
                elif "💡 智能分析:" in line:
                    self.console_text.insert(tk.END, line + '\n', "info")
                elif "【建议】" in line or "【修改方案】" in line or "【问题】" in line:
                    self.console_text.insert(tk.END, line + '\n', "suggestion")
                elif line.startswith("  - ") or line.startswith("  1. ") or line.startswith("  2. ") or line.startswith("  3. ") or line.startswith("  4. "):
                    self.console_text.insert(tk.END, line + '\n', "suggestion")
                else:
                    self.console_text.insert(tk.END, line + '\n', tag)
        elif "🤖 AI助手:" in text:
            # AI助手提示用蓝色
            lines = text.split('\n')
            for line in lines:
                if "🤖 AI助手:" in line:
                    self.console_text.insert(tk.END, line + '\n', "info")
                elif line.strip() != "":
                    self.console_text.insert(tk.END, line + '\n', "suggestion")
                else:
                    self.console_text.insert(tk.END, line + '\n', tag)
        else:
            self.console_text.insert(tk.END, text, tag)
        
        self.console_text.see(tk.END)
        self.console_text.config(state=tk.NORMAL)
        
    def _append_formatted_error(self, error_info):
        """添加格式化的错误信息"""
        self.console_text.config(state=tk.NORMAL)
        
        # 错误类型
        self.console_text.insert(tk.END, "❌ 错误类型: ", "info")
        self.console_text.insert(tk.END, f"{error_info['error_type']}\n", "error")
        
        # 错误信息
        self.console_text.insert(tk.END, "📍 错误信息: ", "info")
        self.console_text.insert(tk.END, f"{error_info['error_message']}\n", "error")
        
        # 错误位置
        if error_info['error_line'] > 0:
            self.console_text.insert(tk.END, "📌 错误位置: ", "info")
            self.console_text.insert(tk.END, f"第 {error_info['error_line']} 行\n", "error")
        
        # 代码上下文
        if error_info['code_context']:
            self.console_text.insert(tk.END, "\n代码上下文:\n", "info")
            self.console_text.insert(tk.END, f"{error_info['code_context']}\n", "code_fix")
        
        # 智能分析
        if error_info['smart_analysis']:
            self.console_text.insert(tk.END, "\n💡 智能分析:\n", "info")
            self.console_text.insert(tk.END, f"{error_info['smart_analysis']}\n", "suggestion")
        
        # 修改建议
        if error_info['suggestion']:
            self.console_text.insert(tk.END, "\n💡 建议: ", "info")
            self.console_text.insert(tk.END, f"{error_info['suggestion']}\n", "suggestion")
        
        # 代码方案
        if error_info['code_fix']:
            self.console_text.insert(tk.END, "\n🔧 修改方案:\n", "info")
            self.console_text.insert(tk.END, f"{error_info['code_fix']}\n", "code_fix")
        
        # AI助手提示
        self.console_text.insert(tk.END, "\n🤖 AI助手: ", "info")
        self.console_text.insert(tk.END, "向AI提问获取详细解决方案\n", "suggestion")
        
        self.console_text.insert(tk.END, "\n" + "="*50 + "\n\n", "info")
        self.console_text.see(tk.END)
        self.console_text.config(state=tk.NORMAL)
