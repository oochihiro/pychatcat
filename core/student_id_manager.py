#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学生ID管理器
用于获取和管理学生的学号/姓名
"""

import os
import json
import tkinter as tk
from tkinter import simpledialog, messagebox
from typing import Optional

STUDENT_ID_FILE = os.path.join("data", "student_id.json")


def get_student_id(force_prompt: bool = False) -> Optional[str]:
    """
    获取学生ID
    如果不存在，弹出对话框让学生输入
    
    Args:
        force_prompt: 是否强制弹出对话框（用于修改学号）
    """
    # 确保数据目录存在
    os.makedirs(os.path.dirname(STUDENT_ID_FILE), exist_ok=True)
    
    saved_student_id = None
    
    # 尝试从文件读取
    if os.path.exists(STUDENT_ID_FILE) and not force_prompt:
        try:
            with open(STUDENT_ID_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                saved_student_id = data.get('student_id', '').strip()
                if saved_student_id:
                    return saved_student_id
        except Exception:
            pass
    
    # 如果不存在或强制提示，弹出对话框
    new_student_id = prompt_student_id(saved_student_id)
    
    # 如果输入了新的学号，且与保存的不同，需要确认
    if new_student_id and saved_student_id and new_student_id != saved_student_id:
        if not confirm_student_id_change(saved_student_id, new_student_id):
            # 用户取消，返回原来的学号
            return saved_student_id
    
    return new_student_id


def confirm_student_id_change(old_id: str, new_id: str) -> bool:
    """
    确认学号变更
    如果学生输入了不同的学号，弹出确认对话框
    """
    root = tk.Tk()
    root.withdraw()
    
    dialog = tk.Toplevel(root)
    dialog.title("学号变更确认")
    dialog.geometry("500x250")
    dialog.resizable(False, False)
    
    # 居中显示
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
    y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")
    
    # 警告信息
    warning_text = f"""检测到学号变更！

原学号: {old_id}
新学号: {new_id}

⚠️ 重要提示：
• 学号变更后，新的学习数据将使用新学号记录
• 之前的学习数据仍使用原学号
• 这可能导致您的学习数据分散到不同的学号下
• 建议保持学号一致，以便完整追踪学习过程

是否确认使用新学号？"""
    
    label = tk.Label(
        dialog,
        text=warning_text,
        font=('Arial', 10),
        justify=tk.LEFT,
        padx=20,
        pady=20
    )
    label.pack()
    
    result = {'confirmed': False}
    
    def on_confirm():
        result['confirmed'] = True
        dialog.destroy()
    
    def on_cancel():
        result['confirmed'] = False
        dialog.destroy()
    
    # 按钮
    button_frame = tk.Frame(dialog)
    button_frame.pack(pady=20)
    
    confirm_button = tk.Button(
        button_frame,
        text="确认使用新学号",
        command=on_confirm,
        width=15,
        font=('Arial', 10),
        bg='#ff6b6b',
        fg='white'
    )
    confirm_button.pack(side=tk.LEFT, padx=10)
    
    cancel_button = tk.Button(
        button_frame,
        text="取消，使用原学号",
        command=on_cancel,
        width=15,
        font=('Arial', 10)
    )
    cancel_button.pack(side=tk.LEFT, padx=10)
    
    dialog.wait_window()
    root.destroy()
    
    return result['confirmed']


def prompt_student_id(current_id: str = None) -> Optional[str]:
    """
    弹出对话框让学生输入学号
    """
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    # 创建对话框
    dialog = tk.Toplevel(root)
    dialog.title("学生身份识别")
    dialog.geometry("400x200")
    dialog.resizable(False, False)
    
    # 居中显示
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
    y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")
    
    # 标签
    if current_id:
        label_text = f"当前学号: {current_id}\n\n请输入新的学号或姓名（留空则使用当前学号）："
    else:
        label_text = "请输入您的学号或姓名："
    
    label = tk.Label(
        dialog,
        text=label_text,
        font=('Arial', 12),
        pady=20,
        justify=tk.LEFT
    )
    label.pack()
    
    # 输入框
    entry = tk.Entry(dialog, font=('Arial', 12), width=30)
    entry.pack(pady=10)
    if current_id:
        entry.insert(0, current_id)
    entry.focus()
    entry.select_range(0, tk.END)
    
    result = {'student_id': None}
    
    def on_ok():
        student_id = entry.get().strip()
        # 如果留空且已有当前学号，使用当前学号
        if not student_id and current_id:
            result['student_id'] = current_id
            dialog.destroy()
        elif student_id:
            result['student_id'] = student_id
            # 保存到文件
            try:
                with open(STUDENT_ID_FILE, 'w', encoding='utf-8') as f:
                    json.dump({'student_id': student_id}, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
            dialog.destroy()
        else:
            messagebox.showwarning("提示", "请输入学号或姓名！")
    
    def on_cancel():
        dialog.destroy()
    
    # 按钮
    button_frame = tk.Frame(dialog)
    button_frame.pack(pady=20)
    
    ok_button = tk.Button(
        button_frame,
        text="确定",
        command=on_ok,
        width=10,
        font=('Arial', 10)
    )
    ok_button.pack(side=tk.LEFT, padx=10)
    
    cancel_button = tk.Button(
        button_frame,
        text="取消",
        command=on_cancel,
        width=10,
        font=('Arial', 10)
    )
    cancel_button.pack(side=tk.LEFT, padx=10)
    
    # 绑定回车键
    entry.bind('<Return>', lambda e: on_ok())
    
    # 等待对话框关闭
    dialog.wait_window()
    root.destroy()
    
    return result['student_id']


def update_student_id(new_student_id: str) -> bool:
    """
    更新学生ID
    """
    try:
        os.makedirs(os.path.dirname(STUDENT_ID_FILE), exist_ok=True)
        with open(STUDENT_ID_FILE, 'w', encoding='utf-8') as f:
            json.dump({'student_id': new_student_id}, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

