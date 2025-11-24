# -*- coding: utf-8 -*-
"""
像素动漫风代码编辑器
支持行号、断点、右键菜单、语法高亮
"""

import tkinter as tk
from tkinter import Canvas
import re

# Python关键字
KEYWORDS = {'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
            'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
            'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
            'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return',
            'try', 'while', 'with', 'yield'}

# Python内置函数
BUILTINS = {'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytearray', 'bytes',
            'callable', 'chr', 'classmethod', 'compile', 'complex', 'delattr',
            'dict', 'dir', 'divmod', 'enumerate', 'eval', 'exec', 'filter',
            'float', 'format', 'frozenset', 'getattr', 'globals', 'hasattr',
            'hash', 'help', 'hex', 'id', 'input', 'int', 'isinstance',
            'issubclass', 'iter', 'len', 'list', 'locals', 'map', 'max',
            'memoryview', 'min', 'next', 'object', 'oct', 'open', 'ord',
            'pow', 'print', 'property', 'range', 'repr', 'reversed', 'round',
            'set', 'setattr', 'slice', 'sorted', 'staticmethod', 'str', 'sum',
            'super', 'tuple', 'type', 'vars', 'zip'}


class PixelCodeEditor(tk.Frame):
    """像素动漫风代码编辑器"""
    
    def __init__(self, parent, file_manager):
        """初始化编辑器"""
        super().__init__(parent)
        
        self.file_manager = file_manager
        self.output_callback = None
        self.is_modified = False
        self.breakpoints = set()
        self.font_size = 11
        
        self.setup_editor()
        self.setup_bindings()
        self.setup_context_menu()
        
    def setup_editor(self):
        """设置编辑器界面"""
        # 创建容器
        container = tk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True)
        
        # 行号和断点区域（Canvas）
        self.line_canvas = Canvas(
            container,
            width=50,
            bg='#f0f0f0',
            highlightthickness=0,
            relief='flat',
            borderwidth=0
        )
        self.line_canvas.pack(side=tk.LEFT, fill=tk.Y)
        
        # 绑定行号区域点击事件（设置断点）
        self.line_canvas.bind('<Button-1>', self.on_line_click)
        
        # 确保Canvas能接收焦点
        self.line_canvas.bind('<Enter>', lambda e: self.line_canvas.configure(cursor='hand2'))
        self.line_canvas.bind('<Leave>', lambda e: self.line_canvas.configure(cursor=''))
        
        # 代码编辑区域
        self.text_area = tk.Text(
            container,
            wrap=tk.NONE,
            undo=True,
            maxundo=50,
            font=('Consolas', self.font_size),
            bg='white',
            fg='black',
            insertbackground='black',
            selectbackground='#0078d7',  # 蓝色背景
            selectforeground='white',    # 白色文字
            tabs='4c',
            padx=5,
            pady=5
        )
        
        # 确保选择样式生效
        self.text_area.configure(
            selectbackground='#0078d7',
            selectforeground='white'
        )
        
        # 垂直滚动条
        v_scrollbar = tk.Scrollbar(container, orient='vertical', command=self.text_area.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 水平滚动条
        h_scrollbar = tk.Scrollbar(self, orient='horizontal', command=self.text_area.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 配置滚动
        self.text_area.config(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # 配置语法高亮标签
        self.setup_syntax_tags()
        
        # 绑定选择变化事件，确保选中文字变白
        self.text_area.bind('<<Selection>>', self.on_selection_change)
        
    def on_selection_change(self, event=None):
        """处理选择变化，确保选中文字显示为白色"""
        try:
            # 清除之前的选择标签
            self.text_area.tag_remove("custom_sel", "1.0", tk.END)
            
            # 获取当前选择范围
            if self.text_area.tag_ranges("sel"):
                start = self.text_area.index("sel.first")
                end = self.text_area.index("sel.last")
                
                # 应用自定义选择标签
                self.text_area.tag_add("custom_sel", start, end)
                
        except tk.TclError:
            # 忽略选择变化时的错误
            pass
        
    def setup_syntax_tags(self):
        """设置语法高亮标签"""
        # 关键字 - 蓝色
        self.text_area.tag_configure("keyword", foreground="#0000FF", font=('Consolas', self.font_size, 'bold'))
        
        # 字符串 - 绿色
        self.text_area.tag_configure("string", foreground="#008000")
        
        # 注释 - 灰色
        self.text_area.tag_configure("comment", foreground="#808080", font=('Consolas', self.font_size, 'italic'))
        
        # 函数名 - 紫色
        self.text_area.tag_configure("function", foreground="#800080", font=('Consolas', self.font_size, 'bold'))
        
        # 类名 - 深青色
        self.text_area.tag_configure("class", foreground="#008080", font=('Consolas', self.font_size, 'bold'))
        
        # 数字 - 橙色
        self.text_area.tag_configure("number", foreground="#FF8C00")
        
        # 自定义选择标签 - 最高优先级，确保选中文字变白
        self.text_area.tag_configure("custom_sel", 
                                   background="#0078d7", 
                                   foreground="white",
                                   font=('Consolas', self.font_size))
        
        # 设置选择标签的优先级（数字越小优先级越高）
        self.text_area.tag_raise("custom_sel")
        
        # 内置函数 - 深蓝色
        self.text_area.tag_configure("builtin", foreground="#0066CC")
        
        # 断点
        self.text_area.tag_configure("breakpoint", background="#ffeb3b")
        
        # 错误行高亮 - 淡红色背景
        self.text_area.tag_configure(
            "error_line",
            background="#ffecec",
            foreground="black"
        )
        # 确保错误高亮在选择标签下方
        self.text_area.tag_lower("error_line")
        
    def highlight_syntax(self):
        """语法高亮"""
        # 清除现有标签（但保留选择标签）
        for tag in ["keyword", "string", "comment", "function", "class", "number", "builtin"]:
            self.text_area.tag_remove(tag, "1.0", tk.END)
        
        # 获取所有文本
        content = self.text_area.get("1.0", tk.END)
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # 跳过空行
            if not line.strip():
                continue
            
            # 高亮注释
            comment_match = re.search(r'#.*$', line)
            if comment_match:
                start = f"{line_num}.{comment_match.start()}"
                end = f"{line_num}.{comment_match.end()}"
                self.text_area.tag_add("comment", start, end)
                # 注释后面的内容不再处理
                line = line[:comment_match.start()]
            
            # 高亮字符串
            for match in re.finditer(r'(["\'])(?:(?=(\\?))\2.)*?\1', line):
                start = f"{line_num}.{match.start()}"
                end = f"{line_num}.{match.end()}"
                self.text_area.tag_add("string", start, end)
            
            # 高亮数字
            for match in re.finditer(r'\b\d+(\.\d+)?\b', line):
                start = f"{line_num}.{match.start()}"
                end = f"{line_num}.{match.end()}"
                self.text_area.tag_add("number", start, end)
            
            # 高亮类定义
            class_match = re.search(r'\bclass\s+(\w+)', line)
            if class_match:
                start = f"{line_num}.{class_match.start(1)}"
                end = f"{line_num}.{class_match.end(1)}"
                self.text_area.tag_add("class", start, end)
            
            # 高亮函数定义
            func_match = re.search(r'\bdef\s+(\w+)', line)
            if func_match:
                start = f"{line_num}.{func_match.start(1)}"
                end = f"{line_num}.{func_match.end(1)}"
                self.text_area.tag_add("function", start, end)
            
            # 高亮关键字和内置函数
            words = re.findall(r'\b\w+\b', line)
            for word in words:
                if word in KEYWORDS:
                    for match in re.finditer(rf'\b{re.escape(word)}\b', line):
                        start = f"{line_num}.{match.start()}"
                        end = f"{line_num}.{match.end()}"
                        self.text_area.tag_add("keyword", start, end)
                elif word in BUILTINS:
                    for match in re.finditer(rf'\b{re.escape(word)}\b', line):
                        start = f"{line_num}.{match.start()}"
                        end = f"{line_num}.{match.end()}"
                        self.text_area.tag_add("builtin", start, end)
        
        # 语法高亮完成后，重新应用选择样式
        self.after(10, self.on_selection_change)
        
    def setup_bindings(self):
        """设置事件绑定"""
        # 文本变化事件
        self.text_area.bind('<KeyRelease>', self.on_text_change)
        self.text_area.bind('<Button-1>', self.on_text_change)
        self.text_area.bind('<MouseWheel>', self.on_scroll)
        
        # 快捷键
        self.text_area.bind('<F9>', lambda e: self.toggle_breakpoint())
        
        # 自动缩进
        self.text_area.bind('<Return>', self.auto_indent)
        
    def setup_context_menu(self):
        """设置右键菜单"""
        self.context_menu = tk.Menu(self.text_area, tearoff=0)
        self.context_menu.add_command(label="📋 复制", command=self.copy, accelerator="Ctrl+C")
        self.context_menu.add_command(label="✂️ 剪切", command=self.cut, accelerator="Ctrl+X")
        self.context_menu.add_command(label="📌 粘贴", command=self.paste, accelerator="Ctrl+V")
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🔲 全选", command=self.select_all, accelerator="Ctrl+A")
        self.context_menu.add_command(label="🗑️ 清空", command=self.clear_all)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🔴 设置断点", command=self.toggle_breakpoint, accelerator="F9")
        self.context_menu.add_command(label="🗑️ 清除所有断点", command=self.clear_all_breakpoints)
        
        self.text_area.bind('<Button-3>', self.show_context_menu)
        
    def show_context_menu(self, event):
        """显示右键菜单"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def on_text_change(self, event=None):
        """文本变化处理"""
        self.is_modified = True
        self.update_line_numbers()
        # 延迟执行语法高亮，避免频繁更新
        if hasattr(self, '_highlight_after_id'):
            self.after_cancel(self._highlight_after_id)
        self._highlight_after_id = self.after(300, self.highlight_syntax)
        
    def on_scroll(self, event):
        """滚动事件"""
        self.update_line_numbers()
        
    def on_line_click(self, event):
        """行号区域点击事件 - 设置断点"""
        # 获取可见行范围
        first_visible = self.text_area.index('@0,0')
        last_visible = self.text_area.index(f'@0,{self.text_area.winfo_height()}')
        
        first_line = int(first_visible.split('.')[0])
        last_line = int(last_visible.split('.')[0])
        
        # 使用更精确的行号计算方法
        # 遍历可见的每一行，找到最接近点击位置的行
        clicked_line = None
        min_distance = float('inf')
        
        for line_num in range(first_line, last_line + 1):
            # 获取该行的位置信息
            line_info = self.text_area.dlineinfo(f'{line_num}.0')
            if line_info:
                line_y = line_info[1]  # 行的y坐标
                line_height = line_info[3]  # 行高
                line_bottom = line_y + line_height  # 行的底部位置
                line_center = line_y + line_height // 2  # 行的中心位置
                
                # 计算点击位置到行中心的距离
                distance = abs(event.y - line_center)
                
                # 如果点击位置在该行的范围内（包含边界）
                if line_y <= event.y <= line_bottom:
                    clicked_line = line_num
                    break
                # 记录距离最近的行
                elif distance < min_distance:
                    min_distance = distance
                    clicked_line = line_num
        
        # 如果没有找到精确匹配，使用距离最近的行
        if clicked_line is None:
            clicked_line = first_line
        
        # 确保行号在有效范围内
        if clicked_line < 1:
            clicked_line = 1
        elif clicked_line > last_line:
            clicked_line = last_line
        
        # 切换断点
        self.toggle_breakpoint(clicked_line)
        
        # 调试信息（可以在控制台查看）
        print(f"点击位置: y={event.y}, 计算行号: {clicked_line}, 可见行范围: {first_line}-{last_line}")
        
    def update_line_numbers(self):
        """更新行号和断点显示"""
        self.line_canvas.delete('all')
        
        # 获取可见行范围
        first_visible = self.text_area.index('@0,0')
        last_visible = self.text_area.index(f'@0,{self.text_area.winfo_height()}')
        
        first_line = int(first_visible.split('.')[0])
        last_line = int(last_visible.split('.')[0])
        
        # 获取文本的实际行高
        line_height = self.text_area.dlineinfo('1.0')
        if line_height:
            line_height = line_height[3]  # 获取行高
        else:
            line_height = 20  # 默认行高
        
        # 绘制行号和断点
        for line_num in range(first_line, last_line + 1):
            # 计算准确的行位置
            line_info = self.text_area.dlineinfo(f'{line_num}.0')
            if line_info:
                # 使用行的实际位置，与断点设置逻辑保持一致
                line_y = line_info[1]  # 行的y坐标
                line_height_actual = line_info[3]  # 实际行高
                y = line_y + line_height_actual // 2  # 行的中心位置
            else:
                # 如果无法获取行信息，使用相对位置计算
                y = (line_num - first_line) * line_height + line_height // 2
            
            # 如果有断点，绘制红色圆点
            if line_num in self.breakpoints:
                self.line_canvas.create_oval(5, y-6, 15, y+6, fill='#ff0000', outline='', width=0)
            
            # 绘制行号
            self.line_canvas.create_text(
                35, y,
                text=str(line_num),
                font=('Consolas', 9),
                fill='#666666',
                anchor='e'
            )
    
    def toggle_breakpoint(self, line=None):
        """切换断点"""
        if line is None:
            # 获取当前光标所在行
            line = int(self.text_area.index(tk.INSERT).split('.')[0])
        
        if line in self.breakpoints:
            self.breakpoints.remove(line)
            # 移除断点背景
            self.text_area.tag_remove("breakpoint", f"{line}.0", f"{line}.end")
        else:
            self.breakpoints.add(line)
            # 添加断点背景
            self.text_area.tag_add("breakpoint", f"{line}.0", f"{line}.end")
        
        self.update_line_numbers()
    
    def clear_all_breakpoints(self):
        """清除所有断点"""
        for line in list(self.breakpoints):
            self.text_area.tag_remove("breakpoint", f"{line}.0", f"{line}.end")
        self.breakpoints.clear()
        self.update_line_numbers()
    
    def highlight_error_line(self, line_number):
        """高亮错误行"""
        try:
            if not line_number:
                self.clear_error_highlight()
                return
            
            self.clear_error_highlight()
            start = f"{line_number}.0"
            end = f"{line_number}.end"
            self.text_area.tag_add("error_line", start, end)
            # 滚动到对应行
            self.text_area.see(start)
            # 轻微闪烁提示
            self.text_area.tag_raise("error_line")
            self.after(100, lambda: self.text_area.tag_lower("error_line"))
        except Exception as e:
            print(f"高亮错误行失败: {e}")
    
    def clear_error_highlight(self):
        """清除错误高亮"""
        self.text_area.tag_remove("error_line", "1.0", tk.END)
    
    def get_breakpoints(self):
        """获取断点列表"""
        return sorted(list(self.breakpoints))
    
    def auto_indent(self, event):
        """自动缩进"""
        # 获取当前行
        line_num = self.text_area.index(tk.INSERT).split('.')[0]
        line = self.text_area.get(f"{line_num}.0", f"{line_num}.end")
        
        # 计算缩进
        indent = len(line) - len(line.lstrip())
        
        # 如果行尾是冒号，增加缩进
        if line.rstrip().endswith(':'):
            indent += 4
        
        # 插入换行和缩进
        self.text_area.insert(tk.INSERT, '\n' + ' ' * indent)
        return 'break'
    
    # 编辑操作
    def undo(self):
        """撤销"""
        try:
            self.text_area.edit_undo()
        except:
            pass
    
    def redo(self):
        """重做"""
        try:
            self.text_area.edit_redo()
        except:
            pass
    
    def cut(self):
        """剪切"""
        self.text_area.event_generate("<<Cut>>")
    
    def copy(self):
        """复制"""
        self.text_area.event_generate("<<Copy>>")
    
    def paste(self):
        """粘贴"""
        self.text_area.event_generate("<<Paste>>")
        self.highlight_syntax()
    
    def select_all(self):
        """全选"""
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT, "1.0")
        self.text_area.see(tk.INSERT)
    
    def clear_all(self):
        """清空"""
        self.text_area.delete("1.0", tk.END)
        self.clear_all_breakpoints()
    
    def get_code(self):
        """获取代码"""
        return self.text_area.get("1.0", tk.END).rstrip()
    
    def set_code(self, code):
        """设置代码"""
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", code)
        self.highlight_syntax()
        self.update_line_numbers()
    
    def find_text(self, text):
        """查找文本"""
        self.text_area.tag_remove("search", "1.0", tk.END)
        
        if text:
            start = "1.0"
            while True:
                pos = self.text_area.search(text, start, tk.END)
                if not pos:
                    break
                end = f"{pos}+{len(text)}c"
                self.text_area.tag_add("search", pos, end)
                start = end
            
            self.text_area.tag_configure("search", background="#fbbf24", foreground="#1f2937")
    
    def insert_template(self, template_type):
        """插入代码模板"""
        templates = {
            'function': '''def function_name(parameters):
    """函数说明"""
    pass
''',
            'class': '''class ClassName:
    """类说明"""
    
    def __init__(self):
        pass
''',
            'loop': '''for item in iterable:
    # 循环体
    pass
''',
            'condition': '''if condition:
    # 条件为真时执行
    pass
else:
    # 条件为假时执行
    pass
''',
            'exception': '''try:
    # 可能出错的代码
    pass
except Exception as e:
    # 异常处理
    print(f"错误: {e}")
'''
        }
        
        if template_type in templates:
            self.text_area.insert(tk.INSERT, templates[template_type])
            self.highlight_syntax()
    
    def insert_sample_code(self):
        """插入示例代码"""
        sample = '''# Python基础语法示例
print("Hello, Python!")

# 变量和数据类型
name = "张三"
age = 25
height = 175.5
is_student = True

# 列表和字典
fruits = ["苹果", "香蕉", "橙子"]
person = {"name": name, "age": age}

# 条件语句
if age >= 18:
    print(f"{name}已经成年")

# 循环语句
for fruit in fruits:
    print(f"- {fruit}")

# 函数定义
def greet(name):
    """问候函数"""
    return f"你好，{name}！"

# 调用函数
message = greet(name)
print(message)
'''
        self.set_code(sample)
    
    def increase_font_size(self):
        """增大字体"""
        self.font_size += 1
        self.text_area.config(font=('Consolas', self.font_size))
        self.setup_syntax_tags()
        self.highlight_syntax()
    
    def decrease_font_size(self):
        """减小字体"""
        if self.font_size > 8:
            self.font_size -= 1
            self.text_area.config(font=('Consolas', self.font_size))
            self.setup_syntax_tags()
            self.highlight_syntax()
    
    def reset_font_size(self):
        """重置字体大小"""
        self.font_size = 11
        self.text_area.config(font=('Consolas', self.font_size))
        self.setup_syntax_tags()
        self.highlight_syntax()
    
    def get_current_line(self):
        """获取当前行号"""
        return int(self.text_area.index(tk.INSERT).split('.')[0])
    
    def get_current_column(self):
        """获取当前列号"""
        return int(self.text_area.index(tk.INSERT).split('.')[1])
    
    def show_line_numbers(self):
        """显示行号"""
        self.line_canvas.pack(side=tk.LEFT, fill=tk.Y)
    
    def hide_line_numbers(self):
        """隐藏行号"""
        self.line_canvas.pack_forget()
    
    def set_output_callback(self, callback):
        """设置输出回调"""
        self.output_callback = callback
    
    def show_python_help(self):
        """显示Python帮助"""
        help_text = """Python语法参考

关键字：if, else, elif, for, while, def, class, import, try, except...
内置函数：print(), input(), len(), range(), type(), str(), int()...
数据类型：int, float, str, list, dict, tuple, set, bool...

更多信息请访问 Python官方文档"""
        
        if self.output_callback:
            self.output_callback(help_text, "info")
