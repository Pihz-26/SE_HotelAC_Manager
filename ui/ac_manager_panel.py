# ac_manager_panel.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSpinBox, QDoubleSpinBox, QPushButton, QMessageBox, QFileDialog, QTableWidget, QTableWidgetItem
from common import post_json, get_json
from exporter import export_bill, export_detail
import json

class AcManagerPanel(QWidget):
    def __init__(self, token):
        super().__init__()
        self.token = token
        self.setWindowTitle("空调管理界面 (AC Manager)")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 模式设置
        layout.addWidget(QLabel("模式 (0冷, 1热):"))
        self.mode_box = QSpinBox()
        self.mode_box.setRange(0, 1)
        layout.addWidget(self.mode_box)

        # 资源限制设置
        layout.addWidget(QLabel("资源限制 (0或1):"))
        self.resource_box = QSpinBox()
        self.resource_box.setRange(0, 1)
        layout.addWidget(self.resource_box)

        # 风速费率设置
        layout.addWidget(QLabel("低风速费率:"))
        self.low_rate = QDoubleSpinBox()
        self.low_rate.setValue(0.5)
        self.low_rate.setDecimals(2)
        layout.addWidget(self.low_rate)

        layout.addWidget(QLabel("中风速费率:"))
        self.mid_rate = QDoubleSpinBox()
        self.mid_rate.setValue(1.0)
        self.mid_rate.setDecimals(2)
        layout.addWidget(self.mid_rate)

        layout.addWidget(QLabel("高风速费率:"))
        self.high_rate = QDoubleSpinBox()
        self.high_rate.setValue(2.0)
        self.high_rate.setDecimals(2)
        layout.addWidget(self.high_rate)

        # 设置中央空调参数按钮
        set_btn = QPushButton("设置中央空调参数")
        set_btn.clicked.connect(self.set_ac_params)
        layout.addWidget(set_btn)

        # 查看全局状态按钮
        refresh_btn = QPushButton("查看全局状态")
        refresh_btn.clicked.connect(self.refresh_status)
        layout.addWidget(refresh_btn)

        # 导出账单按钮
        export_bill_btn = QPushButton("导出账单")
        export_bill_btn.clicked.connect(self.export_bills)
        layout.addWidget(export_bill_btn)

        # 导出详单按钮
        export_detail_btn = QPushButton("导出详单")
        export_detail_btn.clicked.connect(self.export_details)
        layout.addWidget(export_detail_btn)

        # 打印调度记录按钮
        print_schedule_btn = QPushButton("打印调度记录")
        print_schedule_btn.clicked.connect(self.print_schedule_log)
        layout.addWidget(print_schedule_btn)

        # 空调状态表格
        self.table = QTableWidget()
        self.table.setColumnCount(11)  # 添加了 'Status' 和 'TimeSlice'
        self.table.setHorizontalHeaderLabels(['RoomId','RoomTemp','Power','TargetTemp','WindSpeed','Mode','Sweep','Cost','TotalCost','Status','TimeSlice'])
        layout.addWidget(self.table)

        self.setLayout(layout)

    def set_ac_params(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "mode": self.mode_box.value(),
            "resourceLimit": self.resource_box.value(),
            "fanRates": {
                "lowSpeedRate": self.low_rate.value(),
                "midSpeedRate": self.mid_rate.value(),
                "highSpeedRate": self.high_rate.value()
            }
        }
        res = post_json("/central-aircon/adjust", data, headers=headers)
        if res and res.status_code == 200:
            d = res.json()
            if d["code"] == 0:
                QMessageBox.information(self, "成功", d["message"])
            else:
                QMessageBox.critical(self, "错误", d.get("message", "设置失败"))
        else:
            QMessageBox.critical(self, "错误", f"设置失败 {res.status_code if res else '无响应'}")

    def refresh_status(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        res = get_json("/aircon/status", headers=headers)
        if res and res.status_code == 200:
            data = res.json()
            if data["code"] == 0:
                ac_states = data["data"]
                self.table.setRowCount(len(ac_states))
                for i, s in enumerate(ac_states):
                    self.table.setItem(i, 0, QTableWidgetItem(str(s["roomId"])))
                    self.table.setItem(i, 1, QTableWidgetItem(str(s["roomTemperature"])))
                    self.table.setItem(i, 2, QTableWidgetItem("on" if s["power"] else "off"))
                    self.table.setItem(i, 3, QTableWidgetItem(str(s["targetTemperature"])))
                    self.table.setItem(i, 4, QTableWidgetItem(s["windSpeed"]))
                    self.table.setItem(i, 5, QTableWidgetItem(s["mode"]))
                    self.table.setItem(i, 6, QTableWidgetItem("开" if s["sweep"] else "关"))
                    self.table.setItem(i, 7, QTableWidgetItem(str(s["cost"])))
                    self.table.setItem(i, 8, QTableWidgetItem(str(s["totalCost"])))
                    self.table.setItem(i, 9, QTableWidgetItem(str(s["status"])))
                    self.table.setItem(i, 10, QTableWidgetItem(str(s["timeSlice"])))
            else:
                QMessageBox.critical(self, "错误", data.get("message", "查询失败"))
        else:
            QMessageBox.critical(self, "错误", f"查询失败 {res.status_code if res else '无响应'}")

    def export_bills(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        res = get_json("/admin/query_room", headers=headers)
        if res and res.status_code == 200:
            data = res.json()
            if data["code"] == 0:
                rooms = data["data"]
                bill_data = []
                for room in rooms:
                    if room["state"]:
                        bill = {
                            "roomId": room["roomId"],
                            "checkIn": room.get("checkInTime", "无"),
                            "checkOut": room.get("checkOutTime", "未退房"),
                            "totalCost": room["totalCost"]
                        }
                        bill_data.append(bill)
                if bill_data:
                    options = QFileDialog.Options()
                    filename, _ = QFileDialog.getSaveFileName(self, "保存账单", "bills.xlsx", "Excel Files (*.xlsx)", options=options)
                    if filename:
                        export_bill(bill_data, filename)
                        QMessageBox.information(self, "成功", f"账单已导出为 {filename}")
                else:
                    QMessageBox.information(self, "信息", "暂无需要导出的账单数据")
            else:
                QMessageBox.critical(self, "错误", data.get("message", "查询失败"))
        else:
            QMessageBox.critical(self, "错误", f"查询失败 {res.status_code if res else '无响应'}")

    def export_details(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        res = get_json("/admin/query_room", headers=headers)
        if res and res.status_code == 200:
            data = res.json()
            if data["code"] == 0:
                rooms = data["data"]
                detail_data = []
                for room in rooms:
                    if room["state"]:
                        ac_logs = room.get("acLogs", [])
                        for log in ac_logs:
                            detail = {
                                "roomId": room["roomId"],
                                "startTime": room.get("checkInTime", "无"),
                                "endTime": room.get("checkOutTime", "未退房"),
                                "windSpeed": log.get("windSpeed", "N/A"),
                                "cost": log.get("cost", 0)
                            }
                            detail_data.append(detail)
                if detail_data:
                    options = QFileDialog.Options()
                    filename, _ = QFileDialog.getSaveFileName(self, "保存详单", "details.xlsx", "Excel Files (*.xlsx)", options=options)
                    if filename:
                        export_detail(detail_data, filename)
                        QMessageBox.information(self, "成功", f"详单已导出为 {filename}")
                else:
                    QMessageBox.information(self, "信息", "暂无需要导出的详单数据")
            else:
                QMessageBox.critical(self, "错误", data.get("message", "查询失败"))
        else:
            QMessageBox.critical(self, "错误", f"查询失败 {res.status_code if res else '无响应'}")

    def print_schedule_log(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        res = get_json("/admin/query_schedule", headers=headers)
        if res and res.status_code == 200:
            data = res.json()
            if data["code"] == 0:
                schedule_logs = data["data"]
                if not schedule_logs:
                    QMessageBox.information(self, "调度记录", "暂无调度记录")
                    return
                # 格式化调度记录
                log_info = ""
                for log in schedule_logs:
                    wait_queue = ", ".join(map(str, log['waitQueue'])) if log['waitQueue'] else "无"
                    running_queue = ", ".join(map(str, log['runningQueue'])) if log['runningQueue'] else "无"
                    log_info += (f"时间: {log['time']}\n"
                                 f"等待队列: {wait_queue}\n"
                                 f"运行队列: {running_queue}\n\n")
                QMessageBox.information(self, "调度记录", log_info)
            else:
                QMessageBox.critical(self, "错误", data.get("message", "查询失败"))
        else:
            QMessageBox.critical(self, "错误", f"查询失败 {res.status_code if res else '无响应'}")