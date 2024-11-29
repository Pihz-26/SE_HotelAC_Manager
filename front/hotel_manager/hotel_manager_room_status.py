import tkinter as tk
from tkinter import ttk, messagebox

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from front.common.api_client import api_client
from front.common.utils import format_datetime, format_currency
from front.components.room_card import RoomCard
import json

class RoomStatusFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        self.start_updates()
        
    def setup_ui(self):
        """设置UI布局"""
        # 控制面板
        control_frame = ttk.Frame(self)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        # 楼层筛选
        ttk.Label(control_frame, text="楼层:").pack(side="left", padx=5)
        self.floor_var = tk.StringVar(value="全部")
        floor_cb = ttk.Combobox(
            control_frame,
            textvariable=self.floor_var,
            values=["全部", "2层", "3层", "4层", "5层"],
            state="readonly",
            width=10
        )
        floor_cb.pack(side="left", padx=5)
        
        # 房型筛选
        ttk.Label(control_frame, text="房型:").pack(side="left", padx=5)
        self.type_var = tk.StringVar(value="全部")
        type_cb = ttk.Combobox(
            control_frame,
            textvariable=self.type_var,
            values=["全部", "标准间", "大床房"],
            state="readonly",
            width=10
        )
        type_cb.pack(side="left", padx=5)
        
        # 状态筛选
        ttk.Label(control_frame, text="状态:").pack(side="left", padx=5)
        self.status_var = tk.StringVar(value="全部")
        status_cb = ttk.Combobox(
            control_frame,
            textvariable=self.status_var,
            values=["全部", "空闲", "已入住"],
            state="readonly",
            width=10
        )
        status_cb.pack(side="left", padx=5)
        
        # 刷新按钮
        ttk.Button(
            control_frame,
            text="刷新",
            command=self.refresh_status
        ).pack(side="right", padx=5)
        
        # 创建滚动区域
        self.canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True, padx=(10,0), pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)
        
        # 绑定筛选器更改事件
        self.floor_var.trace("w", lambda *args: self.refresh_status())
        self.type_var.trace("w", lambda *args: self.refresh_status())
        self.status_var.trace("w", lambda *args: self.refresh_status())
        
    def filter_rooms(self, rooms):
        """根据筛选条件过滤房间"""
        filtered = []
        for room in rooms:
            # 楼层筛选
            if self.floor_var.get() != "全部":
                floor = int(self.floor_var.get()[0])
                if floor != room["roomId"] // 1000:
                    continue
                    
            # 房型筛选
            if self.type_var.get() != "全部" and self.type_var.get() != room["roomLevel"]:
                continue
                
            # 状态筛选
            room_status = "已入住" if room.get("people") else "空闲"
            if self.status_var.get() != "全部" and self.status_var.get() != room_status:
                continue
                
            filtered.append(room)
            
        return filtered
        
    def refresh_status(self):
        """刷新房态信息"""
        try:
            # 获取房态数据
            response = api_client.get("/admin/query_room")
            if response["code"] != 0:
                raise Exception(response["message"])
                
            # 清除现有显示
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
                
            # 过滤并显示房间卡片
            filtered_rooms = self.filter_rooms(response["data"])
            for room in filtered_rooms:
                card = RoomCard(
                    self.scrollable_frame,
                    room,
                    on_click=self.show_room_details,
                    show_ac_status=True
                )
                card.pack(fill="x", padx=5, pady=2)
                
        except Exception as e:
            messagebox.showerror("错误", f"获取房态信息失败: {str(e)}")
            
    def show_room_details(self, room_data):
        """显示房间详细信息"""
        details_window = tk.Toplevel(self)
        details_window.title(f"房间 {room_data['roomId']} 详细信息")
        details_window.geometry("400x600")
        
        # 基本信息
        info_frame = ttk.LabelFrame(details_window, text="基本信息")
        info_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(info_frame, text=f"房型: {room_data['roomLevel']}").pack(anchor="w", padx=5, pady=2)
        ttk.Label(info_frame, text=f"状态: {'已入住' if room_data.get('people') else '空闲'}").pack(anchor="w", padx=5, pady=2)
        
        if room_data.get("people"):
            people_info = "\n".join(f"- {p['peopleName']}" for p in room_data["people"])
            ttk.Label(info_frame, text=f"入住人:\n{people_info}").pack(anchor="w", padx=5, pady=2)
        
        # 空调信息
        ac_frame = ttk.LabelFrame(details_window, text="空调信息")
        ac_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(ac_frame, text=f"当前温度: {room_data['roomTemperature']}°C").pack(anchor="w", padx=5, pady=2)
        ttk.Label(ac_frame, text=f"设定温度: {room_data['temperature']}°C").pack(anchor="w", padx=5, pady=2)
        ttk.Label(ac_frame, text=f"风速: {room_data['windSpeed']}").pack(anchor="w", padx=5, pady=2)
        ttk.Label(ac_frame, text=f"模式: {room_data['mode']}").pack(anchor="w", padx=5, pady=2)
        ttk.Label(ac_frame, text=f"扫风: {room_data['sweep']}").pack(anchor="w", padx=5, pady=2)

