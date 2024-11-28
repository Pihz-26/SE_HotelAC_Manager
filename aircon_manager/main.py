# front/main.py

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox,
    QLabel, QComboBox, QSpinBox, QDoubleSpinBox, QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PyQt5.QtCore import Qt, QTimer
import requests
from request_body import CentralAirconAdjustRequest, FanRates
from respond_body import AirconStatusResponse
from pydantic import ValidationError

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("酒店空调管理系统")
        self.setGeometry(100, 100, 1000, 700)
        self.setup_ui()

    def setup_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # 中央空调设置部分
        adjust_layout = QVBoxLayout()
        adjust_label = QLabel("中央空调设置")
        adjust_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        adjust_layout.addWidget(adjust_label)

        # 模式选择
        mode_layout = QHBoxLayout()
        mode_label = QLabel("模式：")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["制冷", "制热"])
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)
        adjust_layout.addLayout(mode_layout)

        # 资源限制
        resource_layout = QHBoxLayout()
        resource_label = QLabel("资源限制(0为无限制)：")
        self.resource_spin = QSpinBox()
        self.resource_spin.setRange(0, 100)
        resource_layout.addWidget(resource_label)
        resource_layout.addWidget(self.resource_spin)
        adjust_layout.addLayout(resource_layout)

        # 风速费率
        rate_layout = QVBoxLayout()
        rate_label = QLabel("风速费率(元/度)：")
        rate_label.setStyleSheet("margin-top:10px;")
        rate_layout.addWidget(rate_label)

        rate_form_layout = QHBoxLayout()
        self.low_rate_spin = QDoubleSpinBox()
        self.low_rate_spin.setPrefix("低速费率：")
        self.low_rate_spin.setRange(0.0, 100.0)
        self.low_rate_spin.setSingleStep(0.1)

        self.mid_rate_spin = QDoubleSpinBox()
        self.mid_rate_spin.setPrefix("中速费率：")
        self.mid_rate_spin.setRange(0.0, 100.0)
        self.mid_rate_spin.setSingleStep(0.1)

        self.high_rate_spin = QDoubleSpinBox()
        self.high_rate_spin.setPrefix("高速费率：")
        self.high_rate_spin.setRange(0.0, 100.0)
        self.high_rate_spin.setSingleStep(0.1)

        rate_form_layout.addWidget(self.low_rate_spin)
        rate_form_layout.addWidget(self.mid_rate_spin)
        rate_form_layout.addWidget(self.high_rate_spin)
        rate_layout.addLayout(rate_form_layout)
        adjust_layout.addLayout(rate_layout)

        # 调整按钮
        adjust_button = QPushButton("调整设置")
        adjust_button.clicked.connect(self.adjust_settings)
        adjust_layout.addWidget(adjust_button)

        main_layout.addLayout(adjust_layout)

        # 分割线
        separator = QLabel()
        separator.setFixedHeight(2)
        separator.setStyleSheet("background-color: #ccc; margin: 20px 0;")
        main_layout.addWidget(separator)

        # 空调状态显示部分
        status_layout = QVBoxLayout()
        status_label = QLabel("空调运行状态")
        status_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        status_layout.addWidget(status_label)

        self.status_table = QTableWidget()
        self.status_table.setColumnCount(10)
        self.status_table.setHorizontalHeaderLabels([
            "房间号", "室温", "电源", "目标温度", "风速",
            "模式", "扫风", "费用", "总费用", "状态"
        ])
        self.status_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        status_layout.addWidget(self.status_table)

        # 刷新按钮
        refresh_button = QPushButton("刷新状态")
        refresh_button.clicked.connect(self.refresh_status)
        status_layout.addWidget(refresh_button)

        main_layout.addLayout(status_layout)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # 定时器，每隔60秒自动刷新
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_status)
        self.timer.start(60000)  # 60,000 毫秒，即60秒

        # 首次启动时刷新一次
        self.refresh_status()

    def adjust_settings(self):
        mode = self.mode_combo.currentIndex()  # 0-制冷，1-制热
        resource_limit = self.resource_spin.value()
        fan_rates = FanRates(
            lowSpeedRate=self.low_rate_spin.value(),
            midSpeedRate=self.mid_rate_spin.value(),
            highSpeedRate=self.high_rate_spin.value()
        )
        request_data = CentralAirconAdjustRequest(
            mode=mode,
            resourceLimit=resource_limit,
            fanRates=fan_rates
        )

        try:
            # 验证请求数据
            request_data_dict = request_data.dict()
        except ValidationError as e:
            QMessageBox.warning(self, "验证错误", str(e))
            return

        # 发送POST请求到后端
        url = "http://127.0.0.1:8000/central-aircon/adjust"
        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=request_data_dict, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "网络错误", str(e))
            return

        data = response.json()
        if data.get("code") == 0:
            QMessageBox.information(self, "成功", data.get("message", "中央空调设置成功"))
        else:
            QMessageBox.warning(self, "错误", data.get("message", "设置失败"))

    def refresh_status(self):
        # 发送GET请求获取空调状态
        url = "http://127.0.0.1:8000/aircon/status"
        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "网络错误", str(e))
            return

        data = response.json()
        try:
            status_response = AirconStatusResponse(**data)
        except ValidationError as e:
            QMessageBox.warning(self, "数据错误", str(e))
            return

        self.update_status_table(status_response.data)

    def update_status_table(self, room_status_list):
        self.status_table.setRowCount(len(room_status_list))
        for row, status in enumerate(room_status_list):
            self.status_table.setItem(row, 0, QTableWidgetItem(str(status.roomId)))
            self.status_table.setItem(row, 1, QTableWidgetItem(str(status.roomTemperature)))
            self.status_table.setItem(row, 2, QTableWidgetItem(status.power))
            self.status_table.setItem(row, 3, QTableWidgetItem(str(status.temperature)))
            self.status_table.setItem(row, 4, QTableWidgetItem(status.windSpeed))
            self.status_table.setItem(row, 5, QTableWidgetItem(status.mode))
            self.status_table.setItem(row, 6, QTableWidgetItem(status.sweep))
            self.status_table.setItem(row, 7, QTableWidgetItem(f"{status.cost:.2f}"))
            self.status_table.setItem(row, 8, QTableWidgetItem(f"{status.totalCost:.2f}"))
            self.status_table.setItem(row, 9, QTableWidgetItem(str(status.status)))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
