# frontend/manager_panel.py
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog
from common import post_json, get_json
from exporter import export_bill, export_detail

class ManagerPanel(QWidget):
    def __init__(self, token):
        super().__init__()
        self.token = token
        self.setWindowTitle("酒店经理界面（Manager）")
        self.setGeometry(600, 200, 800, 600)
        # 背景层
        self.background_widget = QLabel(self)
        self.background_widget.setGeometry(0, 0, 800, 600)
        self.background_widget.setStyleSheet("border-image: url('image/经理背景.png');")

        # 控件层
        self.widget_layer = QWidget(self)
        self.widget_layer.setGeometry(0, 0, 800, 600)
        self.init_ui()

    def init_ui(self):
        # 创建 "查看全局状态" 按钮
        self.refresh_btn = QPushButton("查看全局状态", self)  # 按钮设置为 self 属性
        self.refresh_btn.setGeometry(20, 20, 150, 50)  # 自由设置位置和大小
        self.refresh_btn.clicked.connect(self.refresh_status)  # 绑定按钮点击事件
        self.refresh_btn.setStyleSheet(
            "font-size: 16px; color: black;"
            "border: 2px solid black; border-radius: 10px;"
            "background-color: white;"
            "transition: background-color 0.3s;"  # 使过渡更平滑(optional)  
            "}"
            "QPushButton:hover {"
            "background-color: pink;"  # 鼠标悬停时背景变为粉色  
            "}"
        )

        # 创建 "导出账单" 按钮
        self.export_bill_btn = QPushButton("导出账单", self)
        self.export_bill_btn.setGeometry(20, 90, 150, 50)
        self.export_bill_btn.clicked.connect(self.export_bills)
        self.export_bill_btn.setStyleSheet(
            "font-size: 16px; color: black;"
            "border: 2px solid black; border-radius: 10px;"
            "background-color: white;"
            "transition: background-color 0.3s;"  # 使过渡更平滑(optional)  
            "}"
            "QPushButton:hover {"
            "background-color: pink;"  # 鼠标悬停时背景变为粉色  
            "}"
        )

        # 创建 "导出详单" 按钮
        self.export_detail_btn = QPushButton("导出详单", self)
        self.export_detail_btn.setGeometry(20, 160, 150, 50)
        self.export_detail_btn.clicked.connect(self.export_details)
        self.export_detail_btn.setStyleSheet(
            "font-size: 16px; color: black;"
            "border: 2px solid black; border-radius: 10px;"
            "background-color: white;"
            "transition: background-color 0.3s;"  # 使过渡更平滑(optional)  
            "}"
            "QPushButton:hover {"
            "background-color: pink;"  # 鼠标悬停时背景变为粉色  
            "}"
        )

        # 创建 "打印调度记录" 按钮
        self.print_schedule_btn = QPushButton("打印调度记录", self)
        self.print_schedule_btn.setGeometry(20, 230, 150, 50)
        self.print_schedule_btn.clicked.connect(self.print_schedule_log)
        self.print_schedule_btn.setStyleSheet(
            "font-size: 16px; color: black;"
            "border: 2px solid black; border-radius: 10px;"
            "background-color: white;"
            "transition: background-color 0.3s;"  # 使过渡更平滑(optional)  
            "}"
            "QPushButton:hover {"
            "background-color: pink;"  # 鼠标悬停时背景变为粉色  
            "}"
        )

        # 创建表格组件
        self.table = QTableWidget(self)
        self.table.setGeometry(200, 20, 580, 550)  # 自由设置表格位置和大小
        self.table.setColumnCount(11)  # 设置列数为11以匹配标题
        self.table.setHorizontalHeaderLabels(['RoomId', 'RoomTemp', 'Power', 'TargetTemp',
                                              'WindSpeed', 'Mode', 'Sweep', 'Cost',
                                              'TotalCost', 'Status', 'TimeSlice'])

    def refresh_status(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        res = get_json("/aircon/status", headers=headers)
        if res and res.status_code == 200:
            data = res.json()
            if data.get("code") == 0:
                ac_states = data.get("data", [])
                self.table.setRowCount(len(ac_states))
                for i, s in enumerate(ac_states):
                    self.table.setItem(i, 0, QTableWidgetItem(str(s.get("roomId", ""))))
                    self.table.setItem(i, 1, QTableWidgetItem(str(s.get("roomTemperature", ""))))
                    self.table.setItem(i, 2, QTableWidgetItem("on" if s.get("power") else "off"))
                    self.table.setItem(i, 3, QTableWidgetItem(str(s.get("targetTemperature", ""))))
                    self.table.setItem(i, 4, QTableWidgetItem(s.get("windSpeed", "")))
                    self.table.setItem(i, 5, QTableWidgetItem(s.get("mode", "")))
                    self.table.setItem(i, 6, QTableWidgetItem("开" if s.get("sweep") else "关"))
                    self.table.setItem(i, 7, QTableWidgetItem(str(s.get("cost", ""))))
                    self.table.setItem(i, 8, QTableWidgetItem(str(s.get("totalCost", ""))))
                    self.table.setItem(i, 9, QTableWidgetItem(str(s.get("status", ""))))
                    self.table.setItem(i, 10, QTableWidgetItem(str(s.get("timeSlice", "N/A"))))
            else:
                QMessageBox.critical(self, "错误", data.get("message", "查询失败"))
        else:
            QMessageBox.critical(self, "错误", f"查询失败: {res.status_code if res else '无响应'}")

    def export_bills(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        # 确保发送空的数据对象，以避免后端误判
        res = post_json("/admin/query_room", data={}, headers=headers)  # 使用 POST 方法并传递空数据
        if res and res.status_code == 200:
            data = res.json()
            if data.get("code") == 0:
                rooms = data.get("data", [])
                bill_data = []
                print(f"导出账单时收到的房间数据: {rooms}")  # 调试信息
                for room in rooms:
                    # 根据接口文档，房间数据中没有 'state' 字段，需要调整过滤条件
                    # 假设有 'people' 字段，如果有住户则表示房间被占用
                    if room.get("people"):
                        room_id = room.get("roomId")
                        housing_cost = 200  # 固定住房费用为200
                        # 获取空调使用费用
                        record_res = get_json("/stage/record", headers=headers, params={"roomId": room_id})
                        if record_res and record_res.status_code == 200:
                            record_data = record_res.json()
                            if record_data.get("code") == 0:
                                ac_usage_cost = record_data.get("data", {}).get("cost", 0)
                                bill = {
                                    "roomId": room_id,
                                    "housingCost": housing_cost,
                                    "acUsageCost": ac_usage_cost
                                }
                                bill_data.append(bill)
                            else:
                                print(f"获取房间 {room_id} 详单失败: {record_data.get('message', '')}")
                        else:
                            print(f"获取房间 {room_id} 详单请求失败: {record_res.status_code if record_res else '无响应'}")
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
            QMessageBox.critical(self, "错误", f"查询失败: {res.status_code if res else '无响应'}")

    def export_details(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        # 调用 /admin/query_room 获取所有房间信息
        res = post_json("/admin/query_room", data={}, headers=headers)  # 使用 POST 方法并传递空数据
        if res and res.status_code == 200:
            data = res.json()
            if data.get("code") == 0:
                rooms = data.get("data", [])
                detail_data = []
                print(f"导出详单时收到的房间数据: {rooms}")  # 调试信息
                for room in rooms:
                    # 根据接口文档，房间数据中没有 'state' 字段，需要调整过滤条件
                    # 假设有 'people' 字段，如果有住户则表示房间被占用
                    if room.get("people"):
                        room_id = room.get("roomId")
                        # 获取详单记录
                        record_res = get_json("/stage/record", headers=headers, params={"roomId": room_id})
                        if record_res and record_res.status_code == 200:
                            record_data = record_res.json()
                            if record_data.get("code") == 0:
                                records = record_data.get("data", {}).get("records", [])
                                for rec in records:
                                    detail = {
                                        "roomId": room_id,
                                        "time": rec.get("time", "无"),
                                        "windSpeed": rec.get("windSpeed", "N/A"),
                                        "cost": rec.get("cost", 0)
                                    }
                                    detail_data.append(detail)
                            else:
                                print(f"获取房间 {room_id} 详单失败: {record_data.get('message', '')}")
                        else:
                            print(f"获取房间 {room_id} 详单请求失败: {record_res.status_code if record_res else '无响应'}")
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
            QMessageBox.critical(self, "错误", f"查询失败: {res.status_code if res else '无响应'}")

    def print_schedule_log(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        res = get_json("/admin/query_schedule", headers=headers)
        if res and res.status_code == 200:
            data = res.json()
            if data.get("code") == 0:
                schedule_logs = data.get("data", [])
                if not schedule_logs:
                    QMessageBox.information(self, "调度记录", "暂无调度记录")
                    return
                # 格式化调度记录
                log_info = ""
                for log in schedule_logs:
                    wait_queue = ", ".join(map(str, log.get('waitQueue', []))) if log.get('waitQueue') else "无"
                    running_queue = ", ".join(map(str, log.get('runningQueue', []))) if log.get('runningQueue') else "无"
                    log_info += (f"时间: {log.get('time')}\n"
                                 f"等待队列: {wait_queue}\n"
                                 f"运行队列: {running_queue}\n\n")
                QMessageBox.information(self, "调度记录", log_info)
            else:
                QMessageBox.critical(self, "错误", data.get("message", "查询失败"))
        else:
            QMessageBox.critical(self, "错误", f"查询失败: {res.status_code if res else '无响应'}")
