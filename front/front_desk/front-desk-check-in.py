import tkinter as tk
from tkinter import ttk, messagebox
from ..common.api_client import api_client
from ..common.utils import validate_room_id

class CheckInFrame(ttk.Frame):
    def __init__(self, parent, on_check_in=None):
        super().__init__(parent)
        self.on_check_in = on_check_in
        self.setup_ui()
        
    def setup_ui(self):
        """设置入住登记界面"""
        # 标题
        title_label = ttk.Label(
            self, text="入住登记",
            font=('Helvetica', 14, 'bold')
        )
        title_label.pack(pady=20)
        
        # 表单框架
        form_frame = ttk.Frame(self)
        form_frame.pack(padx=20, pady=10)
        
        # 房间号
        ttk.Label(form_frame, text="房间号:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.room_entry = ttk.Entry(form_frame)
        self.room_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # 顾客姓名
        ttk.Label(form_frame, text="顾客姓名:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.name_entry = ttk.Entry(form_frame)
        self.name_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # 身份证号
        ttk.Label(form_frame, text="身份证号:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.id_entry = ttk.Entry(form_frame)
        self.id_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # 入住天数
        ttk.Label(form_frame, text="入住天数:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.days_spinbox = ttk.Spinbox(form_frame, from_=1, to=30, width=5)
        self.days_spinbox.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        # 押金
        ttk.Label(form_frame, text="押金:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.deposit_label = ttk.Label(form_frame, text="¥0.00")
        self.deposit_label.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        
        # 计算押金按钮
        self.calc_btn = ttk.Button(
            form_frame,
            text="计算押金",
            command=self.calculate_deposit
        )
        self.calc_btn.grid(row=5, column=0, columnspan=2, pady=10)
        
        # 提交按钮
        self.submit_btn = ttk.Button(
            form_frame,
            text="办理入住",
            command=self.handle_check_in
        )
        self.submit_btn.grid(row=6, column=0, columnspan=2, pady=10)
        
    def set_room_id(self, room_id: str):
        """设置房间号"""
        self.room_entry.delete(0, tk.END)
        self.room_entry.insert(0, room_id)
        
    def calculate_deposit(self):
        """计算押金"""
        try:
            days = int(self.days_spinbox.get())
            # 假设每天押金100元
            deposit = days * 100
            self.deposit_label.config(text=f"¥{deposit:.2f}")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的入住天数")
            
    def handle_check_in(self):
        """处理入住登记"""
        # 获取输入
        room_id = self.room_entry.get().strip()
        name = self.name_entry.get().strip()
        id_number = self.id_entry.get().strip()
        
        # 验证输入
        if not all([room_id, name, id_number]):
            messagebox.showerror("错误", "请填写所有必填项")
            return
            
        if not validate_room_id(room_id):
            messagebox.showerror("错误", "请输入有效的房间号")
            return
            
        try:
            # 发送入住请求
            data = {
                "roomId": int(room_id),
                "peopleName": name
            }
            
            response = api_client.post("/stage/add", data)
            
            if response["code"] == 0:
                messagebox.showinfo("成功", "入住登记成功")
                self.clear_form()
                if self.on_check_in:
                    self.on_check_in()
            else:
                messagebox.showerror("错误", response["message"])
                
        except Exception as e:
            messagebox.showerror("错误", f"入住登记失败: {str(e)}")
            
    def clear_form(self):
        """清空表单"""
        self.room_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.id_entry.delete(0, tk.END)
        self.days_spinbox.delete(0, tk.END)
        self.days_spinbox.insert(0, "1")
        self.deposit_label.config(text="¥0.00")
