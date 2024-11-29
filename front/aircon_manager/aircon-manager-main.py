import tkinter as tk
from tkinter import ttk, messagebox
from .remote_control import RemoteControlFrame
from .monitor import MonitorFrame
from ..common.config import WINDOW_SIZE
from ..common.utils import center_window

class AirconManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("中央空调管理系统")
        self.geometry(WINDOW_SIZE["ac_manager"])
        center_window(self)
        
        self.setup_ui()
        self.setup_menu()
        
    def setup_ui(self):
        """设置UI布局"""
        # 创建标签页控件
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=5)
        
        # 中央空调控制页面
        self.control_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.control_frame, text="中央空调控制")
        
        # 添加中央空调控制面板
        self.remote_control = RemoteControlFrame(self.control_frame)
        self.remote_control.pack(expand=True, fill="both", padx=10, pady=5)
        
        # 实时监控页面
        self.monitor_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.monitor_frame, text="实时监控")
        
        # 添加监控面板
        self.monitor = MonitorFrame(self.monitor_frame)
        self.monitor.pack(expand=True, fill="both", padx=10, pady=5)

    def setup_menu(self):
        """设置菜单栏"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # 系统菜单
        system_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="系统", menu=system_menu)
        system_menu.add_command(label="退出", command=self.quit)
        
        # 查看菜单
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="查看", menu=view_menu)
        view_menu.add_command(label="刷新监控", command=self.refresh_monitor)
        
        # 设置菜单
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="设置", menu=settings_menu)
        settings_menu.add_command(label="空调参数", command=self.show_settings)
        
    def refresh_monitor(self):
        """刷新监控数据"""
        self.monitor.refresh_data()
        
    def show_settings(self):
        """显示设置对话框"""
        settings_window = tk.Toplevel(self)
        settings_window.title("空调参数设置")
        settings_window.geometry("400x300")
        center_window(settings_window)
        
        # 防止与主窗口交互
        settings_window.grab_set()
        
        # 参数设置界面
        settings_frame = ttk.Frame(settings_window, padding=20)
        settings_frame.pack(fill="both", expand=True)
        
        ttk.Label(settings_frame, text="温度范围设置").pack(anchor="w")
        temp_frame = ttk.Frame(settings_frame)
        temp_frame.pack(fill="x", pady=5)
        
        ttk.Label(temp_frame, text="最低温度:").pack(side="left")
        min_temp = ttk.Spinbox(temp_frame, from_=16, to=24, width=5)
        min_temp.pack(side="left", padx=5)
        
        ttk.Label(temp_frame, text="最高温度:").pack(side="left", padx=10)
        max_temp = ttk.Spinbox(temp_frame, from_=24, to=30, width=5)
        max_temp.pack(side="left", padx=5)
        
        ttk.Label(settings_frame, text="费率设置").pack(anchor="w", pady=(10,5))
        
        rates_frame = ttk.Frame(settings_frame)
        rates_frame.pack(fill="x")
        
        speeds = ["低速", "中速", "高速"]
        default_rates = [0.5, 1.0, 2.0]
        rate_entries = []
        
        for i, (speed, rate) in enumerate(zip(speeds, default_rates)):
            ttk.Label(rates_frame, text=f"{speed}费率:").grid(row=i, column=0, padx=5, pady=5)
            entry = ttk.Entry(rates_frame, width=10)
            entry.insert(0, str(rate))
            entry.grid(row=i, column=1, padx=5, pady=5)
            rate_entries.append(entry)
        
        def save_settings():
            try:
                settings = {
                    "temp_range": {
                        "min": int(min_temp.get()),
                        "max": int(max_temp.get())
                    },
                    "rates": {
                        "low": float(rate_entries[0].get()),
                        "medium": float(rate_entries[1].get()),
                        "high": float(rate_entries[2].get())
                    }
                }
                # 这里可以保存设置
                messagebox.showinfo("成功", "设置已保存")
                settings_window.destroy()
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数值")
        
        ttk.Button(settings_frame, text="保存", command=save_settings).pack(pady=20)

if __name__ == "__main__":
    app = AirconManagerApp()
    app.mainloop()
