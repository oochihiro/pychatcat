# -*- coding: utf-8 -*-
"""
DeepSeek AI客户端
使用OpenAI SDK调用DeepSeek API
"""

import os
import base64
from typing import Optional, List, Dict

# 尝试导入openai库
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class DeepSeekClient:
    """DeepSeek AI客户端"""
    
    def __init__(self):
        """初始化DeepSeek客户端"""
        # API密钥（加密存储）
        self._encrypted_key = "c2stYTk4YTMzMzg4NDQ1NDA3MDhiNTdlYzg3YTIxMjQ5Y2E="
        self.api_key = self._decrypt_key()
        self.base_url = "https://api.deepseek.com/v1"
        self.model = "deepseek-chat"
        self.client = None
        self.conversation_history = []
        self.is_available = OPENAI_AVAILABLE and bool(self.api_key)
        
        if self.is_available:
            self._init_client()
    
    def _decrypt_key(self) -> str:
        """解密API密钥"""
        try:
            return base64.b64decode(self._encrypted_key).decode('utf-8')
        except:
            return ""
    
    def _init_client(self):
        """初始化OpenAI客户端"""
        try:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        except Exception as e:
            print(f"初始化DeepSeek客户端失败: {e}")
            self.is_available = False
    
    def get_python_help(self, question: str, learning_mode: str = "基础语法") -> str:
        """
        获取Python学习帮助
        
        Args:
            question: 用户问题
            learning_mode: 学习模式
            
        Returns:
            AI回复内容
        """
        if not self.is_available:
            return self._get_fallback_response(question)
        
        try:
            # 构建系统提示词
            system_prompt = f"""你是一位专业的Python编程导师，专门帮助初学者学习Python编程。

当前学习模式：{learning_mode}

你的任务：
1. 用简洁明了的中文回答Python相关问题
2. 提供适合在左侧代码编辑器中运行的代码示例（使用```python标记）
3. 解释概念时使用通俗易懂的语言
4. 鼓励学习者直接在左侧编辑器中实践
5. 回答要简洁实用（200-300字为宜）

回答格式要求：
- 先简要回答问题核心
- 提供1个可直接在左侧编辑器运行的代码示例
- 给出1-2条实用的学习建议
- 强调"请在左侧编辑器中尝试运行这段代码"

重要提示：
- 不要建议使用VS Code或其他外部工具
- 专注于左侧代码编辑器的使用
- 代码示例要完整且可立即运行
- 避免冗长的解释，重点在实践

请始终用中文回答，并且要简洁、实用、适合编辑器使用。"""
            
            # 准备消息
            messages = [
                {"role": "system", "content": system_prompt},
            ]
            
            # 添加对话历史（最近4轮）
            for msg in self.conversation_history[-8:]:
                messages.append(msg)
            
            # 添加当前问题
            messages.append({"role": "user", "content": question})
            
            # 调用DeepSeek API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1500,
                temperature=0.7,
                stream=False
            )
            
            # 提取回复
            reply = response.choices[0].message.content
            
            # 保存对话历史
            self.conversation_history.append({"role": "user", "content": question})
            self.conversation_history.append({"role": "assistant", "content": reply})
            
            # 限制历史记录长度
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return reply
            
        except Exception as e:
            error_msg = str(e)
            print(f"DeepSeek API调用失败: {error_msg}")
            
            # 如果是API错误，返回友好的错误信息
            if "rate_limit" in error_msg.lower():
                return "⚠️ API调用频率过高，请稍后再试。\n\n" + self._get_fallback_response(question)
            elif "invalid" in error_msg.lower() or "unauthorized" in error_msg.lower():
                return "⚠️ API服务暂时不可用，使用本地助手回复。\n\n" + self._get_fallback_response(question)
            else:
                return self._get_fallback_response(question)
    
    def _get_fallback_response(self, question: str) -> str:
        """
        备用回复（当API不可用时）
        
        Args:
            question: 用户问题
            
        Returns:
            备用回复内容
        """
        question_lower = question.lower()
        
        # 知识库回复
        responses = {
            "变量": """**变量是Python中存储数据的基本方式。**

**核心概念：**
- 变量就像一个标签，指向内存中的数据
- Python是动态类型语言，类型自动确定
- 变量名要遵循命名规范（字母、数字、下划线）

**示例代码：**
```python
# 定义不同类型的变量
name = "张三"          # 字符串
age = 25              # 整数
height = 175.5        # 浮点数
is_student = True     # 布尔值

# 打印变量
print(f"姓名：{name}，年龄：{age}岁")
print(f"身高：{height}cm，学生：{is_student}")

# 变量可以重新赋值
age = 26
print(f"新年龄：{age}")
```

**学习建议：**
1. 在代码编辑器中尝试定义各种类型的变量
2. 实验变量的赋值和修改
3. 使用有意义的变量名，提高代码可读性

💡 提示：按F5运行代码查看结果！""",

            "函数": """**函数是组织和复用代码的重要方式。**

**核心概念：**
- 函数将一组操作封装成可重复调用的单元
- 可以接受参数，返回结果
- 支持默认参数和关键字参数

**示例代码：**
```python
# 定义一个简单函数
def greet(name, age=18):
    \"\"\"问候函数\"\"\"
    message = f"你好，{name}！你今年{age}岁。"
    return message

# 调用函数
result1 = greet("小明", 20)
print(result1)

# 使用默认参数
result2 = greet("小红")
print(result2)

# 定义计算函数
def calculate_area(length, width):
    \"\"\"计算矩形面积\"\"\"
    return length * width

area = calculate_area(5, 3)
print(f"面积：{area}")
```

**学习建议：**
1. 从简单的函数开始，理解参数和返回值
2. 给函数写文档字符串，说明功能
3. 练习编写实用的小函数

💡 提示：函数让代码更模块化、更易维护！""",

            "列表": """**列表是Python中最常用的数据结构。**

**核心概念：**
- 列表可以存储多个元素，元素可以是不同类型
- 支持索引访问、切片操作
- 可以动态添加、删除元素

**示例代码：**
```python
# 创建列表
fruits = ["苹果", "香蕉", "橙子"]
numbers = [1, 2, 3, 4, 5]

# 访问元素
print(fruits[0])      # 第一个：苹果
print(fruits[-1])     # 最后一个：橙子

# 添加元素
fruits.append("葡萄")      # 末尾添加
fruits.insert(1, "梨")     # 指定位置插入

# 删除元素
fruits.remove("香蕉")      # 删除指定值
del fruits[0]             # 删除指定索引

# 列表推导式
squares = [x**2 for x in range(1, 6)]
print(f"平方数：{squares}")

# 遍历列表
for i, fruit in enumerate(fruits, 1):
    print(f"{i}. {fruit}")
```

**学习建议：**
1. 练习列表的基本操作（增删改查）
2. 掌握列表推导式，简化代码
3. 结合循环使用列表处理批量数据

💡 提示：列表是处理多个数据的首选工具！""",

            "循环": """**循环用于重复执行代码块。**

**核心概念：**
- for循环：遍历序列或执行固定次数
- while循环：根据条件重复执行
- break和continue控制循环流程

**示例代码：**
```python
# for循环基础
print("=== for循环示例 ===")
fruits = ["苹果", "香蕉", "橙子"]
for fruit in fruits:
    print(f"我喜欢{fruit}")

# 使用range
print("\\n=== range循环 ===")
for i in range(1, 6):
    print(f"数字：{i}")

# 带索引的循环
print("\\n=== 带索引循环 ===")
for index, fruit in enumerate(fruits, 1):
    print(f"{index}. {fruit}")

# while循环
print("\\n=== while循环 ===")
count = 0
while count < 3:
    print(f"计数：{count}")
    count += 1

# 循环控制
print("\\n=== 循环控制 ===")
for i in range(10):
    if i == 3:
        continue  # 跳过3
    if i == 7:
        break     # 遇到7停止
    print(i)
```

**学习建议：**
1. 理解for和while的使用场景
2. 掌握range()函数生成数字序列
3. 练习使用break和continue控制流程

💡 提示：循环是处理重复任务的利器！""",

            "字典": """**字典是存储键值对的数据结构。**

**核心概念：**
- 使用键（key）来访问值（value）
- 键必须是唯一的、不可变的
- 非常适合存储结构化数据

**示例代码：**
```python
# 创建字典
person = {
    "name": "张三",
    "age": 25,
    "city": "北京",
    "hobbies": ["读书", "编程", "旅游"]
}

# 访问元素
print(f"姓名：{person['name']}")
print(f"年龄：{person['age']}")

# 安全访问（避免KeyError）
email = person.get("email", "未设置")
print(f"邮箱：{email}")

# 修改和添加
person["age"] = 26          # 修改
person["job"] = "程序员"     # 添加

# 删除键值对
del person["city"]

# 遍历字典
print("\\n=== 遍历字典 ===")
for key, value in person.items():
    print(f"{key}: {value}")

# 只遍历键或值
print("\\n所有键：", person.keys())
print("所有值：", person.values())
```

**学习建议：**
1. 理解字典的键值对概念
2. 使用get()方法安全访问
3. 练习遍历和操作字典数据

💡 提示：字典特别适合存储对象的属性！""",

            "异常": """**异常处理让程序更健壮。**

**核心概念：**
- try-except捕获和处理错误
- 不同异常类型对应不同错误
- finally块无论如何都会执行

**示例代码：**
```python
# 基础异常处理
print("=== 异常处理示例 ===")
try:
    number = int(input("请输入一个数字："))
    result = 10 / number
    print(f"结果：{result}")
    
except ValueError:
    print("❌ 错误：输入的不是有效数字！")
except ZeroDivisionError:
    print("❌ 错误：不能除以零！")
except Exception as e:
    print(f"❌ 未知错误：{e}")
else:
    print("✅ 计算成功完成！")
finally:
    print("程序执行结束")

# 文件操作异常处理
print("\\n=== 文件操作示例 ===")
try:
    with open("data.txt", "r") as f:
        content = f.read()
        print(content)
except FileNotFoundError:
    print("❌ 文件不存在！")
except Exception as e:
    print(f"❌ 读取错误：{e}")
```

**常见异常类型：**
- ValueError: 值错误
- ZeroDivisionError: 除零错误
- FileNotFoundError: 文件未找到
- IndexError: 索引超出范围
- KeyError: 字典键不存在

**学习建议：**
1. 总是处理可能出错的操作
2. 捕获具体的异常类型
3. 使用try-except-else-finally结构

💡 提示：异常处理让程序更专业！"""
        }
        
        # 查找匹配的回复
        for keyword, response in responses.items():
            if keyword in question_lower:
                return response
        
        # 通用回复
        if "hello" in question_lower or "你好" in question_lower:
            return """**你好！欢迎使用Python学习助手！** 👋

我可以帮助您：
• 解释Python语法和概念
• 提供实用代码示例
• 解答编程问题
• 给出学习建议

**试试这些问题：**
- "什么是变量？"
- "如何使用函数？"
- "列表和字典有什么区别？"
- "怎样处理异常？"

💡 **快速上手：**
1. 查看左侧代码编辑器中的示例
2. 按F5运行代码
3. 在控制台查看结果
4. 向我提问学习更多！

开始您的Python学习之旅吧！🚀"""
        
        return f"""**关于您的问题：** {question}

💡 **学习建议：**
1. 在左侧代码编辑器中编写相关代码
2. 使用"Python"菜单插入代码模板
3. 按F5运行代码观察结果
4. 查看控制台的输出和错误信息

**推荐操作：**
- 尝试修改示例代码
- 实验不同的参数值
- 对比不同写法的效果

**学习资源：**
- Python官方文档
- 在线编程练习平台
- 编程社区和论坛

您可以问得更具体些，比如"如何定义函数？"或"列表怎么用？"我会提供详细的解答和代码示例！"""
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
    
    def test_connection(self) -> bool:
        """测试API连接"""
        if not self.is_available:
            return False
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "测试"}],
                max_tokens=10
            )
            return True
        except:
            return False


class AIClientManager:
    """AI客户端管理器"""
    
    def __init__(self):
        """初始化管理器"""
        self.deepseek_client = DeepSeekClient()
        self.use_deepseek = self.deepseek_client.is_available
    
    def get_response(self, question: str, learning_mode: str = "基础语法") -> str:
        """获取AI回复"""
        return self.deepseek_client.get_python_help(question, learning_mode)
    
    def clear_history(self):
        """清空对话历史"""
        self.deepseek_client.clear_history()
    
    def test_connection(self) -> bool:
        """测试连接"""
        return self.deepseek_client.test_connection()
    
    def is_available(self) -> bool:
        """检查是否可用"""
        return self.deepseek_client.is_available
    
    def get_status(self) -> str:
        """获取状态信息"""
        if self.deepseek_client.is_available:
            return "DeepSeek AI"
        elif not OPENAI_AVAILABLE:
            return "需要安装openai库"
        else:
            return "本地助手"
