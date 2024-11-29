import tkinter as tk
from tkinter import ttk, messagebox
from ..common.api_client import api_client
from ..common.utils import validate_room_id, format_datetime, format_currency

class CheckOutFrame(ttk.Frame):
    def __init__(self, parent, on_check_out=None):
        super().__init__(parent)
        self.on_check_out = on_check_out
        self.setup_ui()
        
    def setup_ui(self):
        """设置退房界面"""
        # 标题
        title_label = ttk.Label(
            self, text="退房结算",
            font=('Helvetica', 14, 'bold')
        )
        title_label.pack(pady=20)
        
        # 查询框架
        query_frame = ttk.Frame(self)
        query_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(query_frame, text="房间号:").pack(side="left", padx=5)
        self.room_entry = ttk.Entry(query_frame, width=10)
        self.room_entry.pack(side="left", padx=5)
        
        ttk.Button(
            query_frame,
            text="查询",
            command=self.query_bill
        ).pack(side="left", padx=5)
        
        # 账单显示区域
        self.bill_frame = ttk.LabelFrame(self, text="账单信息")
        self.bill_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # 基本信息
        self.info_frame = ttk.Frame(self.bill_frame)
        self.info_frame.pack(fill="x", padx=10, pady=5)
        
        self.room_info_label = ttk.Label(self.info_frame, text="房间信息: --")
        self.room_info_label.pack(anchor="w")
        
        self.guest_info_label = ttk.Label(self.info_frame, text="入住人: --")
        self.guest_info_label.pack(anchor="w")
        
        self.time_info_label = ttk.Label(self.info_frame, text="入住时间: --")
        self.time_info_label.pack(anchor="w")
        
        # 费用信息
        self.cost_frame = ttk.Frame(self.bill_frame)
        self.cost_frame.pack(fill="x", padx=10, pady=5)
        
        self.room_cost_label = ttk.Label(self.cost_frame, text="房费: ¥0.00")
        self.room_cost_label.pack(anchor="w")
        
        self.ac_cost_label = ttk.Label(self.cost_frame, text="空调费: ¥0.00")
        self.ac_cost_label.pack(anchor="w")
        
        self.total_cost_label = ttk.Label(
            self.cost_frame,
            text="总计: ¥0.00",
            font=('Helvetica', 12, 'bold')
        )
        self.total_cost_label.pack(anchor="w")
        
        # 详单按钮
        self.detail_btn = ttk.Button(
            self.bill_frame,
            text="查看详单",
            command=self.show_details,
            state="disabled"
        )
        self.detail_btn.pack(pady=10)
        
        # 结算按钮
        self.checkout_btn = ttk.Button(
            self,
            text="办理退房",
            command=self.handle_check_out,
            state="disabled"
        )
        self.checkout_btn.pack(pady=20)
        
    def set_room_id(self, room_id: str):
        """设置房间号并查询"""
        self.room_entry.delete(0, tk.END)
        self.room_entry.insert(0, room_id)
        self.query_bill()
        
    def query_bill(self):
        """查询账单信息"""
        room_i