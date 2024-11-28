# hotel_manager/main.py

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
import requests
from respond_body import RoomInfoResponse
from pydantic import ValidationError

class HotelManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("酒店管理系统")
        self.setGeometry(100, 100, 1000, 600)
        self.setup_ui()
        self.refresh_room_info()

    def setup_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # 房间信息
        info_layout = QVBoxLayout()
        info_label = QLabel("房间信息")
        info_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        info_layout.addWidget(info_label)

        self.info_table = QTableWidget()
        self.info_table.setColumnCount(10)
        self.info_table.setHorizontalHeaderLabels([
            "房间号", "房间等级", "住户", "总消费(KWH)", "室温",
            "电源", "温度", "风速", "模式", "扫风"
        ])
        self.info_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        info_layout.addWidget(self.info_table)

        refresh_button = QPushButton("刷新")
        refresh_button.clicked.connect(self.refresh_room_info)
        info_layout.addWidget(refresh_button)

        main_layout.addLayout(info_layout)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def refresh_room_info(self):
        url = "http://127.0.0.1:8000/admin/query_room"  # 确保这里的 URL 正确，没有空格
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "网络错误", str(e))
            return

        data = response.json()
        try:
            info_response = RoomInfoResponse(**data)
        except ValidationError as e:
            QMessageBox.warning(self, "数据错误", str(e))
            return

        self.update_info_table(info_response.data)

    def update_info_table(self, room_list):
        self.info_table.setRowCount(len(room_list))
        for row, room in enumerate(room_list):
            self.info_table.setItem(row, 0, QTableWidgetItem(str(room.roomId)))
            self.info_table.setItem(row, 1, QTableWidgetItem(room.roomLevel))
            people_names = ', '.join([p.peopleName for p in room.people])
            self.info_table.setItem(row, 2, QTableWidgetItem(people_names))
            self.info_table.setItem(row, 3, QTableWidgetItem(f"{room.cost:.2f}"))
            self.info_table.setItem(row, 4, QTableWidgetItem(str(room.roomTemperature)))
            self.info_table.setItem(row, 5, QTableWidgetItem(room.power))
            self.info_table.setItem(row, 6, QTableWidgetItem(str(room.temperature)))
            self.info_table.setItem(row, 7, QTableWidgetItem(room.windSpeed))
            self.info_table.setItem(row, 8, QTableWidgetItem(room.mode))
            self.info_table.setItem(row, 9, QTableWidgetItem(room.sweep))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HotelManagerWindow()
    window.show()
    sys.exit(app.exec_())
