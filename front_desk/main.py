# front_desk/main.py

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox,
    QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QInputDialog
)
from PyQt5.QtCore import Qt
import requests
from request_body import CheckInRequest
from respond_body import HotelStatusResponse, DetailedBillResponse
from pydantic import ValidationError

class FrontDeskWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("前台营业管理系统")
        self.setGeometry(100, 100, 800, 600)
        self.setup_ui()
        self.refresh_hotel_status()

    def setup_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # 酒店入住情况
        status_layout = QVBoxLayout()
        status_label = QLabel("酒店入住情况")
        status_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        status_layout.addWidget(status_label)

        self.status_table = QTableWidget()
        self.status_table.setColumnCount(5)
        self.status_table.setHorizontalHeaderLabels([
            "房间号", "房间等级", "空调消费(KWH)", "入住时间", "住户"
        ])
        self.status_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        status_layout.addWidget(self.status_table)

        # 操作按钮
        button_layout = QHBoxLayout()
        refresh_button = QPushButton("刷新")
        refresh_button.clicked.connect(self.refresh_hotel_status)
        button_layout.addWidget(refresh_button)

        checkin_button = QPushButton("办理入住")
        checkin_button.clicked.connect(self.check_in)
        button_layout.addWidget(checkin_button)

        checkout_button = QPushButton("办理退房")
        checkout_button.clicked.connect(self.check_out)
        button_layout.addWidget(checkout_button)

        detail_button = QPushButton("开具详单")
        detail_button.clicked.connect(self.view_detailed_bill)
        button_layout.addWidget(detail_button)

        status_layout.addLayout(button_layout)
        main_layout.addLayout(status_layout)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def refresh_hotel_status(self):
        url = "http://127.0.0.1:8000/stage/query"
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "网络错误", str(e))
            return

        data = response.json()
        try:
            status_response = HotelStatusResponse(**data)
        except ValidationError as e:
            QMessageBox.warning(self, "数据错误", str(e))
            return

        self.update_status_table(status_response.data)

    def update_status_table(self, room_list):
        self.status_table.setRowCount(len(room_list))
        for row, room in enumerate(room_list):
            self.status_table.setItem(row, 0, QTableWidgetItem(str(room.roomId)))
            self.status_table.setItem(row, 1, QTableWidgetItem(room.roomLevel))
            self.status_table.setItem(row, 2, QTableWidgetItem(f"{room.cost:.2f}"))
            self.status_table.setItem(row, 3, QTableWidgetItem(room.checkInTime))
            people_names = ', '.join([p.peopleName for p in room.people])
            self.status_table.setItem(row, 4, QTableWidgetItem(people_names))

    def check_in(self):
        room_id, ok = QInputDialog.getInt(self, "办理入住", "请输入房间号：")
        if not ok:
            return
        people_name, ok = QInputDialog.getText(self, "办理入住", "请输入顾客姓名：")
        if not ok:
            return

        request_data = CheckInRequest(roomId=room_id, peopleName=people_name)
        url = "http://127.0.0.1:8000/stage/add"
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, json=request_data.dict(), headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "网络错误", str(e))
            return

        data = response.json()
        if data.get("code") == 0:
            QMessageBox.information(self, "成功", data.get("message", "顾客添加成功"))
            self.refresh_hotel_status()
        else:
            QMessageBox.warning(self, "错误", data.get("message", "操作失败"))

    def check_out(self):
        room_id, ok = QInputDialog.getInt(self, "办理退房", "请输入房间号：")
        if not ok:
            return

        url = f"http://127.0.0.1:8000/stage/delete?roomId={room_id}"
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "网络错误", str(e))
            return

        data = response.json()
        if data.get("code") == 0:
            QMessageBox.information(self, "成功", data.get("message", "退房成功"))
            self.refresh_hotel_status()
        else:
            QMessageBox.warning(self, "错误", data.get("message", "操作失败"))

    def view_detailed_bill(self):
        room_id, ok = QInputDialog.getInt(self, "开具详单", "请输入房间号：")
        if not ok:
            return

        url = f"http://127.0.0.1:8000/stage/record?roomId={room_id}"
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "网络错误", str(e))
            return

        data = response.json()
        try:
            bill_response = DetailedBillResponse(**data)
        except ValidationError as e:
            QMessageBox.warning(self, "数据错误", str(e))
            return

        # 展示详单信息，可以创建一个新的窗口显示
        self.show_detailed_bill(bill_response)

    def show_detailed_bill(self, bill_response):
        bill_data = bill_response.data
        people_names = ', '.join([p.peopleName for p in bill_data.people])
        records = bill_data.records

        msg = f"入住时间：{bill_response.checkInTime}\n"
        msg += f"总消费：{bill_data.cost:.2f} KWH\n"
        msg += f"住户：{people_names}\n\n"
        msg += "空调使用记录：\n"

        for record in records:
            msg += f"时间：{record.time}, 消耗：{record.cost} KWH, 电源：{record.power}, 温度：{record.temperature}℃, 风速：{record.windSpeed}, 模式：{record.mode}, 扫风：{record.sweep}\n"

        QMessageBox.information(self, "详单", msg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FrontDeskWindow()
    window.show()
    sys.exit(app.exec_())
