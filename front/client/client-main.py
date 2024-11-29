import tkinter as tk
from tkinter import ttk, messagebox
from .ac_control import ACControlFrame
from .ac_status import ACStatusFrame
from ..common.config import WINDOW_SIZE
from ..common.utils import center_window, validate_room_id

class ClientApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("空调客户端")
        self.geometry(WINDOW_SIZE["client"])
        center_window(self)
        
        self.room_id = None
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI布局"""
        # 房间信息框架
        self.room_frame = ttk.LabelFrame(self, text="房间信息")
        self.room_frame.pack(padx=10, pady=5, fill="x")
        
        # 房间号输入
        self.room_entry_frame = ttk.Frame(self.room_frame)
        self.room_entry_frame.pack(padx=5, pady=5, fill="x")
        
        ttk.Label(self.room_entry_frame, text="房间号:").pack(side="left", padx=5)
        self.room_entry = ttk.Entry(self.room_entry_frame, width=10)
        self.room_entry.pack(side="left", padx=5)
        
        self.confirm_btn = ttk.Button(
            self.room_entry_frame,
            text="确认",
            command=self.confirm_room
        )
        self.confirm_btn.pack(side="left", padx=5)
        
        # 空调控制和状态显示区域
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(expand=True, fill="both", padx=10, pady=5)
        
        # 创建但先不显示空调控制和状态组件
        self.ac_control = ACControlFrame(self.content_frame)
        self.ac_status = ACStatusFrame(self.content_frame)
        
    def confirm_room(self):
        """确认房间号并初始化界面"""
        room_id = self.room_entry.get().strip()
        
        if not validate_room_id(room_id):
            messagebox.showerror("错误", "请输入有效的房间号")
            return
            
        self.room_id = room_id
        self.room_entry.configure(state="disabled")
        self.confirm_btn.configure(state="disabled")
        
        # 显示空调控制和状态组件
        self.ac_control.set_room_id(room_id)
        self.ac_control.pack(side="left", fill="both", expand=True, padx=5)
        
        self.ac_status.set_room_id(room_id)
        self.ac_status.pack(side="right", fill="both", expand=True, padx=5)
        
        # 开始定时更新状态
        self.ac_status.start_updates()

if __name__ == "__main__":
    app = ClientApp()
    app.mainloop()
