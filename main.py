#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能Python学习桌面应用 - 完整版
IDLE风格 + AI助手
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.pixel_code_editor import PixelCodeEditor
from ui.pixel_console import PixelConsole
from ui.debugger_panel import DebuggerPanel
from ui.pixel_ai_assistant import PixelAIAssistant
from core.file_manager import FileManager
from core.code_executor import CodeExecutor
try:
    from cat_icon import get_cat_icon_photo
    CAT_ICON_AVAILABLE = True
except ImportError:
    CAT_ICON_AVAILABLE = False

# 集成SQLite数据采集功能
try:
    from integrations.sqlite_integration import integrate_with_app, sqlite_integration
    SQLITE_ANALYTICS_AVAILABLE = True
except ImportError:
    SQLITE_ANALYTICS_AVAILABLE = False
    print("⚠️ SQLite数据采集功能不可用，请检查integrations目录")


class PythonLearningApp:
    """完整的Python学习应用"""
    
    def __init__(self):
        """初始化"""
        self.root = tk.Tk()
        self.current_file = None
        self.is_debugging = False
        self.ai_panel_visible = True
        
        # 获取学生ID（在窗口显示前）
        self.student_id = self.get_student_id()
        
        self.setup_window()
        self.setup_components()
        self.setup_layout()
        # 在组件创建后集成数据采集功能
        self.setup_analytics()
        self.setup_menu()
        self.setup_statusbar()
    
    def get_student_id(self):
        """获取学生ID"""
        try:
            from core.student_id_manager import get_student_id
            student_id = get_student_id()
            if not student_id:
                # 如果用户取消，使用默认ID
                import uuid
                student_id = f"student_{uuid.uuid4().hex[:8]}"
                print(f"⚠️ 未输入学号，使用临时ID: {student_id}")
            else:
                print(f"✅ 学生ID: {student_id}")
            return student_id
        except Exception as e:
            print(f"⚠️ 获取学生ID失败: {e}")
            import uuid
            return f"student_{uuid.uuid4().hex[:8]}"
    
    def change_student_id(self):
        """修改学生ID"""
        try:
            from core.student_id_manager import get_student_id, update_student_id
            # 强制弹出对话框
            new_student_id = get_student_id(force_prompt=True)
            if new_student_id and new_student_id != self.student_id:
                # 更新当前学生ID
                old_student_id = self.student_id
                self.student_id = new_student_id
                # 重新启动会话
                if SQLITE_ANALYTICS_AVAILABLE:
                    sqlite_integration.end_session()
                    sqlite_integration.start_session(user_id=new_student_id)
                messagebox.showinfo("成功", f"学号已更新：{old_student_id} → {new_student_id}\n\n新的学习数据将使用新学号记录。")
        except Exception as e:
            messagebox.showerror("错误", f"修改学号失败：{e}")
        
    def setup_window(self):
        """设置窗口"""
        self.root.title("Python 学习助手 🐱")
        
        # 设置猫猫头图标
        if CAT_ICON_AVAILABLE:
            try:
                cat_icon = get_cat_icon_photo()
                self.root.iconphoto(False, cat_icon)
                print("🐱 猫猫头图标设置成功！")
            except Exception as e:
                print(f"设置图标失败: {e}")
        else:
            print("⚠️ 猫猫头图标不可用，请安装Pillow: pip install Pillow")
        
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 设置窗口为屏幕的80%
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        
        # 计算居中位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # 设置窗口大小和位置
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(1000, 600)
        self.root.maxsize(screen_width, screen_height)  # 允许最大化到屏幕大小
        
        # 确保窗口可以调整大小
        self.root.resizable(True, True)
        self.root.state('normal')
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_components(self):
        """初始化组件"""
        self.file_manager = FileManager()
        self.code_executor = CodeExecutor()
        
    def setup_analytics(self):
        """集成SQLite数据采集功能（在组件创建后调用）"""
        if SQLITE_ANALYTICS_AVAILABLE:
            try:
                # 使用学生ID启动会话
                sqlite_integration.start_session(user_id=self.student_id)
                integrate_with_app(self)
                print("📊 SQLite数据采集功能已启用")
            except Exception as e:
                print(f"⚠️ SQLite数据采集集成失败: {e}")
                import traceback
                traceback.print_exc()
        
    def setup_layout(self):
        """设置布局 - 使用PanedWindow实现可拖动调整"""
        # 主容器
        main_container = tk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建垂直PanedWindow（上下分割：主区域 + 调试器）
        self.v_paned = tk.PanedWindow(main_container, orient=tk.VERTICAL, sashrelief=tk.RAISED, sashwidth=5)
        self.v_paned.pack(fill=tk.BOTH, expand=True)
        
        # 上部区域（主区域）
        top_frame = tk.Frame(self.v_paned)
        self.v_paned.add(top_frame, stretch="always")
        
        # 创建水平PanedWindow（左右分割：编辑器 + 右侧栏）
        h_paned = tk.PanedWindow(top_frame, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=5)
        h_paned.pack(fill=tk.BOTH, expand=True)
        
        # 左侧：代码编辑器（初始宽度适中）
        editor_frame = ttk.LabelFrame(h_paned, text="代码编辑器", padding=2)
        h_paned.add(editor_frame, minsize=500, stretch="always")
        
        self.code_editor = PixelCodeEditor(editor_frame, self.file_manager)
        self.code_editor.pack(fill=tk.BOTH, expand=True)
        
        # 右侧：上下分栏（控制台 + AI助手）
        right_frame = tk.Frame(h_paned)
        h_paned.add(right_frame, minsize=450, stretch="always")
        
        right_paned = tk.PanedWindow(right_frame, orient=tk.VERTICAL, sashrelief=tk.RAISED, sashwidth=5)
        right_paned.pack(fill=tk.BOTH, expand=True)
        
        # 右上：输出控制台（占右侧45%）
        console_frame = ttk.LabelFrame(right_paned, text="输出控制台", padding=2)
        right_paned.add(console_frame, minsize=200, stretch="always")
        
        self.console = PixelConsole(console_frame, self.code_executor)
        self.console.pack(fill=tk.BOTH, expand=True)
        
        # 右下：AI助手（占右侧55%）
        ai_frame = ttk.LabelFrame(right_paned, text="AI学习助手", padding=2)
        right_paned.add(ai_frame, minsize=250, stretch="always")
        
        self.ai_assistant = PixelAIAssistant(ai_frame)
        self.ai_assistant.pack(fill=tk.BOTH, expand=True)
        
        # 底部：调试器面板（默认不添加到PanedWindow）
        self.debugger_frame = ttk.LabelFrame(self.v_paned, text="调试器 - 变量和堆栈", padding=5)
        self.debugger = DebuggerPanel(self.debugger_frame)
        self.debugger.pack(fill=tk.BOTH, expand=True)
        
        # 调试器面板显示状态
        self.debugger_visible = False
        
        # 绑定回调
        self.code_editor.set_output_callback(self.console.append_output)
        self.code_executor.set_output_callback(self.console.append_output)
        self.code_executor.set_debugger_callback(self.debugger.update_debug_info)
        self.code_executor.set_error_callback(self.handle_code_error)
        
    def setup_menu(self):
        """设置完整菜单 - 带图标"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📁 文件", menu=file_menu)
        file_menu.add_command(label="📄 新建文件", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="📂 打开文件...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="💾 保存", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="💿 另存为...", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="❌ 退出", command=self.on_closing)
        
        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="✏️ 编辑", menu=edit_menu)
        edit_menu.add_command(label="↩️ 撤销", command=self.code_editor.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="↪️ 重做", command=self.code_editor.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="✂️ 剪切", command=self.code_editor.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="📋 复制", command=self.code_editor.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="📌 粘贴", command=self.code_editor.paste, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="🔲 全选", command=self.code_editor.select_all, accelerator="Ctrl+A")
        edit_menu.add_command(label="🔍 查找...", command=self.show_find, accelerator="Ctrl+F")
        
        # 格式菜单
        format_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🎨 格式", menu=format_menu)
        format_menu.add_command(label="➡️ 增加缩进", command=self.indent_region, accelerator="Ctrl+]")
        format_menu.add_command(label="⬅️ 减少缩进", command=self.dedent_region, accelerator="Ctrl+[")
        format_menu.add_separator()
        format_menu.add_command(label="💬 注释代码", command=self.comment_region, accelerator="Alt+3")
        format_menu.add_command(label="🔓 取消注释", command=self.uncomment_region, accelerator="Alt+4")
        
        # 运行菜单
        run_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="▶️ 运行", menu=run_menu)
        run_menu.add_command(label="▶️ 运行代码", command=self.run_code, accelerator="F5")
        run_menu.add_command(label="✅ 检查语法", command=self.check_syntax)
        
        # 调试菜单 - 完整调试功能
        debug_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🐛 调试", menu=debug_menu)
        debug_menu.add_command(label="▶️ 继续执行", command=self.debug_go, accelerator="F5")
        debug_menu.add_command(label="👣 单步步入", command=self.debug_step, accelerator="F7")
        debug_menu.add_command(label="⏭️ 单步跳过", command=self.debug_over, accelerator="F8")
        debug_menu.add_command(label="⏫ 单步跳出", command=self.debug_out, accelerator="Shift+F8")
        debug_menu.add_separator()
        debug_menu.add_command(label="🔴 设置/取消断点", command=self.toggle_breakpoint, accelerator="F9")
        debug_menu.add_command(label="🗑️ 清除所有断点", command=self.clear_breakpoints)
        debug_menu.add_separator()
        debug_menu.add_command(label="👁️ 显示调试器面板", command=self.show_debugger)
        debug_menu.add_command(label="🙈 隐藏调试器面板", command=self.hide_debugger)
        
        # 选项菜单
        options_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="⚙️ 选项", menu=options_menu)
        self.show_line_num_var = tk.BooleanVar(value=True)
        options_menu.add_checkbutton(label="🔢 显示行号", variable=self.show_line_num_var,
                                     command=self.toggle_line_numbers)
        options_menu.add_separator()
        options_menu.add_command(label="👤 修改学号", command=self.change_student_id)
        
        # 窗口菜单
        window_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🪟 窗口", menu=window_menu)
        window_menu.add_command(label="🔍 放大", command=self.code_editor.increase_font_size, accelerator="Ctrl++")
        window_menu.add_command(label="🔎 缩小", command=self.code_editor.decrease_font_size, accelerator="Ctrl+-")
        window_menu.add_command(label="↩️ 重置大小", command=self.code_editor.reset_font_size)
        
        # Python
        python_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🐍 Python", menu=python_menu)
        python_menu.add_command(label="🔧 插入函数模板", command=lambda: self.code_editor.insert_template('function'))
        python_menu.add_command(label="🏗️ 插入类模板", command=lambda: self.code_editor.insert_template('class'))
        python_menu.add_command(label="🔄 插入循环模板", command=lambda: self.code_editor.insert_template('loop'))
        python_menu.add_command(label="❓ 插入条件模板", command=lambda: self.code_editor.insert_template('condition'))
        python_menu.add_command(label="⚠️ 插入异常模板", command=lambda: self.code_editor.insert_template('exception'))
        python_menu.add_separator()
        python_menu.add_command(label="📚 加载基础语法示例", command=self.load_examples)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="❓ 帮助", menu=help_menu)
        help_menu.add_command(label="📖 使用说明", command=self.show_help)
        help_menu.add_command(label="📚 Python语法参考", command=self.show_python_ref)
        help_menu.add_separator()
        help_menu.add_command(label="ℹ️ 关于", command=self.show_about)
        
        # 绑定快捷键
        self.root.bind('<F5>', lambda e: self.run_code())
        self.root.bind('<F6>', lambda e: self.debug_go())
        self.root.bind('<F7>', lambda e: self.debug_step())
        self.root.bind('<F8>', lambda e: self.debug_over())
        self.root.bind('<F9>', lambda e: self.toggle_breakpoint())
        
    def setup_statusbar(self):
        """设置状态栏"""
        self.statusbar = ttk.Frame(self.root, relief=tk.SUNKEN, borderwidth=1)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.line_col_label = ttk.Label(self.statusbar, text="行: 1  列: 0", width=15)
        self.line_col_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(self.statusbar, orient='vertical').pack(side=tk.LEFT, fill=tk.Y)
        
        self.filename_label = ttk.Label(self.statusbar, text="未命名", width=25)
        self.filename_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(self.statusbar, orient='vertical').pack(side=tk.LEFT, fill=tk.Y)
        
        self.encoding_label = ttk.Label(self.statusbar, text="UTF-8")
        self.encoding_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(self.statusbar, orient='vertical').pack(side=tk.LEFT, fill=tk.Y)
        
        self.debug_label = ttk.Label(self.statusbar, text="就绪")
        self.debug_label.pack(side=tk.LEFT, padx=5)
        
        self.update_statusbar()
        
    def update_statusbar(self):
        """更新状态栏"""
        try:
            line = self.code_editor.get_current_line()
            col = self.code_editor.get_current_column()
            self.line_col_label.config(text=f"行: {line}  列: {col}")
            
            filename = self.file_manager.get_current_file()
            self.filename_label.config(text=filename)
            
            if self.is_debugging:
                bp_count = len(self.code_editor.get_breakpoints())
                self.debug_label.config(text=f"调试中 ({bp_count}个断点)", foreground="red")
            else:
                bp_count = len(self.code_editor.get_breakpoints())
                if bp_count > 0:
                    self.debug_label.config(text=f"{bp_count}个断点", foreground="blue")
                else:
                    self.debug_label.config(text="就绪", foreground="black")
        except:
            pass
            
        self.root.after(100, self.update_statusbar)
        
    # 文件操作
    def new_file(self):
        """新建"""
        if self.file_manager.new_file(self.code_editor):
            self.update_title()
            
    def open_file(self):
        """打开"""
        if self.file_manager.open_file(self.code_editor):
            self.update_title()
            
    def save_file(self):
        """保存"""
        if self.file_manager.save_file(self.code_editor):
            self.update_title()
            
    def save_as_file(self):
        """另存为"""
        if self.file_manager.save_as_file(self.code_editor):
            self.update_title()
            
    def update_title(self):
        """更新标题"""
        filename = self.file_manager.get_current_file()
        self.root.title(f"{filename} - Python 学习助手")
        
    # 格式化操作
    def indent_region(self):
        """缩进"""
        try:
            sel = self.code_editor.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            lines = sel.split('\n')
            indented = '\n'.join(['    ' + l for l in lines])
            self.code_editor.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.code_editor.text_area.insert(tk.INSERT, indented)
        except:
            pass
            
    def dedent_region(self):
        """取消缩进"""
        try:
            sel = self.code_editor.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            lines = sel.split('\n')
            dedented = '\n'.join([l[4:] if l.startswith('    ') else l for l in lines])
            self.code_editor.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.code_editor.text_area.insert(tk.INSERT, dedented)
        except:
            pass
            
    def comment_region(self):
        """注释"""
        try:
            sel = self.code_editor.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            lines = sel.split('\n')
            commented = '\n'.join(['# ' + l for l in lines])
            self.code_editor.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.code_editor.text_area.insert(tk.INSERT, commented)
        except:
            pass
            
    def uncomment_region(self):
        """取消注释"""
        try:
            sel = self.code_editor.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            lines = sel.split('\n')
            uncommented = '\n'.join([l[2:] if l.startswith('# ') else l for l in lines])
            self.code_editor.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.code_editor.text_area.insert(tk.INSERT, uncommented)
        except:
            pass
            
    # 运行和调试
    def run_code(self):
        """运行代码"""
        code = self.code_editor.get_code()
        if code.strip():
            self.console.clear_output()
            self.console.append_output(">>> 程序开始运行...\n", "info")
            self.code_editor.clear_error_highlight()
            self.code_executor.execute_code(code)
        else:
            messagebox.showwarning("运行", "代码为空")
    
    def handle_code_error(self, line_number):
        """接收执行器错误回调并高亮对应行"""
        try:
            if line_number:
                self.code_editor.highlight_error_line(line_number)
            else:
                self.code_editor.clear_error_highlight()
        except Exception as e:
            print(f"高亮错误行失败: {e}")
            
    def check_syntax(self):
        """检查语法"""
        code = self.code_editor.get_code()
        is_valid, error = self.code_executor.check_syntax(code)
        if is_valid:
            messagebox.showinfo("语法检查", "✓ 语法正确")
        else:
            messagebox.showerror("语法错误", error)
            
    def debug_go(self):
        """开始调试"""
        code = self.code_editor.get_code()
        breakpoints = self.code_editor.get_breakpoints()
        
        if not code.strip():
            messagebox.showwarning("调试", "代码为空")
            return
            
        if not breakpoints:
            result = messagebox.askyesno("调试", "未设置断点。\n\n点击行号区域可设置断点。\n是否以普通模式运行？")
            if result:
                self.run_code()
            return
            
        self.is_debugging = True
        self.show_debugger()
        
        self.console.clear_output()
        self.console.append_output("=== 调试模式 ===\n", "info")
        self.console.append_output(f"断点: {', '.join(map(str, breakpoints))}\n", "info")
        self.console.append_output("F7=单步 F8=跳过 Shift+F8=跳出\n", "info")
        self.console.append_output("=" * 50 + "\n", "info")
        
        self.code_executor.execute_with_breakpoints(code, breakpoints)
        
    def debug_step(self):
        """单步步入"""
        if not self.is_debugging:
            self.debug_go()
        else:
            self.console.append_output("→ 单步步入\n", "info")
            
    def debug_over(self):
        """单步跳过"""
        if not self.is_debugging:
            messagebox.showwarning("调试", "请先开始调试（F5或F6）")
        else:
            self.console.append_output("→ 单步跳过\n", "info")
            
    def debug_out(self):
        """跳出"""
        if not self.is_debugging:
            messagebox.showwarning("调试", "请先开始调试")
        else:
            self.console.append_output("→ 跳出函数\n", "info")
            
    def toggle_breakpoint(self):
        """切换断点"""
        self.code_editor.toggle_breakpoint()
        
    def clear_breakpoints(self):
        """清除断点"""
        self.code_editor.clear_all_breakpoints()
        messagebox.showinfo("断点", "所有断点已清除")
        
    def show_debugger(self):
        """显示调试器面板"""
        if not self.debugger_visible:
            # 添加调试器面板到垂直PanedWindow
            self.v_paned.add(self.debugger_frame, height=200, stretch="never")
            self.debugger_visible = True
            self.debugger.show_stack_info()
        
    def hide_debugger(self):
        """隐藏调试器面板"""
        if self.debugger_visible:
            # 从PanedWindow中移除调试器面板
            self.v_paned.remove(self.debugger_frame)
            self.debugger_visible = False
            self.is_debugging = False
            self.debugger.clear()
        
    # 选项
    def toggle_line_numbers(self):
        """切换行号"""
        if self.show_line_num_var.get():
            self.code_editor.show_line_numbers()
        else:
            self.code_editor.hide_line_numbers()
            
            
    # 其他
    def show_find(self):
        """查找"""
        text = simpledialog.askstring("查找", "查找:")
        if text:
            self.code_editor.find_text(text)
            
    def load_examples(self):
        """加载示例"""
        self.code_editor.insert_sample_code()
        
    def show_help(self):
        """显示帮助"""
        help_text = """Python 学习助手 - 使用指南

界面布局：
• 左侧：代码编辑器（点击行号设置断点）
• 中间：输出控制台
• 右侧：AI学习助手
• 底部：状态栏（行列/文件/编码/调试状态）

快捷键：
F5  - 运行/继续调试
F7  - 单步步入
F8  - 单步跳过
F9  - 设置/取消断点

断点设置：
• 点击行号区域的数字
• 断点显示为红色圆点
• 黄色背景标记断点行

调试功能：
• 设置断点后按F5开始调试
• Debug菜单查看完整选项
• 调试器面板显示变量和堆栈

AI助手：
• 提问Python相关问题
• 复制AI的代码示例
• 选择学习模式获得针对性建议"""
        
        messagebox.showinfo("帮助", help_text)
        
    def show_python_ref(self):
        """Python参考"""
        self.code_editor.show_python_help()
        
    def show_about(self):
        """关于"""
        messagebox.showinfo("关于", """Python 学习助手

版本: 2.0
设计: IDLE风格
AI: DeepSeek集成

功能完整的Python学习环境""")
        
    def on_closing(self):
        """关闭"""
        # 清理SQLite数据采集会话
        if SQLITE_ANALYTICS_AVAILABLE and sqlite_integration.enabled:
            try:
                sqlite_integration.end_session()
                print("📊 数据采集会话已结束")
            except Exception as e:
                print(f"⚠️ 结束数据采集会话失败: {e}")
        
        self.root.destroy()
        
    def run(self):
        """运行"""
        self.root.mainloop()


def main():
    """主函数"""
    try:
        app = PythonLearningApp()
        app.run()
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
