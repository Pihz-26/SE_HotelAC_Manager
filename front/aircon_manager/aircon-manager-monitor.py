import tkinter as tk
from tkinter import ttk
from ..common.api_client import api_client
from ..common.utils import format_currency

class RoomMonitorCard(ttk.Frame):
    """单个房间监控卡片"""
    def __init__(self, parent, room_data):
        super().__init__(parent)
        self.room_data = room_data
        self.setup_ui()
        
    def setup_ui(self):
        """设置卡片UI"""
        # 房间号和状态
        header = ttk.Frame(self)
        header.pack(fill="x", padx=5, pady=2)
        
        ttk.Label(
            header,
            text=f"房间 {self.room_data['roomId']}",
            font=('Helvetica', 10, 'bold')
        ).pack(side="left")
        
        status = "运行中" if self.room_data["power"] == "on" else "关闭"
        ttk.Label(
            header,
            text=status,
            foreground="green" if status == "运行中" else "red"
        ).pack(side="right")
        
        # 温度信息
        temp_frame = ttk.Frame(self)
        temp_frame.pack(fill="x", padx=5)
        
        ttk.Label(
            temp_frame,
            text=f"室温: {self.room_data['roomTemperature']}°C"
        ).pack(side="left")
        
        ttk.Label(
            temp_frame,
            text=f"设定: {self.room_data['temperature']}°C"
        ).pack(side="right")
        
        # 运行参数
        param_frame = ttk.Frame(self)
        param_frame.pack(fill="x", padx=5)
        
        ttk.Label(
            param_frame,
            text=f"模式: {self.room