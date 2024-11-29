import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, Callable
from datetime import datetime

class RoomCard(ttk.Frame):
    """房间信息卡片组件"""
    def __init__(
        self, 
        parent: tk.Widget,
        room_data: Dict[str, Any],
        on_click: Optional[Callable[[Dict[str, Any]], None]] = None,
        show_ac_status: bool = True
    ):
        super().__init__(parent)
        self.room_data = room_data
        self.on_click = on_click
        self.show_ac_status = show_ac_status
        self.setup_styles()
        self.setup_ui()

    def setup_styles(self):
        """设置自定义样式"""
        style = ttk.Style()
        
        # 卡片框架样式
        style.configure(
            'RoomCard.TFrame',
            background='#ffffff',
            relief='raised',
            borderwidth=1
        )
        
        # 房间号样式
        style.configure(
            'RoomNumber.TLabel',
            font=('Helvetica', 12, 'bold'),
            foreground='#333333'
        )
        
        # 状态标签样式
        style.configure(
            'Status.TLabel',
            font=('Helvetica', 9),
            padding=3
        )
        
        # 数值样式
        style.configure(
            'Value.TLabel',
            font=('Helvetica', 10),
            foreground='#666666'
        )

    def setup_ui(self):
        """设置UI布局"""
        self.configure(style='RoomCard.TFrame')
        
        # 主要信息框架
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=8, pady=8)

        # 顶部信息：房间号和状态
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill="x", pady=(0, 5))
        
        room_number = ttk.Label(
            top_frame, 
            text=f"房间 {self.room_data['roomId']}", 
            style='RoomNumber.TLabel'
        )
        room_number.pack(side="left")
        
        # 房间类型标签
        room_type = ttk.Label(
            top_frame,
            text=self.room_data['roomLevel'],
            style='Status.TLabel'
        )
        room_type.pack(side="right")

        # 住客信息
        if self.room_data.get('people'):
            guest_frame = ttk.Frame(main_frame)
            guest_frame.pack(fill="x", pady=2)
            
            ttk.Label(guest_frame, text="住客: ").pack(side="left")
            guests = ", ".join(p["peopleName"] for p in self.room_data["people"])
            ttk.Label(
                guest_frame, 
                text=guests,
                style='Value.TLabel'
            ).pack(side="left")

        # 空调状态信息
        if self.show_ac_status:
            ac_frame = ttk.Frame(main_frame)
            ac_frame.pack(fill="x", pady=5)
            
            # 温度信息
            temp_frame = ttk.Frame(ac_frame)
            temp_frame.pack(side="left")
            
            current_temp = ttk.Label(
                temp_frame,
                text=f"室温: {self.room_data.get('roomTemperature', '--')}°C",
                style='Value.TLabel'
            )
            current_temp.pack(anchor="w")
            
            target_temp = ttk.Label(
                temp_frame,
                text=f"设定: {self.room_data.get('temperature', '--')}°C",
                style='Value.TLabel'
            )
            target_temp.pack(anchor="w")
            
            # 风速和模式
            mode_frame = ttk.Frame(ac_frame)
            mode_frame.pack(side="right")
            
            wind_speed = ttk.Label(
                mode_frame,
                text=f"风速: {self.room_data.get('windSpeed', '--')}",
                style='Value.TLabel'
            )
            wind_speed.pack(anchor="e")
            
            mode = ttk.Label(
                mode_frame,
                text=f"模式: {self.room_data.get('mode', '--')}",
                style='Value.TLabel'
            )
            mode.pack(anchor="e")

        # 底部信息
        if "cost" in self.room_data:
            cost_frame = ttk.Frame(main_frame)
            cost_frame.pack(fill="x", pady=(5, 0))
            
            ttk.Label(
                cost_frame,
                text=f"空调费用: ¥{self.room_data['cost']:.2f}",
                style='Value.TLabel'
            ).pack(side="right")

        # 绑定点击事件
        if self.on_click:
            self.bind("<Button-1>", lambda e: self.on_click(self.room_data))
            for child in self.winfo_children():
                child.bind("<Button-1>", lambda e: self.on_click(self.room_data))

    def update_data(self, new_data: Dict[str, Any]):
        """更新房间数据并刷新显示"""
        self.room_data.update(new_data)
        
        # 清除现有组件
        for widget in self.winfo_children():
            widget.destroy()
            
        # 重新设置UI
        self.setup_ui()