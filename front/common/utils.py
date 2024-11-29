from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import json
from typing import Dict, Any, Optional

def format_datetime(dt_str: str) -> str:
    """将ISO格式的日期时间字符串转换为更友好的显示格式"""
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return dt_str

def validate_room_id(room_id: str) -> bool:
    """验证房间号格式是否正确"""
    try:
        room = int(room_id)
        floor = room // 100
        number = room % 100
        return 2 <= floor <= 5 and 1 <= number <= 10
    except ValueError:
        return False

def format_currency(amount: float) -> str:
    """格式化货币显示"""
    return f"¥{amount:.2f}"

def show_error(title: str, message: str):
    """显示错误消息对话框"""
    messagebox.showerror(title, message)

def show_info(title: str, message: str):
    """显示信息消息对话框"""
    messagebox.showinfo(title, message)

def show_warning(title: str, message: str):
    """显示警告消息对话框"""
    messagebox.showwarning(title, message)

def center_window(window: tk.Tk):
    """将窗口居中显示"""
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

def create_scrollable_frame(parent: tk.Widget) -> tuple[tk.Frame, tk.Canvas]:
    """创建可滚动的框架"""
    canvas = tk.Canvas(parent)
    scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    return scrollable_frame, canvas

class FormValidator:
    """表单验证工具类"""
    @staticmethod
    def validate_required(value: str, field_name: str) -> tuple[bool, str]:
        """验证必填字段"""
        if not value or not value.strip():
            return False, f"{field_name}不能为空"
        return True, ""

    @staticmethod
    def validate_number(value: str, field_name: str) -> tuple[bool, str]:
        """验证数字字段"""
        try:
            float(value)
            return True, ""
        except ValueError:
            return False, f"{field_name}必须是数字"

    @staticmethod
    def validate_range(value: float, min_val: float, max_val: float, field_name: str) -> tuple[bool, str]:
        """验证数值范围"""
        if value < min_val or value > max_val:
            return False, f"{field_name}必须在{min_val}和{max_val}之间"
        return True, ""

def load_json_file(filepath: str) -> Dict[str, Any]:
    """加载JSON配置文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        show_error("配置加载错误", f"无法加载配置文件: {str(e)}")
        return {}

def save_json_file(filepath: str, data: Dict[str, Any]) -> bool:
    """保存JSON配置文件"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        show_error("配置保存错误", f"无法保存配置文件: {str(e)}")
        return False

class ConfigManager:
    """配置管理器"""
    _instance = None
    _config = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_config(self, filepath: str):
        """加载配置"""
        self._config = load_json_file(filepath)

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self._config.get(key, default)

    def set(self, key: str, value: Any):
        """设置配置值"""
        self._config[key] = value

    def save(self, filepath: str) -> bool:
        """保存配置"""
        return save_json_file(filepath, self._config)