# client/main.py

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox,
    QLabel, QComboBox, QSpinBox, QDoubleSpinBox
)
from PyQt5.QtCore import Qt, QTimer
import requests
from request_body import AirconControlRequest
from respond_body import AirconPanelResponse
from pydantic import ValidationError

class ClientWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("房间空调控制面板")
        self.setGeometry(100, 100, 400, 300)
        self.room_id = 2001  # 示例房间号，可以根据实际情况设置
        self.setup_ui()
        self.refresh_panel()

    def setup_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # 空调状态显示
        status_layout = QVBoxLayout()
        status_label = QLabel("空调状态")
        status_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        status_layout.addWidget(status_label)

        self.room_temp_label = QLabel("室温：")
        self.power_label = QLabel("电源：")
        self.temperature_label = QLabel("温度：")
        self.wind_speed_label = QLabel("风速：")
        self.mode_label = QLabel("模式：")
        self.sweep_label = QLabel("扫风：")
        self.cost_label = QLabel("当前消费：")
        self.total_cost_label = QLabel("总消费：")

        status_layout.addWidget(self.room_temp_label)
        status_layout.addWidget(self.power_label)
        status_layout.addWidget(self.temperature_label)
        status_layout.addWidget(self.wind_speed_label)
        status_layout.addWidget(self.mode_label)
        status_layout.addWidget(self.sweep_label)
        status_layout.addWidget(self.cost_label)
        status_layout.addWidget(self.total_cost_label)

        main_layout.addLayout(status_layout)

        # 空调控制
        control_layout = QVBoxLayout()
        control_label = QLabel("空调控制")
        control_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        control_layout.addWidget(control_label)

        # 开关
        power_layout = QHBoxLayout()
        power_label = QLabel("电源：")
        self.power_combo = QComboBox()
        self.power_combo.addItems(["on", "off"])
        power_layout.addWidget(power_label)
        power_layout.addWidget(self.power_combo)
        control_layout.addLayout(power_layout)

        # 温度
        temp_layout = QHBoxLayout()
        temp_label = QLabel("温度：")
        self.temp_spin = QSpinBox()
        self.temp_spin.setRange(16, 30)
        temp_layout.addWidget(temp_label)
        temp_layout.addWidget(self.temp_spin)
        control_layout.addLayout(temp_layout)

        # 风速
        wind_layout = QHBoxLayout()
        wind_label = QLabel("风速：")
        self.wind_combo = QComboBox()
        self.wind_combo.addItems(["低", "中", "高"])
        wind_layout.addWidget(wind_label)
        wind_layout.addWidget(self.wind_combo)
        control_layout.addLayout(wind_layout)

        # 扫风
        sweep_layout = QHBoxLayout()
        sweep_label = QLabel("扫风：")
        self.sweep_combo = QComboBox()
        self.sweep_combo.addItems(["关", "开"])
        sweep_layout.addWidget(sweep_label)
        sweep_layout.addWidget(self.sweep_combo)
        control_layout.addLayout(sweep_layout)

        # 控制按钮
        control_button = QPushButton("提交")
        control_button.clicked.connect(self.control_aircon)
        control_layout.addWidget(control_button)

        main_layout.addLayout(control_layout)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # 定时刷新面板
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_panel)
        self.timer.start(60000)  # 每60秒刷新

    def control_aircon(self):
        power = self.power_combo.currentText()
        temperature = self.temp_spin.value()
        wind_speed = self.wind_combo.currentText()
        sweep = self.sweep_combo.currentText()

        request_data = AirconControlRequest(
            roomId=self.room_id,
            power=power,
            temperature=temperature,
            windSpeed=wind_speed,
            sweep=sweep
        )

        url = "http://127.0.0.1:8000/aircon/control"
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, json=request_data.dict(), headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "网络错误", str(e))
            return

        data = response.json()
        if data.get("code") == 0:
            QMessageBox.information(self, "成功", data.get("message", "空调设置已更新"))
            self.refresh_panel()
        else:
            QMessageBox.warning(self, "错误", data.get("message", "设置失败"))

    def refresh_panel(self):
        url = f"http://127.0.0.1:8000/aircon/panel?roomId={self.room_id}"
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "网络错误", str(e))
            return

        data = response.json()
        try:
            panel_response = AirconPanelResponse(**data)
        except ValidationError as e:
            QMessageBox.warning(self, "数据错误", str(e))
            return

        panel_data = panel_response.data
        self.room_temp_label.setText(f"室温：{panel_data.roomTemperature}℃")
        self.power_label.setText(f"电源：{panel_data.power}")
        self.temperature_label.setText(f"温度：{panel_data.temperature}℃")
        self.wind_speed_label.setText(f"风速：{panel_data.windSpeed}")
        self.mode_label.setText(f"模式：{panel_data.mode}")
        self.sweep_label.setText(f"扫风：{panel_data.sweep}")
        self.cost_label.setText(f"当前消费：{panel_data.cost:.2f} KWH")
        self.total_cost_label.setText(f"总消费：{panel_data.totalCost:.2f} KWH")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClientWindow()
    window.show()
    sys.exit(app.exec_())
