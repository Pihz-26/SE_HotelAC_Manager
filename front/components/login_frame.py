import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
import json

class LoginFrame(ttk.Frame):
    def __init__(self, parent: tk.Widget, on_login_success: Optional[Callable[[str], None]] = None):
        super().__init__(parent)
        self.parent = parent
        self.on_login_success = on_login_success
        self.setup_ui()

    def setup_ui(self):
        """设置登录界面UI"""
        # 创建样式
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'))
        
        # 标题
        self.title_label = ttk.Label(
            self, text="酒店管理系统登录", 
            style='Title.TLabel'
        )
        self.title_label.pack(pady=20)

        # 登录表单
        self.form_frame = ttk.Frame(self)
        self.form_frame.pack(pady=20)

        # 用户名
        ttk.Label(self.form_frame, text="用户名:").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        self.username_entry = ttk.Entry(self.form_frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        # 密码
        ttk.Label(self.form_frame, text="密码:").grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        self.password_entry = ttk.Entry(self.form_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        # 角色选择
        ttk.Label(self.form_frame, text="角色:").grid(
            row=2, column=0, padx=5, pady=5, sticky="e"
        )
        self.role_var = tk.StringVar(value="前台")
        self.role_combobox = ttk.Combobox(
            self.form_frame, 
            textvariable=self.role_var,
            values=["前台", "空调管理员", "酒店经理"],
            state="readonly"
        )
        self.role_combobox.grid(row=2, column=1, padx=5, pady=5)

        # 登录按钮
        self.login_btn = ttk.Button(
            self, 
            text="登录",
            command=self.handle_login
        )
        self.login_btn.pack(pady=10)

        # 绑定回车键
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())
        self.password_entry.bind('<Return>', lambda e: self.handle_login())

    def handle_login(self):
        """处理登录请求"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_var.get()

        # 输入验证
        if not username or not password:
            messagebox.showerror("错误", "用户名和密码不能为空")
            return

        try:
            # 在实际应用中，这里应该发送请求到后端进行验证
            # 现在我们模拟一个成功的登录
            if username == "admin" and password == "admin":
                if self.on_login_success:
                    self.on_login_success(role)
            else:
                messagebox.showerror("错误", "用户名或密码错误")
        except Exception as e:
            messagebox.showerror("错误", f"登录失败: {str(e)}")

    def clear_form(self):
        """清空表单"""
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.role_var.set("前台")