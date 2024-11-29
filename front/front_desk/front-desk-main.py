import tkinter as tk
from tkinter import ttk, messagebox
from .check_in import CheckInFrame
from .check_out import CheckOutFrame
from .records import RecordFrame
from ..common.config import WINDOW_SIZE
from ..common.utils import center_window
from ..components.room_card import RoomCard

class FrontDeskApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("酒店前台管理系统")
        self.geometry(WINDOW_SIZE["front_desk"])
        center_window(self)
        
        self.setup_ui()
        self.start_room_updates()
        
    def setup_ui(self):
        """设置UI布局"""
        # 创建标签页控件
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=5)
        
        # 房态信息页面
        self.status_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.status_frame, text="房态信息")
        
        # 创建房态信息滚动区域
        self.canvas = tk.Canvas(self.status_frame)
        scrollbar = ttk.Scrollbar(self.status_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 入住登记页面
        self.check_in_frame = CheckInFrame(self.notebook, self.refresh_status)
        self.notebook.add(self.check_in_frame, text="入住登记")
        
        # 退房结算页面
        self.check_out_frame = CheckOutFrame(self.notebook, self.refresh_status)
        self.notebook.add(self.check_out_frame, text="退房结算")
        
        # 详单查询页面
        self.record_frame = RecordFrame(self.notebook)
        self.notebook.add(self.record_frame, text="详单查询")
        
    def update_room_status(self):
        """更新房态信息显示"""
        from ..common.api_client import api_client
        
        try:
            response = api_client.get("/stage/query")
            if response["code"] == 0:
                # 清空现有显示
                for widget in self.scrollable_frame.winfo_children():
                    widget.destroy()
                    
                # 添加新的房间卡片
                for room_data in response["data"]:
                    card = RoomCard(
                        self.scrollable_frame,
                        room_data,
                        on_click=self.handle_room_click,
                        show_ac_status=False
                    )
                    card.pack(fill="x", padx=5, pady=2)
                    
        except Exception as e:
            messagebox.showerror("错误", f"获取房态信息失败: {str(e)}")
            
    def handle_room_click(self, room_data):
        """处理房间卡片点击事件"""
        if room_data.get("people"):
            # 如果房间有人，跳转到退房页面
            self.notebook.select(2)  # 切换到退房标签页
            self.check_out_frame.set_room_id(room_data["roomId"])
        else:
            # 如果房间空闲，跳转到入住页面
            self.notebook.select(1)  # 切换到入住标签页
            self.check_in_frame.set_room_id(room_data["roomId"])
            
    def refresh_status(self):
        """刷新房态信息"""
        self.update_room_status()
        
    def start_room_updates(self):
        """开始定时更新房态信息"""
        self.update_room_status()
        self.after(5000, self.start_room_updates)

if __name__ == "__main__":
    app = FrontDeskApp()
    app.mainloop()
