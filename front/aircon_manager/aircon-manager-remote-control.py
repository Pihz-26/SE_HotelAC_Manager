import tkinter as tk
from tkinter import ttk, messagebox
from ..common.api_client import api_client
from ..common.config import AC_CONFIG

class RemoteControlFrame(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="中央空调控制面板")
        self.setup_ui()
        
    def setup_ui(self):
        """设置控制面板界面"""
        # 工作模式设置
        mode_frame = ttk.LabelFrame(self, text="工作模式")
        mode_frame.pack(fill="x", padx=10, pady=5)
        
        self.mode_var = tk.StringVar(value="制冷")
        ttk.Radiobutton(
            mode_frame,
            text="制冷模式",
            variable=self.mode_var,
            value="制冷"
        ).pack(side="left", padx=20, pady=5)
        
        ttk.Radiobutton(
            mode_frame,
            text="制热模式",
            variable=self.mode_var,
            value="制热"
        ).pack(side="left", padx=20, pady=5)
        
        # 温度范围设置
        temp_frame = ttk.LabelFrame(self, text="温度范围设置")
        temp_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(temp_frame, text="制冷温度范围:").pack(side="left", padx=5)
        self.cool_min = ttk.Spinbox(temp_frame, from_=16, to=24, width=5)
        self.cool_min.pack(side="left", padx=5)
        ttk.Label(temp_frame, text="至").pack(side="left", padx=5)
        self.cool_max = ttk.Spinbox(temp_frame, from_=16, to=24, width=5)
        self.cool_max.pack(side="left", padx=5)
        
        ttk.Label(temp_frame, text="制热温度范围:").pack(side="left", padx=20)
        self.heat_min = ttk.Spinbox(temp_frame, from_=22, to=28, width=5)
        self.heat_min.pack(side="left", padx=5)
        ttk.Label(temp_frame, text="至").pack(side="left", padx=5)
        self.heat_max = ttk.Spinbox(temp_frame, from_=22, to=28, width=5)
        self.heat_max.pack(side="left", padx=5)
        
        # 费率设置
        rate_frame = ttk.LabelFrame(self, text="费率设置")
        rate_frame.pack(fill="x", padx=10, pady=5)
        
        speeds = ["低速", "中速", "高速"]
        self.rate_entries = {}
        
        for i, speed in enumerate(speeds):
            ttk.Label(rate_frame, text=f"{speed}费率:").grid(row=i, column=0, padx=5, pady=5)
            entry = ttk.Entry(rate_frame, width=10)
            entry.grid(row=i, column=1, padx=5, pady=5)
            ttk.Label(rate_frame, text="元/度").grid(row=i, column=2, padx=5, pady=5)
            self.rate_entries[speed] = entry
            
        # 资源调度设置
        resource_frame = ttk.LabelFrame(self, text="资源调度")
        resource_frame.pack(fill="x", padx=10, pady=5)
        
        self.resource_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            resource_frame,
            text="启用资源限制（最多同时服务3个房间）",
            variable=self.resource_var
        ).pack(padx=5, pady=5)
        
        # 控制按钮
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=20)
        
        ttk.Button(
            btn_frame,
            text="开机",
            command=self.start_system
        ).pack(side="left", padx=10)
        
        ttk.Button(
            btn_frame,
            text="关机",
            command=self.stop_system
        ).pack(side="left", padx=10)
        
        ttk.Button(
            btn_frame,
            text="应用设置",
            command=self.apply_settings
        ).pack(side="left", padx=10)
        
    def start_system(self):
        """启动空调系统"""
        try:
            self.apply_settings()
            messagebox.showinfo("成功", "空调系统已启动")
        except Exception as e:
            messagebox.showerror("错误", f"系统启动失败: {str(e)}")
            
    def stop_system(self):
        """关闭空调系统"""
        try:
            response = api_client.post("/central-aircon/adjust", {
                "power": "off"
            })
            if response["code"] == 0:
                messagebox.showinfo("成功", "空调系统已关闭")
            else:
                messagebox.showerror("错误", response["message"])
        except Exception as e:
            messagebox.showerror("错误", f"系统关闭失败: {str(e)}")
            
    def apply_settings(self):
        """应用空调设置"""
        try:
            # 收集设置数据
            settings = {
                "mode": 0 if self.mode_var.get() == "制冷" else 1,
                "resourceLimit": int(self.resource_var.get()),
                "fanRates": {
                    "lowSpeedRate": float(self.rate_entries["低速"].get()),
                    "midSpeedRate": float(self.rate_entries["中速"].get()),
                    "highSpeedRate": float(self.rate_entries["高速"].get())
                }
            }
            
            # 发送设置请求
            response = api_client.post("/central-aircon/adjust", settings)
            
            if response["code"] == 0:
                messagebox.showinfo("成功", "设置已更新")
            else:
                messagebox.showerror("错误", response["message"])
                
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数值")
        except Exception as e:
            messagebox.showerror("错误", f"设置更新失败: {str(e)}")
