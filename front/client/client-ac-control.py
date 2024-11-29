import tkinter as tk
from tkinter import ttk, messagebox
from ..common.api_client import api_client
from ..common.config import AC_CONFIG

class ACControlFrame(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="空调控制")
        self.room_id = None
        self.setup_ui()
        
    def setup_ui(self):
        """设置空调控制界面"""
        # 电源控制
        power_frame = ttk.Frame(self)
        power_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(power_frame, text="电源:").pack(side="left", padx=5)
        self.power_var = tk.StringVar(value="off")
        ttk.Radiobutton(
            power_frame, 
            text="开启",
            variable=self.power_var,
            value="on",
            command=self.update_ac
        ).pack(side="left", padx=5)
        ttk.Radiobutton(
            power_frame,
            text="关闭",
            variable=self.power_var,
            value="off",
            command=self.update_ac
        ).pack(side="left", padx=5)
        
        # 温度控制
        temp_frame = ttk.Frame(self)
        temp_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(temp_frame, text="温度:").pack(side="left", padx=5)
        self.temp_var = tk.StringVar(value=str(AC_CONFIG["default_temp"]))
        self.temp_spinbox = ttk.Spinbox(
            temp_frame,
            from_=AC_CONFIG["temp_range"][0],
            to=AC_CONFIG["temp_range"][1],
            width=5,
            textvariable=self.temp_var,
            command=self.update_ac
        )
        self.temp_spinbox.pack(side="left", padx=5)
        ttk.Label(temp_frame, text="°C").pack(side="left")
        
        # 风速控制
        wind_frame = ttk.Frame(self)
        wind_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(wind_frame, text="风速:").pack(side="left", padx=5)
        self.wind_var = tk.StringVar(value=AC_CONFIG["wind_speeds"][0])
        for speed in AC_CONFIG["wind_speeds"]:
            ttk.Radiobutton(
                wind_frame,
                text=speed,
                variable=self.wind_var,
                value=speed,
                command=self.update_ac
            ).pack(side="left", padx=5)
        
        # 扫风控制
        sweep_frame = ttk.Frame(self)
        sweep_frame.pack(fill="x", padx=5, pady=5)
        
        self.sweep_var = tk.StringVar(value="关")
        ttk.Checkbutton(
            sweep_frame,
            text="扫风",
            variable=self.sweep_var,
            onvalue="开",
            offvalue="关",
            command=self.update_ac
        ).pack(side="left", padx=5)
        
    def set_room_id(self, room_id: str):
        """设置房间号"""
        self.room_id = room_id
        
    def update_ac(self):
        """更新空调设置"""
        if not self.room_id:
            return
            
        try:
            data = {
                "roomId": int(self.room_id),
                "power": self.power_var.get(),
                "temperature": int(self.temp_var.get()),
                "windSpeed": self.wind_var.get(),
                "sweep": self.sweep_var.get()
            }
            
            response = api_client.post("/aircon/control", data)
            
            if response["code"] != 0:
                messagebox.showerror("错误", response["message"])
                
        except Exception as e:
            messagebox.showerror("错误", f"设置失败: {str(e)}")
            
    def set_status(self, status_data: dict):
        """根据状态更新控制界面"""
        if not status_data:
            return
            
        self.power_var.set(status_data.get("power", "off"))
        self.temp_var.set(str(status_data.get("temperature", AC_CONFIG["default_temp"])))
        self.wind_var.set(status_data.get("windSpeed", AC_CONFIG["wind_speeds"][0]))
        self.sweep_var.set(status_data.get("sweep", "关"))
