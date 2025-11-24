# -*- coding: utf-8 -*-
"""
代码执行器
负责执行Python代码并捕获输出
"""

import sys
import io
import threading
import time
import subprocess
import os
from contextlib import redirect_stdout, redirect_stderr


class CodeExecutor:
    """代码执行器类"""
    
    def __init__(self):
        """初始化代码执行器"""
        self.is_running = False
        self.execution_thread = None
        self.output_callback = None
        self.error_callback = None
        self.debugger_callback = None
        self.execution_timeout = 30  # 执行超时时间（秒）
        self.debug_mode = False
        self.breakpoints = []
        self.current_line = 0
        
    def set_output_callback(self, callback):
        """
        设置输出回调函数
        
        Args:
            callback: 输出回调函数
        """
        self.output_callback = callback
    
    def set_debugger_callback(self, callback):
        """
        设置调试器回调函数
        
        Args:
            callback: 调试器回调函数
        """
        self.debugger_callback = callback
        
    def set_error_callback(self, callback):
        """
        设置错误回调函数
        
        Args:
            callback: 错误回调函数
        """
        self.error_callback = callback
        
    def execute_code(self, code):
        """
        执行Python代码
        
        Args:
            code: 要执行的Python代码
        """
        if self.is_running:
            if self.output_callback:
                self.output_callback("代码正在执行中，请等待完成...", "warning")
            return
            
        # 在新线程中执行代码
        self.execution_thread = threading.Thread(
            target=self._execute_code_thread,
            args=(code,),
            daemon=True
        )
        self.execution_thread.start()
        
    def _execute_code_thread(self, code):
        """在单独线程中执行代码"""
        self.is_running = True
        start_time = time.time()
        
        try:
            # 创建输出捕获对象
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            # 执行代码
            exec_globals = {
                '__name__': '__main__',
                '__builtins__': __builtins__,
                'print': self._custom_print
            }
            
            # ⚠️ 注意：必须让 globals 与 locals 指向同一个字典
            # 否则在 exec() 中定义的类/函数会落到 exec_locals 里，
            # 后续函数调用（例如 main() 里访问 StudentManagementSystem）就找不到，
            # 会出现 “NameError: 'XXX' is not defined” 的误报。
            exec_locals = exec_globals
            
            # 重定向输出
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                try:
                    # 每次运行前先清除错误高亮
                    if self.error_callback:
                        self._notify_error_line(None)
                    exec(code, exec_globals, exec_locals)
                except Exception as e:
                    # 捕获执行异常并提供代码提示
                    import traceback
                    import sys
                    
                    # 获取完整的异常信息
                    exc_type, exc_value, exc_tb = sys.exc_info()
                    
                    # 提取错误行号
                    error_line = None
                    error_msg = str(e)
                    
                    # 优先从错误信息中提取行号，这样更准确
                    import re
                    match = re.search(r'line (\d+)', error_msg)
                    if match:
                        error_line = int(match.group(1))
                    elif exc_tb:
                        # 如果错误信息中没有行号，使用traceback
                        tb = exc_tb
                        while tb.tb_next:
                            tb = tb.tb_next
                        error_line = tb.tb_lineno
                    
                    # 分析错误并提供建议
                    error_analysis, resolved_line = self.analyze_error_with_context(
                        e, code, error_line, exec_locals
                    )
                    self._notify_error_line(resolved_line)
                    if self.output_callback:
                        self.output_callback(error_analysis, "error")
                    
            # 获取输出
            stdout_output = stdout_capture.getvalue()
            stderr_output = stderr_capture.getvalue()
            
            # 显示输出
            if stdout_output:
                if self.output_callback:
                    self.output_callback(stdout_output, "output")
                    
            if stderr_output:
                if self.output_callback:
                    self.output_callback(stderr_output, "error")
                    
            # 计算执行时间
            execution_time = time.time() - start_time
            
            # 显示执行完成信息
            if self.output_callback:
                if not stdout_output and not stderr_output:
                    self.output_callback("代码执行完成，无输出。", "info")
                else:
                    self.output_callback(f"执行完成 (耗时: {execution_time:.3f}秒)", "info")
                    
        except Exception as e:
            # 捕获执行器异常
            error_msg = f"代码执行器错误：{str(e)}"
            if self.output_callback:
                self.output_callback(error_msg, "error")
        finally:
            self.is_running = False
            self._notify_error_line(None)
            
    def _custom_print(self, *args, **kwargs):
        """自定义print函数，用于捕获输出"""
        # 将输出重定向到回调函数
        output = ' '.join(str(arg) for arg in args)
        if self.output_callback:
            self.output_callback(output + '\n', "output")
        else:
            # 如果没有回调函数，使用标准输出
            print(*args, **kwargs)
            
    def stop_execution(self):
        """停止代码执行"""
        if self.is_running:
            self.is_running = False
            if self.output_callback:
                self.output_callback("代码执行已停止。", "warning")
                
    def execute_file(self, filename):
        """
        执行Python文件
        
        Args:
            filename: Python文件路径
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                code = f.read()
                
            self.execute_code(code)
            
        except Exception as e:
            error_msg = f"读取文件失败：{str(e)}"
            if self.output_callback:
                self.output_callback(error_msg, "error")
                
    def execute_with_timeout(self, code, timeout=None):
        """
        带超时的代码执行
        
        Args:
            code: 要执行的代码
            timeout: 超时时间（秒）
        """
        if timeout is None:
            timeout = self.execution_timeout
            
        def timeout_handler():
            time.sleep(timeout)
            if self.is_running:
                self.stop_execution()
                if self.output_callback:
                    self.output_callback(f"代码执行超时（{timeout}秒）", "warning")
                    
        # 启动超时监控线程
        timeout_thread = threading.Thread(target=timeout_handler, daemon=True)
        timeout_thread.start()
        
        # 执行代码
        self.execute_code(code)
        
    def check_syntax(self, code):
        """
        检查代码语法
        
        Args:
            code: 要检查的代码
            
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            compile(code, '<string>', 'exec')
            return True, None
        except SyntaxError as e:
            error_msg = f"语法错误：第{e.lineno}行，{e.msg}"
            return False, error_msg
        except Exception as e:
            error_msg = f"代码检查错误：{str(e)}"
            return False, error_msg
            
    def get_available_modules(self):
        """
        获取可用的Python模块
        
        Returns:
            list: 可用模块列表
        """
        try:
            import pkgutil
            modules = []
            for importer, modname, ispkg in pkgutil.iter_modules():
                modules.append(modname)
            return sorted(modules)
        except Exception as e:
            print(f"获取模块列表失败：{e}")
            return []
            
    def get_builtin_functions(self):
        """
        获取内置函数列表
        
        Returns:
            list: 内置函数列表
        """
        try:
            builtin_functions = []
            for name in dir(__builtins__):
                if not name.startswith('_'):
                    builtin_functions.append(name)
            return sorted(builtin_functions)
        except Exception as e:
            print(f"获取内置函数列表失败：{e}")
            return []
            
    def is_running(self):
        """
        检查是否正在执行代码
        
        Returns:
            bool: 是否正在执行
        """
        return self.is_running
        
    def set_timeout(self, timeout):
        """
        设置执行超时时间
        
        Args:
            timeout: 超时时间（秒）
        """
        self.execution_timeout = timeout
        
    def get_execution_info(self):
        """
        获取执行信息
        
        Returns:
            dict: 执行信息字典
        """
        return {
            'is_running': self.is_running,
            'timeout': self.execution_timeout,
            'thread_alive': self.execution_thread.is_alive() if self.execution_thread else False
        }
        
    def execute_with_breakpoints(self, code, breakpoints):
        """
        带断点执行代码
        
        Args:
            code: 要执行的代码
            breakpoints: 断点行号列表
        """
        self.debug_mode = True
        self.breakpoints = sorted(breakpoints)
        self.current_line = 0
        self.local_vars = {}
        
        if self.output_callback:
            self.output_callback("=== 调试模式 ===", "info")
            self.output_callback(f"断点: {self.breakpoints}", "info")
            self.output_callback("F7=单步步入 F8=单步跳过 Shift+F8=跳出\n", "info")
            self.output_callback("=" * 50 + "\n", "info")
        
        # 实现真正的断点调试
        self.debug_execute(code)
    
    def _notify_error_line(self, line_number):
        """通知外部错误行号，用于编辑器高亮"""
        if self.error_callback:
            try:
                self.error_callback(line_number)
            except Exception as e:
                print(f"错误高亮回调失败: {e}")
    
    def debug_execute(self, code):
        """
        调试模式执行代码
        
        Args:
            code: 要执行的代码
        """
        try:
            # 首先尝试编译整个代码块
            try:
                compiled_code = compile(code, '<string>', 'exec')
            except SyntaxError as e:
                # 如果有语法错误，直接分析错误
                if self.output_callback:
                    self.output_callback(f"❌ 语法错误: {str(e)}", "error")
                analysis, resolved_line = self.analyze_error_with_context(
                    e, code, getattr(e, 'lineno', 1), {}
                )
                self._notify_error_line(resolved_line)
                if self.output_callback:
                    self.output_callback(analysis, "error")
                return
            
            # 创建执行环境
            global_vars = {'__builtins__': __builtins__}
            local_vars = {}
            
            # 逐行执行代码（模拟调试）
            lines = code.split('\n')
            
            for i, line in enumerate(lines, 1):
                self.current_line = i
                
                # 检查是否到达断点
                if i in self.breakpoints:
                    if self.output_callback:
                        self.output_callback(f"🛑 断点命中 - 第 {i} 行", "warning")
                        self.output_callback(f"代码: {line.strip()}", "info")
                        self.output_callback("等待调试指令...", "info")
                    
                    # 更新调试器面板
                    if self.debugger_callback:
                        self.debugger_callback(i, local_vars, breakpoint_hit=True)
                    
                    # 模拟暂停（实际调试器会在这里暂停）
                    self.show_debug_info(local_vars, i)
                    
                    if self.output_callback:
                        self.output_callback("继续执行...", "info")
                
                # 跳过空行和注释
                if not line.strip() or line.strip().startswith('#'):
                    continue
                
                # 执行当前行
                try:
                    # 尝试执行单行代码
                    line_code = compile(line, '<string>', 'exec')
                    exec(line_code, global_vars, local_vars)
                    self.local_vars = local_vars.copy()
                    
                    # 显示变量变化
                    if '=' in line and not line.strip().startswith('#'):
                        var_name = line.split('=')[0].strip()
                        if var_name in local_vars:
                            if self.output_callback:
                                self.output_callback(f"  {var_name} = {repr(local_vars[var_name])}", "success")
                    
                    # 更新调试器面板
                    if self.debugger_callback:
                        self.debugger_callback(i, local_vars, breakpoint_hit=False)
                
                except Exception as e:
                    if self.output_callback:
                        self.output_callback(f"❌ 第 {i} 行执行错误: {str(e)}", "error")
                    # 使用完整的代码上下文进行错误分析
                    analysis, resolved_line = self.analyze_error_with_context(e, code, i, local_vars)
                    self._notify_error_line(resolved_line)
                    if self.output_callback:
                        self.output_callback(analysis, "error")
                    break
            
            if self.output_callback:
                self.output_callback("\n✅ 调试执行完成", "success")
                self.output_callback("=" * 50 + "\n", "info")
                
        except Exception as e:
            if self.output_callback:
                self.output_callback(f"❌ 调试执行失败: {str(e)}", "error")
            analysis, resolved_line = self.analyze_error_with_context(e, code, 1, {})
            self._notify_error_line(resolved_line)
            if self.output_callback:
                self.output_callback(analysis, "error")
    
    def show_debug_info(self, local_vars, current_line):
        """
        显示调试信息
        
        Args:
            local_vars: 局部变量
            current_line: 当前行号
        """
        if self.output_callback:
            self.output_callback(f"📍 当前位置: 第 {current_line} 行", "info")
            
            if local_vars:
                self.output_callback("📊 当前变量:", "info")
                for name, value in local_vars.items():
                    if not name.startswith('_'):
                        self.output_callback(f"  {name} = {repr(value)}", "success")
            else:
                self.output_callback("📊 当前无局部变量", "info")
            
            self.output_callback("-" * 30, "info")
        
    def analyze_error(self, error, code):
        """
        分析错误并提供代码提示
        
        Args:
            error: 错误对象
            code: 源代码
            
        Returns:
            str: 错误提示信息
        """
        error_type = type(error).__name__
        error_msg = str(error)
        
        # 尝试从错误中提取行号
        error_line = None
        try:
            import traceback
            import sys
            exc_type, exc_value, exc_tb = sys.exc_info()
            if exc_tb:
                error_line = exc_tb.tb_lineno
        except:
            pass
        
        # 常见错误提示和修改方案
        tips = {
            'SyntaxError': {
                'tip': """
语法错误提示：
• 检查括号、引号是否配对
• 确认缩进是否正确（Python使用4个空格）
• 检查是否缺少冒号（if、for、def后面）
• 确认关键字拼写正确""",
                'fix': """
修改建议：
```python
# 常见问题1: 缺少冒号
if x > 5:  # ← 确保有冒号
    print("大于5")

# 常见问题2: 括号不配对
result = (1 + 2) * 3  # ← 确保括号配对

# 常见问题3: 缩进错误
def my_func():
    print("正确缩进4个空格")  # ← 4个空格
```"""
            },
            
            'NameError': {
                'tip': """
变量名错误提示：
• 检查变量是否已定义
• 确认变量名拼写正确
• 确保在使用前已赋值
• 检查是否在正确的作用域内""",
                'fix': """
修改建议：
```python
# 正确做法：先定义再使用
x = 10  # ← 先定义变量
print(x)  # ← 再使用

# 常见错误：使用未定义的变量
# print(y)  # ← 错误：y未定义

# 解决方法：
y = 20
print(y)  # ← 正确
```"""
            },
            
            'TypeError': {
                'tip': """
类型错误提示：
• 检查操作数的类型是否匹配
• 确认函数参数类型正确
• 尝试使用类型转换（int(), str(), float()）
• 检查是否对不可变对象进行修改""",
                'fix': """
修改建议：
```python
# 常见问题：类型不匹配
# result = "5" + 3  # ← 错误：字符串不能直接加数字

# 解决方法1：转换为数字
result = int("5") + 3
print(result)  # 8

# 解决方法2：都转为字符串
result = "5" + str(3)
print(result)  # "53"
```"""
            },
            
            'IndexError': {
                'tip': """
索引错误提示：
• 检查列表/元组索引是否超出范围
• 记住索引从0开始
• 使用len()函数检查长度
• 考虑使用try-except处理""",
                'fix': """
修改建议：
```python
fruits = ["苹果", "香蕉", "橙子"]

# 常见错误：索引超出范围
# print(fruits[3])  # ← 错误：只有0,1,2

# 解决方法：检查索引范围
if len(fruits) > 3:
    print(fruits[3])
else:
    print("索引超出范围")

# 或使用try-except
try:
    print(fruits[3])
except IndexError:
    print("索引不存在")
```"""
            },
            
            'KeyError': {
                'tip': """
键错误提示：
• 检查字典键是否存在
• 使用dict.get()方法安全访问
• 确认键名拼写正确
• 考虑先检查键是否存在""",
                'fix': """
修改建议：
```python
person = {"name": "张三", "age": 25}

# 常见错误：键不存在
# print(person["email"])  # ← 错误：email键不存在

# 解决方法1：使用get()方法
email = person.get("email", "未设置")
print(email)  # "未设置"

# 解决方法2：先检查键是否存在
if "email" in person:
    print(person["email"])
else:
    print("email键不存在")
```"""
            },
            
            'ValueError': {
                'tip': """
值错误提示：
• 检查函数参数值是否有效
• 确认类型转换的输入格式
• 使用try-except处理转换错误
• 验证输入数据的有效性""",
                'fix': """
修改建议：
```python
# 常见问题：类型转换失败
# num = int("abc")  # ← 错误："abc"不能转为整数

# 解决方法：使用try-except
try:
    num = int(input("请输入数字："))
    print(f"您输入的是：{num}")
except ValueError:
    print("输入的不是有效数字！")
    num = 0  # 使用默认值
```"""
            },
            
            'ZeroDivisionError': {
                'tip': """
除零错误提示：
• 检查除数是否为零
• 在除法前添加条件检查
• 使用try-except处理
• 考虑使用默认值""",
                'fix': """
修改建议：
```python
# 常见问题：除以零
x = 10
y = 0
# result = x / y  # ← 错误：不能除以0

# 解决方法1：条件检查
if y != 0:
    result = x / y
    print(result)
else:
    print("除数不能为零！")
    result = 0

# 解决方法2：try-except
try:
    result = x / y
except ZeroDivisionError:
    print("除数为零，使用默认值")
    result = 0
```"""
            }
        }
        
        # 获取错误提示和修改方案
        error_info = tips.get(error_type, {
            'tip': """
通用错误提示：
• 仔细阅读错误消息
• 检查错误提示的行号
• 使用print()调试变量值
• 尝试简化代码逐步调试""",
            'fix': """
修改建议：
请在AI助手中输入具体的错误信息获取帮助。"""
        })
        
        tip = error_info.get('tip', '') if isinstance(error_info, dict) else error_info
        fix = error_info.get('fix', '') if isinstance(error_info, dict) else ''
        
        # 构建完整的错误信息
        result = f"""
❌ 错误类型: {error_type}
📍 错误信息: {error_msg}
"""
        
        if error_line:
            result += f"📌 错误行号: 第 {error_line} 行\n"
        
        result += f"""
💡 {tip}

🔧 {fix}

🤖 AI助手建议：
向右下角AI助手提问："{error_type}错误如何解决？"
AI会根据您的具体代码提供更详细的修改方案。
"""
        
        return result
        
    def analyze_error_with_context(self, error, code, error_line, local_vars):
        """
        基于代码上下文分析错误并提供准确建议
        
        Args:
            error: 错误对象
            code: 源代码
            error_line: 错误行号
            local_vars: 局部变量字典
            
        Returns:
            tuple[str, Optional[int]]: (错误分析文案, 定位后的行号)
        """
        error_type = type(error).__name__
        error_msg = str(error)
        
        # 分析代码行
        code_lines = code.split('\n')
        
        # 智能分析错误行号
        error_code_line = ""  # 初始化变量
        if error_line and error_line <= len(code_lines):
            original_error_line = error_line
            error_code_line = code_lines[error_line - 1]
            
            # 对于IndentationError，进一步分析错误行号
            if isinstance(error, IndentationError):
                # 如果错误行是空行，可能错误在上一行
                if not error_code_line.strip():
                    # 向前查找非空行
                    for i in range(error_line - 1, 0, -1):
                        if code_lines[i - 1].strip():
                            error_line = i
                            break
                # 如果错误行以冒号结尾，错误可能在下一行（缺少缩进）
                elif error_code_line.strip().endswith(':'):
                    # 向后查找下一行
                    if error_line < len(code_lines):
                        next_line = code_lines[error_line].strip()
                        if not next_line or not next_line.startswith((' ', '\t')):
                            # 下一行没有缩进，错误在下一行
                            error_line = error_line + 1
            
            # 对于SyntaxError，检查是否有上下文问题
            elif isinstance(error, SyntaxError):
                # 检查是否是函数定义问题
                if "'return' outside function" in str(error):
                    # 向前查找最近的函数定义
                    for i in range(error_line - 1, 0, -1):
                        line = code_lines[i - 1].strip()
                        if line.startswith('def '):
                            # 检查函数定义是否完整
                            if not line.endswith(':'):
                                error_line = i  # 函数定义缺少冒号
                            break
                        elif line and not line.startswith(' ') and not line.startswith('\t'):
                            # 找到非缩进的代码行，可能是函数定义问题
                            if 'def' in line or line.startswith('class '):
                                error_line = i
                            break
            
            # 更新错误代码行
            if error_line != original_error_line:
                error_code_line = code_lines[error_line - 1] if 0 < error_line <= len(code_lines) else ""
        
        # 获取上下文（前后2行）
        context_start = max(0, (error_line or 1) - 3)
        context_end = min(len(code_lines), (error_line or 1) + 2)
        context_lines = code_lines[context_start:context_end]
        
        # 构建基础错误信息（使用特殊标记，稍后在控制台用颜色显示）
        result = f"\n{'=' * 60}\n"
        result += f"❌ 错误类型: {error_type}\n"
        result += f"📍 错误信息: {error_msg}\n"
        
        if error_line:
            result += f"📌 错误位置: 第 {error_line} 行\n"
            result += f"\n错误代码:\n"
            result += f"  {error_line} | {error_code_line}\n"
        
        result += f"\n代码上下文:\n"
        for i, line in enumerate(context_lines, start=context_start + 1):
            marker = "→" if i == error_line else " "
            result += f"  {marker} {i:3} | {line}\n"
        
        # 分析具体错误并提供准确建议
        suggestion = self._generate_smart_suggestion(error_type, error_msg, error_code_line, code_lines, error_line, local_vars)
        
        result += f"\n💡 智能分析:\n{suggestion}\n"
        result += f"\n🤖 AI助手:\n向右下角AI助手提问可获取更详细的解决方案。\n"
        result += f"{'=' * 60}\n"
        
        return result, error_line
        
    def _generate_smart_suggestion(self, error_type, error_msg, error_line_code, all_lines, error_line, local_vars):
        """生成智能建议"""
        
        if error_type == 'NameError':
            # 提取未定义的变量名
            import re
            match = re.search(r"name '(\w+)'", error_msg)
            var_name = match.group(1) if match else "变量"
            
            # 检查是否是拼写错误
            defined_vars = list(local_vars.keys())
            similar_vars = [v for v in defined_vars if v.lower().startswith(var_name[0].lower())]
            
            suggestion = f"变量 '{var_name}' 未定义。\n\n"
            
            if similar_vars:
                suggestion += f"【建议】您可能想使用以下变量：\n"
                for v in similar_vars:
                    suggestion += f"  - {v} (已定义)\n"
                suggestion += f"\n【修改方案】将 '{var_name}' 改为 '{similar_vars[0]}'\n"
            else:
                suggestion += f"【建议】在使用 '{var_name}' 之前先定义它：\n"
                suggestion += f"\n【修改方案】\n"
                suggestion += f"  {var_name} = 初始值  # 在第{error_line}行之前添加\n"
                suggestion += f"  {error_line_code.strip()}\n"
            
            return suggestion
            
        elif error_type == 'TypeError':
            suggestion = "类型不匹配错误。\n\n"
            
            # 分析错误信息
            if "unsupported operand type" in error_msg:
                suggestion += "【问题】尝试对不兼容的类型进行运算。\n\n"
                suggestion += "【建议】检查运算符两侧的数据类型：\n"
                suggestion += "  - 字符串和数字相加需要先转换类型\n"
                suggestion += "  - 使用 int(), str(), float() 进行转换\n\n"
                suggestion += "【修改方案】\n"
                suggestion += "  # 如果是字符串转数字：\n"
                suggestion += "  result = int(字符串变量) + 数字\n"
                suggestion += "  # 如果是数字转字符串：\n"
                suggestion += "  result = str(数字变量) + 字符串\n"
            else:
                suggestion += f"【错误详情】{error_msg}\n"
                suggestion += "【建议】检查函数调用的参数类型是否正确。\n"
            
            return suggestion
            
        elif error_type == 'IndexError':
            suggestion = "索引超出范围。\n\n"
            suggestion += f"【问题】尝试访问不存在的索引位置。\n\n"
            
            # 尝试提取索引信息
            suggestion += "【建议】\n"
            suggestion += "  1. 检查列表/字符串的长度\n"
            suggestion += "  2. 记住索引从0开始\n"
            suggestion += "  3. 使用 len() 函数验证长度\n\n"
            suggestion += "【修改方案】\n"
            suggestion += "  # 添加索引范围检查：\n"
            suggestion += "  if 索引 < len(列表):\n"
            suggestion += f"      {error_line_code.strip()}\n"
            suggestion += "  else:\n"
            suggestion += "      print('索引超出范围')\n"
            
            return suggestion
            
        elif error_type == 'KeyError':
            # 提取键名
            import re
            match = re.search(r"'(\w+)'", error_msg)
            key_name = match.group(1) if match else "键"
            
            suggestion = f"字典键 '{key_name}' 不存在。\n\n"
            suggestion += "【建议】\n"
            suggestion += "  1. 检查键名拼写是否正确\n"
            suggestion += "  2. 使用 dict.get() 方法安全访问\n"
            suggestion += "  3. 先检查键是否存在\n\n"
            suggestion += "【修改方案】\n"
            suggestion += f"  # 方法1: 使用get()避免错误\n"
            suggestion += f"  value = 字典.get('{key_name}', 默认值)\n\n"
            suggestion += f"  # 方法2: 先检查键是否存在\n"
            suggestion += f"  if '{key_name}' in 字典:\n"
            suggestion += f"      {error_line_code.strip()}\n"
            
            return suggestion
            
        elif error_type == 'ZeroDivisionError':
            suggestion = "除数为零错误。\n\n"
            suggestion += "【问题】尝试除以零。\n\n"
            suggestion += "【建议】在除法运算前检查除数是否为零。\n\n"
            suggestion += "【修改方案】\n"
            suggestion += "  # 添加零检查：\n"
            suggestion += "  if 除数 != 0:\n"
            suggestion += f"      {error_line_code.strip()}\n"
            suggestion += "  else:\n"
            suggestion += "      print('除数不能为零')\n"
            suggestion += "      result = 0  # 或其他默认值\n"
            
            return suggestion
            
        elif error_type == 'ValueError':
            suggestion = "值错误。\n\n"
            
            if "invalid literal" in error_msg:
                suggestion += "【问题】类型转换失败（输入的值无法转换）。\n\n"
                suggestion += "【建议】使用try-except处理可能的转换错误。\n\n"
                suggestion += "【修改方案】\n"
                suggestion += "  try:\n"
                suggestion += f"      {error_line_code.strip()}\n"
                suggestion += "  except ValueError:\n"
                suggestion += "      print('输入的值无法转换为数字')\n"
                suggestion += "      # 使用默认值或重新输入\n"
            else:
                suggestion += f"【错误详情】{error_msg}\n"
                suggestion += "【建议】检查函数参数的值是否在有效范围内。\n"
            
            return suggestion
            
        elif error_type == 'SyntaxError':
            suggestion = "语法错误。\n\n"
            
            # 根据具体错误信息提供针对性建议
            if "'return' outside function" in error_msg:
                suggestion += "【问题分析】\n"
                suggestion += "  return语句出现在函数外部。\n\n"
                suggestion += "【常见原因】\n"
                suggestion += "  1. 函数定义不完整（缺少def关键字）\n"
                suggestion += "  2. 函数定义后缺少冒号\n"
                suggestion += "  3. return语句的缩进不正确\n\n"
                suggestion += "【修改方案】\n"
                suggestion += "  1. 检查return语句前是否有完整的函数定义：\n"
                suggestion += "     def 函数名(参数):\n"
                suggestion += "         # 函数体\n"
                suggestion += "         return 返回值\n"
                suggestion += "  2. 确保return语句在函数内部（有正确的缩进）\n"
                suggestion += "  3. 如果不需要函数，直接删除return语句\n"
                
            elif "invalid syntax" in error_msg:
                suggestion += "【问题分析】\n"
                suggestion += "  代码语法不正确。\n\n"
                suggestion += "【常见原因】\n"
                suggestion += "  1. 缺少冒号（if、for、def、class后面）\n"
                suggestion += "  2. 括号、引号不配对\n"
                suggestion += "  3. 缩进不正确\n"
                suggestion += "  4. 使用了中文符号\n\n"
                suggestion += "【修改方案】\n"
                suggestion += "  检查错误行的语法，确保：\n"
                suggestion += "  - 控制语句后有冒号\n"
                suggestion += "  - 括号完整配对\n"
                suggestion += "  - 使用4个空格缩进\n"
                
            elif "unexpected indent" in error_msg:
                suggestion += "【问题分析】\n"
                suggestion += "  缩进不正确。\n\n"
                suggestion += "【修改方案】\n"
                suggestion += "  1. 检查缩进是否一致（建议使用4个空格）\n"
                suggestion += "  2. 确保同级代码缩进相同\n"
                suggestion += "  3. 避免混合使用空格和Tab键\n"
                
            else:
                # 通用语法错误建议
                suggestion += "【常见原因】\n"
                suggestion += "  1. 缺少冒号（if、for、def、class后面）\n"
                suggestion += "  2. 括号、引号不配对\n"
                suggestion += "  3. 缩进不正确\n"
                suggestion += "  4. 使用了中文符号\n\n"
                suggestion += "【修改方案】\n"
                suggestion += "  检查错误行的语法，确保：\n"
                suggestion += "  - 控制语句后有冒号\n"
                suggestion += "  - 括号完整配对\n"
                suggestion += "  - 使用4个空格缩进\n"
            
            return suggestion
            
        else:
            # 通用建议
            suggestion = f"发生了{error_type}错误。\n\n"
            suggestion += "【建议】\n"
            suggestion += "  1. 仔细阅读错误信息\n"
            suggestion += "  2. 检查错误行的代码逻辑\n"
            suggestion += "  3. 使用print()输出中间变量值\n"
            suggestion += "  4. 向AI助手询问详细解决方案\n"
            
            return suggestion
