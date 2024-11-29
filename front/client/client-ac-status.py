import tkinter as tk
from tkinter import ttk
from ..common.api_client import api_client
from ..common.utils import format_currency

class ACStatusFrame(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="空调状态")
        self.room_id = None
        self.update_job = None
        self.setup_ui()
        
    def setup_ui(self):
        """设置状态显示界面"""
        # 当前温度显示
        temp_frame = ttk.Frame(self)
        temp_frame.pack(fill="x", padx=5, pady=5)
        
        self.room_temp_label = ttk.Label(
            temp_frame,
            text="室温: --℃",
            font=('Helvetica', 14)
        )
        self.room_temp_label.pack()
        
        # 运行状态显示
        status_frame = ttk.Frame(self)
        status_frame.pack(fill="x", padx=5, pady=5)
        
        self.mode_label = ttk.Label(status_frame, text="模式: --")
        self.mode_label.pack(pady=2)
        
        self.wind_label = ttk.Label(status_frame, text="风速: --")
        self.wind_label.pack(pady=2)
        
        self.sweep_label = ttk.Label(status_frame, text="扫风: --")
        self.sweep_label.pack(pady=2)
        
        # 费用信息显示
        cost_frame = ttk.Frame(self)
        cost_frame.pack(fill="x", padx=5, pady=5)
        
        self.current_cost_label = ttk.Label(
            cost_frame,
            text="当前费用: --",
            font=('Helvetica', 12)
        )
        self.current_cost_label.pack(pady=2)
        
        self.total_cost_label = ttk.Label(
            cost_frame,
            text="总费用: --",
            font=('Helvetica', 12)
        )
        self.total_cost_label.pack(pady=2)
        
    def set_room_id(self, room_id: str):
        """设置房间号并初始化显示"""
        self.room_id = room_id
        self.update_status()
        
    def update_status(self):
        """更新状态显示"""
        if not self.room_id:
            return
            
        try:
            response = api_client.get("/aircon/panel", {"roomId": int(self.room_id)})
            
            if response["code"] == 0:
                data = response["data"]
                
                # 更新温度显示
                self.room_temp_label.config(
                    text=f"室温: {data['roomTemperature']}℃"
                )
                
                # 更新状态显示
                self.mode_label.config(text=f"模式: {data['mode']}")
                self.wind_label.config(text=f"风速: {data['windSpeed']}")
                self.sweep_label.config(text=f"扫风: {data['sweep']}")
                
                # 更新费用显示
                self.current_cost_label.config(
                    text=f"当前费用: {format_currency(data['cost'])}"
                )
                self.total_cost_label.config(
                    text=f"总费用: {format_currency(data['totalCost'])}"
                )
                
        except Exception:
            pass
            
    def start_updates(self):
        """开始定时更新"""
        if self.update_job:
            self.after_cancel(self.update_job)
            
        def update():
            self.update_status()
            self.update_job = self.after(1000, update)
            
        update()
        
    def stop_updates(self):
        """停止定时更新"""
        if self.update_job:
            self.after_cancel(self.update_job)
            self.update_job = None
            
    def destroy(self):
        """清理资源"""
        self.stop_updates()
        super().destroy()
