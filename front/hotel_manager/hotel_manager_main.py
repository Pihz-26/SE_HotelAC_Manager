import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

# 修改导入为绝对路径
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


from common.config import WINDOW_SIZE
from common.utils import center_window
from common.api_client import api_client
from hotel_manager_room_status import RoomStatusFrame


class HotelManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("酒店管理系统")
        self.geometry(WINDOW_SIZE["hotel_manager"])
        center_window(self)
        
        self.setup_ui()
        self.start_updates()
        
    def setup_ui(self):
        """设置UI布局"""
        # 创建标签页控件
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=5)
        
        # 房态监控页面
        self.room_status_frame = RoomStatusFrame(self.notebook)
        self.notebook.add(self.room_status_frame, text="房态监控")
        
        # 数据统计页面
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="数据统计")
        
        # 创建统计图表区域
        self.create_stats_view()
        
    def create_stats_view(self):
        """创建统计视图"""
        # 时间范围选择
        control_frame = ttk.Frame(self.stats_frame)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(control_frame, text="统计范围:").pack(side="left", padx=5)
        self.range_var = tk.StringVar(value="day")
        ttk.Radiobutton(
            control_frame,
            text="日报",
            variable=self.range_var,
            value="day",
            command=self.update_stats
        ).pack(side="left", padx=10)
        ttk.Radiobutton(
            control_frame,
            text="周报",
            variable=self.range_var,
            value="week",
            command=self.update_stats
        ).pack(side="left", padx=10)
        
        # 图表框架
        self.charts_frame = ttk.Frame(self.stats_frame)
        self.charts_frame.pack(expand=True, fill="both", padx=10, pady=5)
        
    def update_stats(self):
        """更新统计数据和图表"""
        try:
            # 获取空调使用记录
            response_ac = api_client.get("/admin/query_ac")
            if response_ac["code"] != 0:
                raise Exception(response_ac["message"])
                
            # 获取客流记录
            response_people = api_client.get("/admin/query_people")
            if response_people["code"] != 0:
                raise Exception(response_people["message"])
                
            # 清除现有图表
            for widget in self.charts_frame.winfo_children():
                widget.destroy()
                
            # 创建新图表
            self.create_ac_usage_chart(response_ac["data"])
            self.create_guest_flow_chart(response_people["data"])
            
        except Exception as e:
            messagebox.showerror("错误", f"获取统计数据失败: {str(e)}")
            
    def create_ac_usage_chart(self, data):
        """创建空调使用统计图表"""
        # 创建图形
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        
        # 统计每个房间的空调使用时长和费用
        room_stats = {}
        for record in data:
            room_id = record["roomId"]
            if room_id not in room_stats:
                room_stats[room_id] = {"duration": 0, "cost": 0}
            room_stats[room_id]["duration"] += record["timeSlice"]
            room_stats[room_id]["cost"] += record["cost"]
        
        # 绘制使用时长柱状图
        rooms = list(room_stats.keys())
        durations = [stats["duration"] for stats in room_stats.values()]
        ax1.bar(rooms, durations)
        ax1.set_title("空调使用时长统计")
        ax1.set_xlabel("房间号")
        ax1.set_ylabel("使用时长(分钟)")
        
        # 绘制费用饼图
        costs = [stats["cost"] for stats in room_stats.values()]
        ax2.pie(costs, labels=rooms, autopct='%1.1f%%')
        ax2.set_title("空调费用分布")
        
        # 创建画布并显示
        canvas = FigureCanvasTkAgg(fig, self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        
    def create_guest_flow_chart(self, data):
        """创建客流统计图表"""
        # 创建图形
        fig, ax = plt.subplots(figsize=(12, 4))
        
        # 按时间统计入住和退房人数
        flow_stats = {}
        for record in data:
            date = datetime.fromisoformat(record["time"]).date()
            if date not in flow_stats:
                flow_stats[date] = {"checkin": 0, "checkout": 0}
            if record["operation"] == "入住":
                flow_stats[date]["checkin"] += 1
            else:
                flow_stats[date]["checkout"] += 1
        
        # 绘制折线图
        dates = sorted(flow_stats.keys())
        checkins = [flow_stats[date]["checkin"] for date in dates]
        checkouts = [flow_stats[date]["checkout"] for date in dates]
        
        ax.plot(dates, checkins, label="入住人数", marker="o")
        ax.plot(dates, checkouts, label="退房人数", marker="s")
        ax.set_title("客流量趋势")
        ax.set_xlabel("日期")
        ax.set_ylabel("人数")
        ax.legend()
        
        # 创建画布并显示
        canvas = FigureCanvasTkAgg(fig, self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        
    def start_updates(self):
        """开始定时更新"""
        self.update_stats()
        self.after(300000, self.start_updates)  # 每5分钟更新一次

if __name__ == "__main__":
    # 确保正确运行脚本
    app = HotelManagerApp()
    app.mainloop()
