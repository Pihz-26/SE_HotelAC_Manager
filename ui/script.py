# occupant_panel.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox, QHBoxLayout
)
from common import post_json
from PyQt5.QtCore import QTimer


def automate_process(self, tasks):
    """
    启动自动化进程。
    :param tasks: 执行任务列表，数组形式，每个任务是一个元组 (时间, 控件, 值)。
    """
    total_clicks = 25  # 点击次数
    interval = 10 * 1000  # 每隔10秒（单位：毫秒）
    elapsed_time = 0  # 已经过的时间

    # ======= 定义周期性点击 get_panel_btn 的任务 =======
    def click_get_panel_btn():
        nonlocal elapsed_time
        if elapsed_time < total_clicks * 10:  # 确保不会超过250秒
            print(f"点击 get_panel_btn 第 {elapsed_time // 10 + 1} 次")
            self.get_panel_btn.click()  # 点击 “获取空调状态按钮”
            elapsed_time += 10
        else:
            panel_timer.stop()  # 停止定时器

    # 创建一个周期性定时器
    panel_timer = QTimer(self)
    panel_timer.timeout.connect(click_get_panel_btn)  # 每次触发点击 get_panel_btn
    panel_timer.start(interval)  # 开始定时器，每10秒触发一次

    # ======= 根据任务列表安排任务 =======
    for task in tasks:
        time, widget, value = task  # 从任务中获取时间、控件、值
        QTimer.singleShot(time * 1000, lambda w=widget, v=value: self.perform_action(w, v))


def perform_action(self, widget, value):
    """
    更新控件的值，并点击设置按钮。
    """
    if isinstance(widget, QLineEdit):
        widget.setText(value)  # 更新文本内容
    elif isinstance(widget, QComboBox):
        widget.setCurrentText(value)  # 设置下拉框的值
    self.set_btn.click()  # 点击设置按钮
    print(f"修改 {widget} 为 {value} 并点击设置按钮")


# ======= 不同按钮对应的任务列表 =======
def get_process1_tasks(self):
    return [
        (0, self.power_combo, "on"),
        (10, self.temp_input, "18"),
        (50, self.wind_combo, "高"),
        (90, self.temp_input, "22"),
        (140, self.power_combo, "off"),
        (180, self.power_combo, "on"),
        (240, self.power_combo, "off"),
    ]


def get_process2_tasks(self):
    return [
        (10, self.power_combo, "on"),
        (30, self.temp_input, "19"),
        (60, self.power_combo, "off"),
        (70, self.power_combo, "on"),
        (110, self.temp_input, "22"),
        (160, self.power_combo, "off"),
        (190, self.power_combo, "on"),
        (250, self.power_combo, "off"),
    ]


def get_process3_tasks(self):
    return [
        (20, self.power_combo, "on"),
        (140, self.temp_input, "24"),
        (140, self.wind_combo, "低"),
        (170, self.wind_combo, "高"),
        (220, self.power_combo, "off"),
    ]


def get_process4_tasks(self):
    return [
        (30, self.power_combo, "on"),
        (90, self.temp_input, "18"),
        (90, self.wind_combo, "高"),  # 同时更新温度和风速
        (180, self.temp_input, "20"),
        (180, self.wind_combo, "中"),
        (250, self.power_combo, "off"),
    ]


def get_process5_tasks(self):
    return [
        (10, self.power_combo, "on"),
        (40, self.temp_input, "22"),
        (70, self.wind_combo, "高"),
        (120, self.wind_combo, "低"),
        (150, self.temp_input, "20"),
        (150, self.wind_combo, "高"),
        (200, self.temp_input, "25"),
        (230, self.power_combo, "off"),
    ]