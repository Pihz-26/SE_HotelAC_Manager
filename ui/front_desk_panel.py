# front_desk_panel.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QInputDialog
from common import get_json, post_json
from urllib.parse import urlencode

class FrontDeskPanel(QWidget):
    def __init__(self, token):
        super().__init__()
        self.token = token
        self.setWindowTitle("前台界面 (Front Desk)")
        self.setGeometry(600, 200, 800, 600)
        # 背景层
        self.background_widget = QLabel(self)
        self.background_widget.setGeometry(0, 0, 800, 600)
        self.background_widget.setStyleSheet("border-image: url('ui/前台背景.png');")

        # 控件层
        self.widget_layer = QWidget(self)
        self.widget_layer.setGeometry(0, 0, 800, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 创建 "查询入住情况" 按钮
        self.query_btn = QPushButton("查询入住情况", self)  # 按钮设置为 self 属性
        self.query_btn.setGeometry(20, 20, 150, 40)  # 设置位置和大小
        self.query_btn.clicked.connect(self.query_rooms)  # 绑定按钮点击事件
        self.query_btn.setStyleSheet(
            "font-size: 18px; color: black;"
            "border: 2px solid black; border-radius: 10px;"
            "background-color: white;"
            "border-image: none;"
            "transition: background-color 0.3s;"  # 使过渡更平滑(optional)
            "}"
            "QPushButton:hover {"
            "background-color: pink;"  # 鼠标悬停时背景变为粉色
            "}"
        )

        # 创建 "办理入住" 按钮
        self.checkin_btn = QPushButton("办理入住", self)
        self.checkin_btn.setGeometry(20, 80, 150, 40)
        self.checkin_btn.clicked.connect(self.check_in)
        self.checkin_btn.setStyleSheet(
            "font-size: 18px; color: black;"
            "border: 2px solid black; border-radius: 10px;"
            "background-color: white;"
            "border-image: none;"
            "transition: background-color 0.3s;"
            "}"
            "QPushButton:hover {"
            "background-color: pink;"
            "}"
        )

        # 创建 "办理退房" 按钮
        self.checkout_btn = QPushButton("办理退房", self)
        self.checkout_btn.setGeometry(20, 140, 150, 40)
        self.checkout_btn.clicked.connect(self.check_out)
        self.checkout_btn.setStyleSheet(
            "font-size: 18px; color: black;"
            "border: 2px solid black; border-radius: 10px;"
            "background-color: white;"
            "border-image: none;"
            "transition: background-color 0.3s;"
            "}"
            "QPushButton:hover {"
            "background-color: pink;"
            "}"
        )

        # 创建 "查看详单" 按钮
        self.record_btn = QPushButton("查看详单", self)
        self.record_btn.setGeometry(20, 200, 150, 40)
        self.record_btn.clicked.connect(self.print_record)
        self.record_btn.setStyleSheet(
            "font-size: 18px; color: black;"
            "border: 2px solid black; border-radius: 10px;"
            "background-color: white;"
            "border-image: none;"
            "transition: background-color 0.3s;"
            "}"
            "QPushButton:hover {"
            "background-color: pink;"
            "}"
        )

        # 创建表格组件
        self.table = QTableWidget(self)
        self.table.setGeometry(200, 20, 580, 500)  # 设置表格位置和大小
        self.table.setColumnCount(5)  # 设置列数
        self.table.setHorizontalHeaderLabels(["RoomId", "RoomLevel", "Cost", "CheckInTime", "People"])

        layout.addWidget(self.table)
        self.setLayout(layout)

    def query_rooms(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        res = post_json("/stage/query", headers=headers)
        if res and res.status_code == 200:
            data = res.json()
            if data["code"] == 0:
                rooms = data["data"]
                self.table.setRowCount(len(rooms))
                for i, r in enumerate(rooms):
                    self.table.setItem(i, 0, QTableWidgetItem(str(r["roomId"])))
                    self.table.setItem(i, 1, QTableWidgetItem(r["roomLevel"]))
                    self.table.setItem(i, 2, QTableWidgetItem(str(r["cost"])))
                    self.table.setItem(i, 3, QTableWidgetItem(r.get("checkInTime", "无")))
                    self.table.setItem(i, 4, QTableWidgetItem("无" if not r["people"] else ", ".join([p["peopleName"] for p in r["people"]])))
            else:
                QMessageBox.critical(self, "错误", data.get("message", "查询失败"))
        else:
            QMessageBox.critical(self, "错误", f"查询失败: {res.status_code}")

    def check_in(self):
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        room_id, ok = QInputDialog.getText(self, "办理入住", "房间号:")
        if not ok or not room_id.strip().isdigit():
            QMessageBox.critical(self, "错误", "请正确输入房间号（数字）")
            return
        pname, ok = QInputDialog.getText(self, "办理入住", "顾客姓名:")
        if not ok or not pname.strip():
            QMessageBox.critical(self, "错误", "请正确输入顾客姓名")
            return
        data = {"roomId": room_id.strip(), "peopleName": pname.strip()}
        res = post_json("/stage/add", data=data, headers=headers)
        if res and res.status_code == 200:
            d = res.json()
            if d["code"] == 0:
                QMessageBox.information(self, "成功", "入住成功")
            else:
                QMessageBox.critical(self, "错误", d.get("message", "入住失败"))
        else:
            QMessageBox.critical(self, "错误", f"入住失败 {res.status_code if res else '无响应'}")

    def check_out(self):
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        room_id, ok = QInputDialog.getText(self, "办理退房", "房间号:")
        if not ok or not room_id.strip().isdigit():
            QMessageBox.critical(self, "错误", "请正确输入房间号（数字）")
            return
        data = {"roomId": room_id.strip()}
        url = f"/stage/delete?{urlencode(data)}"
        res = get_json(url, headers=headers)
        if res and res.status_code == 200:
            d = res.json()
            if d["code"] == 0:
                msg = f"退房成功！\n总费用: {d['bill']['totalCost']}"
                QMessageBox.information(self, "成功", msg)
            else:
                QMessageBox.critical(self, "错误", d.get("message", "退房失败"))
        else:
            QMessageBox.critical(self, "错误", f"退房失败 {res.status_code if res else '无响应'}")

    def print_record(self):
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        room_id, ok = QInputDialog.getText(self, "查看详单", "房间号:")
        if not ok or not room_id.strip().isdigit():
            QMessageBox.critical(self, "错误", "请正确输入房间号（数字）")
            return
        res = get_json(f"/stage/record?roomId={room_id.strip()}", headers=headers)
        if res and res.status_code == 200:
            d = res.json()
            if d["code"] == 0:
                record_data = d["data"]
                check_in_time = d.get("checkInTime", "无")
                total_cost = record_data.get("cost", "无")
                records = record_data.get("records", [])
                records_str = ""
                for rec in records:
                    records_str += f"时间: {rec['time']} | 状态: {rec['status']} | 温度: {rec['temperature']}°C | 风速: {rec['windSpeed']} | 模式: {rec['mode']} | 扫风: {rec['sweep']} | 费用: {rec['cost']}元\n"
                msg = f"查询成功\n入住时间: {check_in_time}\n总费用: {total_cost}\n\n空调使用记录:\n{records_str}"
                QMessageBox.information(self, "详单", msg)
            else:
                QMessageBox.critical(self, "错误", d.get("message", "查询失败"))
        else:
            QMessageBox.critical(self, "错误", f"查询失败 {res.status_code if res else '无响应'}")
