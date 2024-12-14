# occupant_panel.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox, QHBoxLayout
)
from common import post_json, get_json
from urllib.parse import urlencode
from PyQt5.QtCore import QTimer

class OccupantPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("住户空调控制面板 (Occupant AC Control)")
        self.setGeometry(250, 100, 1400, 850)
        # 背景层
        self.background_widget = QLabel(self)
        self.background_widget.setGeometry(0, 0, 1400, 850)
        self.background_widget.setStyleSheet("border-image: url('image/顾客界面.png');")

        # 控件层
        self.widget_layer = QWidget(self)
        self.widget_layer.setGeometry(0, 0, 1400, 850)
        self.init_ui()
        self.init_ui()

    def init_ui(self):
        # 输入房间号标签及输入框
        self.room_label = QLabel("房间号：", self)  # 房间号标签
        self.room_label.setGeometry(230, 145, 400, 60)  # (x, y, width, height)
        self.room_label.setStyleSheet("font-size: 40px; color: black;border-image:none")

        self.room_input = QLineEdit(self)  # 房间号输入框
        self.room_input.setGeometry(380, 145, 150, 60)
        self.room_input.setStyleSheet("""  
                                QLineEdit {  
                                    border: 2px solid gray;  
                                    border-radius: 10px;   
                                    padding: 5px;  
                                    background-color: #f9f9f9;  
                                    font-size: 25px; 
                                    border-image:none 
                                }  
                                QLineEdit:focus {  
                                    border: 2px solid #4682B4; 
                                    border-image:none 
                                }  
                            """)

        # 获取空调状态按钮
        self.get_panel_btn = QPushButton("获取空调状态", self)
        self.get_panel_btn.setGeometry(320, 710, 240, 60)
        self.get_panel_btn.clicked.connect(self.get_panel_info)
        self.get_panel_btn.setStyleSheet(
            "font-size: 35px; color: black;"
            "border: 2px solid black; border-radius: 10px;"
            "background-color: white;"
            "border-image: none;"
            "transition: background-color 0.3s;"  # 使过渡更平滑(optional)  
            "}"
            "QPushButton:hover {"
            "background-color: pink;"  # 鼠标悬停时背景变为粉色  
            "}"
        )


        # 电源组合框
        self.power_label = QLabel("电源(on/off):", self)
        self.power_label.setGeometry(185, 270, 200, 30)
        self.power_label.setStyleSheet("font-size: 30px; color: black;border-image:none")

        self.power_combo = QComboBox(self)
        self.power_combo.setGeometry(400, 260, 130, 50)
        self.power_combo.addItems(["on", "off"])
        self.power_combo.setStyleSheet("""  
                                QComboBox {  
                                    font-size: 32px;  
                                    border: 2px solid gray;  
                                    border-radius: 8px;  
                                    padding: 5px;  
                                    background-color: #ebd1df;  
                                    border-image:none
                                }  
                                QComboBox QAbstractItemView {  
                                    font-size: 25px;  
                                    border-image:none
                                }  
                            """)

        # 目标温度输入框
        self.temp_label = QLabel("目标温度(℃):", self)
        self.temp_label.setGeometry(185,380, 200, 30)
        self.temp_label.setStyleSheet("font-size: 30px; color: black;border-image:none")


        self.temp_input = QLineEdit("25", self)
        self.temp_input.setGeometry(400, 370, 100, 50)
        self.temp_input.setStyleSheet("font-size: 40px;background-color: #ebd1df; color: black;border-image:none")

        # 风速组合框
        self.wind_label = QLabel("风速低/中/高:", self)
        self.wind_label.setGeometry(185, 500, 200, 30)
        self.wind_label.setStyleSheet("font-size: 30px; color: black;border-image:none")

        self.wind_combo = QComboBox(self)
        self.wind_combo.setGeometry(400, 490, 130, 50)
        self.wind_combo.addItems(["低", "中", "高"])
        self.wind_combo.setCurrentText("中")
        self.wind_combo.setStyleSheet("""  
                                        QComboBox {  
                                            font-size: 32px;  
                                            border: 2px solid gray;  
                                            border-radius: 8px;  
                                            padding: 5px;  
                                            background-color: #ebd1df;  
                                            border-image:none
                                        }  
                                        QComboBox QAbstractItemView {  
                                            font-size: 25px;  
                                            border-image:none
                                        }  
                                    """)

        # 扫风组合框
        self.sweep_label = QLabel("扫风(开/关):", self)
        self.sweep_label.setGeometry(195, 615, 200, 30)
        self.sweep_label.setStyleSheet("font-size: 30px; color: black;border-image:none")

        self.sweep_combo = QComboBox(self)
        self.sweep_combo.setGeometry(400, 605, 130, 50)
        self.sweep_combo.addItems(["开", "关"])
        self.sweep_combo.setStyleSheet("""  
                                                QComboBox {  
                                                    font-size: 32px;  
                                                    border: 2px solid gray;  
                                                    border-radius: 8px;  
                                                    padding: 5px;  
                                                    background-color: #ebd1df;  
                                                    border-image:none
                                                }  
                                                QComboBox QAbstractItemView {  
                                                    font-size: 25px;  
                                                    border-image:none
                                                }  
                                            """)

        # 设置空调按钮
        self.set_btn = QPushButton("设置空调", self)
        self.set_btn.setGeometry(90, 710, 180, 60)
        self.set_btn.clicked.connect(self.set_ac_control)
        self.set_btn.setStyleSheet(
            "font-size: 35px; color: black;"
            "border: 2px solid black; border-radius: 10px;"
            "background-color: white;"
            "border-image: none;"
            "transition: background-color 0.3s;"  # 使过渡更平滑(optional)  
            "}"
            "QPushButton:hover {"
            "background-color: pink;"  # 鼠标悬停时背景变为粉色  
            "}"
        )
        
        # 进程显示按钮 1
        self.process1_btn = QPushButton("1", self)
        self.process1_btn.setGeometry(720, 700, 90, 90)
        self.process1_btn.clicked.connect(lambda: self.automate_process(self.get_process1_tasks()))
        self.process1_btn.setStyleSheet(
            "font-size: 80px; color: black;"
            "border: 2px solid black; border-radius: 10px;"
            "background-color: #4989c2;"
            "border-image: none;"
            "transition: background-color 0.3s;"  # 使过渡更平滑(optional)  
            "}"
            "QPushButton:hover {"
            "background-color: pink;"  # 鼠标悬停时背景变为粉色  
            "}"
        )
        # 进程显示按钮 2
        self.process2_btn = QPushButton("2", self)
        self.process2_btn.setGeometry(845, 700, 90, 90)
        self.process2_btn.clicked.connect(lambda: self.automate_process(self.get_process2_tasks()))
        self.process2_btn.setStyleSheet(
            "font-size: 80px; color: black;"
            "border: 2px solid black; border-radius: 10px;"
            "background-color: #74abdd;"
            "border-image: none;"
            "transition: background-color 0.3s;"  # 使过渡更平滑(optional)  
            "}"
            "QPushButton:hover {"
            "background-color: pink;"  # 鼠标悬停时背景变为粉色  
            "}"
        )
        
        # 进程显示按钮 3
        self.process3_btn = QPushButton("3", self)
        self.process3_btn.setGeometry(965, 700, 90, 90)
        self.process3_btn.clicked.connect(lambda: self.automate_process(self.get_process3_tasks()))
        self.process3_btn.setStyleSheet(
            "font-size: 80px; color: black;"
            "border: 2px solid black; border-radius: 10px;"
            "background-color: #e7d4df;"
            "border-image: none;"
            "transition: background-color 0.3s;"  # 使过渡更平滑(optional)  
            "}"
            "QPushButton:hover {"
            "background-color: pink;"  # 鼠标悬停时背景变为粉色  
            "}"
        )
        # 进程显示按钮 4
        self.process4_btn = QPushButton("4", self)
        self.process4_btn.setGeometry(1085, 700, 90, 90)
        self.process4_btn.clicked.connect(lambda: self.automate_process(self.get_process4_tasks()))
        self.process4_btn.setStyleSheet(
            "font-size: 80px; color: black;"
            "border: 2px solid black; border-radius: 10px;"
            "background-color: #ffd0eb;"
            "border-image: none;"
            "transition: background-color 0.3s;"  # 使过渡更平滑(optional)  
            "}"
            "QPushButton:hover {"
            "background-color: pink;"  # 鼠标悬停时背景变为粉色  
            "}"
        )
        
        # 进程显示按钮 5
        self.process5_btn = QPushButton("5", self)
        self.process5_btn.setGeometry(1205, 700, 90, 90)
        self.process5_btn.clicked.connect(lambda: self.automate_process(self.get_process5_tasks()))
        self.process5_btn.setStyleSheet(
            "font-size: 80px; color: black;"
            "border: 2px solid black; border-radius: 10px;"
            "background-color: #f6b1d9;"
            "border-image: none;"
            "transition: background-color 0.3s;"  # 使过渡更平滑(optional)  
            "}"
            "QPushButton:hover {"
            "background-color: pink;"  # 鼠标悬停时背景变为粉色  
            "}"
        )
        
        # 空调界面温度显示
        self.room_temperature_label = QLabel(f"", self)
        self.room_temperature_label.setGeometry(750, 200, 250, 180)
        self.room_temperature_label.setStyleSheet("font-size: 100px; color: black;border-image:none")
        
        self.power_label = QLabel(f"", self)
        self.power_label.setGeometry(882, 387, 250, 50)
        self.power_label.setStyleSheet("font-size: 50px; color: black;border-image:none")
        
        self.wind_speed_label = QLabel(f"", self)
        self.wind_speed_label.setGeometry(1120, 140, 220, 60)
        self.wind_speed_label.setStyleSheet("font-size: 45px;border: 2px solid black; border-radius: 10px; color: black;border-image:none")

        self.mode_label = QLabel("", self)
        self.mode_label.setGeometry(1120, 260, 220, 60)
        self.mode_label.setStyleSheet("font-size: 45px;border: 2px solid black; border-radius: 10px; color: black;border-image:none")

        self.sweep_label = QLabel("", self)
        self.sweep_label.setGeometry(1120, 380, 220, 60)
        self.sweep_label.setStyleSheet("font-size: 45px; border: 2px solid black; border-radius: 10px; color: black;border-image:none")

        self.cost_label = QLabel("", self)
        self.cost_label.setGeometry(720, 540,400, 50)
        self.cost_label.setStyleSheet("font-size: 50px; color: black;border-image:none")
        
        self.total_cost_label = QLabel("", self)
        self.total_cost_label.setGeometry(720, 620,400, 50)
        self.total_cost_label.setStyleSheet("font-size: 50px; color: black;border-image:none")
        
    def get_panel_info(self):
        room_id = self.room_input.text().strip()
        if not room_id.isdigit():
            QMessageBox.critical(self, "错误", "请正确输入房间号（数字）")
            return
        from urllib.parse import urlencode

        data = {"roomId": int(room_id)}
        url = f"/aircon/panel?{urlencode(data)}"
        res = get_json(url)
        if res and res.status_code == 200:
            try:
                d = res.json()
                
                if d.get("code") == 0:  # 使用 get 方法更安全，避免键不存在时抛出异常
                    panel = d.get("data", {})
                    info = (
                        f"房间温度: {panel.get('roomTemperature', 'N/A')}°C | 电源: {panel.get('power', 'N/A')} | "
                        f"目标温度: {panel.get('temperature', 'N/A')}°C | 风速: {panel.get('windSpeed', 'N/A')} | "
                        f"模式: {panel.get('mode', 'N/A')} | 扫风: {panel.get('sweep', 'N/A')} | "
                        f"当前费用: {panel.get('cost', 'N/A')}元 | 累计费用: {panel.get('totalCost', 'N/A')}元"
                    )
                    self.room_temperature_label.clear()
                    self.room_temperature_label.setText(f"{panel.get('roomTemperature', '--')}")
                    self.room_temperature_label.repaint()
                    
                    self.power_label.clear()
                    self.power_label.setText(f"{panel.get('power', 'N/A')}")
                    self.power_label.repaint()
                    
                    self.wind_speed_label.clear()
                    self.wind_speed_label.setText(f"风速：{panel.get('windSpeed', 'N/A')}")
                    self.wind_speed_label.repaint()
                    
                    self.mode_label.clear()
                    self.mode_label.setText(f"模式:{panel.get('mode', 'N/A')}")
                    self.mode_label.repaint()
                    
                    self.sweep_label.clear()
                    self.sweep_label.setText(f"扫风:{panel.get('sweep', 'N/A')}")
                    self.sweep_label.repaint()
                    
                    self.cost_label.clear()
                    self.cost_label.setText(f"当前费用：{panel.get('cost', 'N/A')}元")
                    self.cost_label.repaint()
                    
                    self.total_cost_label.clear()
                    self.total_cost_label.setText(f"总费用：{panel.get('totalCost', 'N/A')}元")
                    self.total_cost_label.repaint()
                    
                else:
                    QMessageBox.critical(self, "错误", d.get("message", "查询失败"))
            except (ValueError, KeyError) as e:
                QMessageBox.critical(self, "错误", f"响应解析失败: {e}")
        else:
            QMessageBox.critical(self, "错误", f"查询失败: {res.status_code if res else '无响应'}")

    def set_ac_control(self):
        room_id = self.room_input.text().strip()
        if not room_id.isdigit():
            QMessageBox.critical(self, "错误", "请正确输入房间号")
            return
        try:
            temperature = int(self.temp_input.text().strip())
        except ValueError:
            QMessageBox.critical(self, "错误", "请正确输入目标温度（数字）")
            return
        data = {
            "roomId": int(room_id),
            "power": self.power_combo.currentText(),
            "temperature": temperature,
            "windSpeed": self.wind_combo.currentText(),
            "sweep": self.sweep_combo.currentText()
        }
        res = post_json("/aircon/control", data)
        if res and res.status_code == 200:
            d = res.json()
            if d["code"] == 0:

                self.get_panel_info()  # 刷新状态
            else:
                QMessageBox.critical(self, "错误", d.get("message", "设置失败"))
        else:
            QMessageBox.critical(self, "错误", f"设置失败: {res.status_code if res else '无响应'}")
        
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
        # return [
        #     (0, self.power_combo, "on"),
        #     (10, self.temp_input, "18"),
        #     (50, self.wind_combo, "高"),
        #     (90, self.temp_input, "22"),
        #     (140, self.power_combo, "off"),
        #     (180, self.power_combo, "on"),
        #     (180, self.temp_input, "25"),
        #     (240, self.power_combo, "off"),
        # ]
        return [
            (0, self.power_combo, "on"),
            (10, self.temp_input, "24"),
            (50, self.wind_combo, "高"),
            (90, self.temp_input, "28"),
            (140, self.power_combo, "off"),
            (180, self.power_combo, "on"),
            (180, self.wind_combo, "中"),
            (180, self.temp_input, "22"),
            (240, self.power_combo, "off"),
        ]
        

    def get_process2_tasks(self):
        # return [
        #     (10, self.power_combo, "on"),
        #     (30, self.temp_input, "19"),
        #     (60, self.power_combo, "off"),
        #     (70, self.power_combo, "on"),
        #     (70, self.temp_input, "25"),
        #     (110, self.temp_input, "22"),
        #     (160, self.power_combo, "off"),
        #     (190, self.power_combo, "on"),
        #     (190, self.temp_input, "25"),
        #     (250, self.power_combo, "off"),
        # ]
        return [
            (10, self.power_combo, "on"),
            (30, self.temp_input, "25"),
            (120, self.wind_combo, "高"),
            (200, self.wind_combo, "中"),
            (200, self.temp_input, "27"),
            (250, self.power_combo, "off"),
        ]
    def get_process3_tasks(self):
        # return [
        #     (20, self.power_combo, "on"),
        #     (140, self.temp_input, "24"),
        #     (140, self.wind_combo, "低"),
        #     (170, self.wind_combo, "高"),
        #     (220, self.power_combo, "off"),
        # ]
        return [
            (20, self.power_combo, "on"),
            (40, self.temp_input, "27"),
            (140, self.wind_combo, "低"),
            (170, self.wind_combo, "高"),
            (240, self.power_combo, "off"),
        ]
    def get_process4_tasks(self):
        # return [
        #     (30, self.power_combo, "on"),
        #     (90, self.temp_input, "18"),
        #     (90, self.wind_combo, "高"),  # 同时更新温度和风速
        #     (180, self.temp_input, "20"),
        #     (180, self.wind_combo, "中"),
        #     (250, self.power_combo, "off"),
        # ]
        return [
            (30, self.power_combo, "on"),
            (90, self.temp_input, "28"),
            (90, self.wind_combo, "高"),  # 同时更新温度和风速
            (180, self.wind_combo, "中"),
            (180, self.temp_input, "25"),
            (250, self.power_combo, "off"),
        ]
    def get_process5_tasks(self):
        # return [
        #     (10, self.power_combo, "on"),
        #     (40, self.temp_input, "22"),
        #     (70, self.wind_combo, "高"),
        #     (120, self.wind_combo, "低"),
        #     (150, self.temp_input, "20"),
        #     (150, self.wind_combo, "高"),
        #     (200, self.temp_input, "25"),
        #     (230, self.power_combo, "off"),
        # ]
        return [
            (30, self.power_combo, "on"),
            (40, self.wind_combo, "高"),
            (70, self.temp_input, "24"),
            (110, self.wind_combo, "中"),
            (160, self.power_combo, "off"),
            (200, self.power_combo, "on"),
            (200, self.temp_input, "22"),
            (240, self.power_combo, "off"),
        ]
