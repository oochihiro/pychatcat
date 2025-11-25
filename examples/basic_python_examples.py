# -*- coding: utf-8 -*-
"""
Python基础语法示例
可以在智能Python学习桌面应用中运行这些示例
"""

# 1. 变量和数据类型
print("=== 变量和数据类型 ===")
name = "张三"
age = 25
height = 175.5
is_student = True

print(f"姓名：{name}")
print(f"年龄：{age}")
print(f"身高：{height}cm")
print(f"是否为学生：{is_student}")

# 2. 列表操作
print("\n=== 列表操作 ===")
fruits = ["苹果", "香蕉", "橙子"]
print("水果列表：", fruits)

# 添加元素
fruits.append("葡萄")
print("添加葡萄后：", fruits)

# 列表推导式
squares = [x**2 for x in range(1, 6)]
print("平方数列表：", squares)

# 3. 字典操作
print("\n=== 字典操作 ===")
person = {
    "name": "李四",
    "age": 30,
    "city": "北京",
    "hobbies": ["读书", "游泳", "编程"]
}
print("个人信息：", person)
print("姓名：", person["name"])
print("爱好：", person["hobbies"])

# 4. 函数定义和调用
print("\n=== 函数定义和调用 ===")
def greet(name, age=18):
    """问候函数"""
    return f"你好，{name}！你{age}岁了。"

result = greet("小明", 20)
print(result)

# 使用默认参数
result2 = greet("小红")
print(result2)

# 5. 循环结构
print("\n=== 循环结构 ===")
# for循环
print("for循环示例：")
for i in range(3):
    print(f"循环次数：{i}")

# while循环
print("while循环示例：")
count = 0
while count < 3:
    print(f"计数：{count}")
    count += 1

# 6. 条件语句
print("\n=== 条件语句 ===")
score = 85

if score >= 90:
    grade = "优秀"
elif score >= 80:
    grade = "良好"
elif score >= 70:
    grade = "中等"
elif score >= 60:
    grade = "及格"
else:
    grade = "不及格"

print(f"分数：{score}，等级：{grade}")

# 7. 异常处理
print("\n=== 异常处理 ===")
try:
    number = int("123")
    result = 100 / number
    print(f"计算结果：{result}")
except ValueError:
    print("输入的不是有效数字！")
except ZeroDivisionError:
    print("不能除以零！")
except Exception as e:
    print(f"发生未知错误：{e}")
else:
    print("代码执行成功！")
finally:
    print("无论如何都会执行")

# 8. 文件操作
print("\n=== 文件操作 ===")
try:
    # 写入文件
    with open("temp_example.txt", "w", encoding="utf-8") as f:
        f.write("这是一个示例文件\n")
        f.write("包含多行文本\n")
        f.write("用于演示文件操作")
    
    # 读取文件
    with open("temp_example.txt", "r", encoding="utf-8") as f:
        content = f.read()
        print("文件内容：")
        print(content)
        
    # 清理临时文件
    import os
    os.remove("temp_example.txt")
    print("临时文件已删除")
    
except Exception as e:
    print(f"文件操作错误：{e}")

# 9. 类和对象
print("\n=== 类和对象 ===")
class Student:
    def __init__(self, name, age, grade):
        self.name = name
        self.age = age
        self.grade = grade
    
    def introduce(self):
        return f"我是{self.name}，{self.age}岁，{self.grade}年级学生"
    
    def study(self, subject):
        return f"{self.name}正在学习{subject}"

# 创建对象
student1 = Student("王五", 16, "高一")
print(student1.introduce())
print(student1.study("数学"))

# 10. 模块导入
print("\n=== 模块导入 ===")
import datetime

now = datetime.datetime.now()
print(f"当前时间：{now.strftime('%Y-%m-%d %H:%M:%S')}")

# 使用数学模块
import math
print(f"圆周率：{math.pi}")
print(f"2的平方根：{math.sqrt(2)}")

print("\n=== 示例运行完成 ===")
print("这些示例展示了Python的基础语法和常用功能。")
print("你可以在代码编辑器中修改这些代码，然后运行查看结果。")

