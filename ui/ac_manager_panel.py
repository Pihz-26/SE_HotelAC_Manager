# frontend/ac_manager_panel.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSpinBox, QDoubleSpinBox, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QFileDialog
from common import post_json, get_json
from exporter import export_bill, export_detail

class AcManagerPanel(QWidget):
    def __init__(self, token):
        super().__init__()
        self.token = token
        self.setWindowTitle("空调管理界面 (AC Manager)")
        self.setGeometry(600, 200, 1200, 600)
        # 背景层
        self.background_widget = QLabel(self)
        self.background_widget.setGeometry(0, 0, 1200, 600)
        self.background_widget.setStyleSheet("border-image: url('image/设置界面2.png');")

        # 控件层
        self.widget_layer = QWidget(self)
        self.widget_layer.setGeometry(0, 0, 1200, 600)
        self.init_ui()

    def init_ui(self):
        # 设置模式 (0: 冷, 1: 热)
        self.mode_label = QLabel("模式(0冷1热):", self)
        self.mode_label.setGeometry(120, 120, 250, 60)
        self.mode_label.setStyleSheet("font-size: 35px; color: black;border-image:none")


        self.mode_box = QSpinBox(self)
        self.mode_box.setRange(0, 1)
        self.mode_box.setGeometry(135, 180, 200, 60)
        self.mode_box.setStyleSheet("font-size: 60px; color: black;border-image:none")

        # 设置资源限制 (0 或 1)
        self.resource_label = QLabel("资源限制(0或1):", self)
        self.resource_label.setGeometry(520, 120, 250, 60)
        self.resource_label.setStyleSheet("font-size: 35px; color: black;border-image:none")


        self.resource_box = QSpinBox(self)
        self.resource_box.setRange(0, 1)
        self.resource_box.setGeometry(540, 180, 200, 60)
        self.resource_box.setStyleSheet("font-size: 60px; color: black;border-image:none")

        # 设置低风速费率
        self.low_rate_label = QLabel("低风速", self)
        self.low_rate_label.setGeometry(120, 305, 200, 60)
        self.low_rate_label.setStyleSheet("font-size: 35px; color: black;border-image:none")

        self.low_rate_label2 = QLabel("费率：", self)
        self.low_rate_label2.setGeometry(35, 390, 200, 60)
        self.low_rate_label2.setStyleSheet("font-size: 32px; color: black;border-image:none")


        self.low_rate = QDoubleSpinBox(self)
        self.low_rate.setValue(0.5)
        self.low_rate.setDecimals(2)
        self.low_rate.setGeometry(115, 390, 120, 60)
        self.low_rate.setStyleSheet("font-size: 35px; color: black;border-image:none")

        # 设置中风速费率
        self.mid_rate_label = QLabel("中风速", self)
        self.mid_rate_label.setGeometry(385, 305, 200, 60)
        self.mid_rate_label.setStyleSheet("font-size: 35px; color: black;border-image:none")

        self.mid_rate_label2 = QLabel("费率：", self)
        self.mid_rate_label2.setGeometry(302, 390, 100, 60)
        self.mid_rate_label2.setStyleSheet("font-size: 32px; color: black;border-image:none")

        self.mid_rate = QDoubleSpinBox(self)
        self.mid_rate.setValue(1.0)
        self.mid_rate.setDecimals(2)
        self.mid_rate.setGeometry(380, 390, 120, 60)
        self.mid_rate.setStyleSheet("font-size: 35px; color: black")

        # 设置高风速费率
        self.high_rate_label = QLabel("高风速", self)
        self.high_rate_label.setGeometry(645, 305, 200, 60)
        self.high_rate_label.setStyleSheet("font-size: 35px; color: black;border-image:none")

        self.high_rate_label2 = QLabel("费率：", self)
        self.high_rate_label2.setGeometry(560, 390, 100, 60)
        self.high_rate_label2.setStyleSheet("font-size: 32px; color: black;border-image:none")



        self.high_rate = QDoubleSpinBox(self)
        self.high_rate.setValue(2.0)
        self.high_rate.setDecimals(2)
        self.high_rate.setGeometry(640, 390, 120, 60)
        self.high_rate.setStyleSheet("font-size: 35px; color: black")

        # 设置中央空调参数按钮
        self.set_btn = QPushButton("设置中央空调参数", self)
        self.set_btn.setGeometry(255, 510, 210, 50)
        self.set_btn.clicked.connect(self.set_ac_params)
        self.set_btn.setStyleSheet(
            "font-size: 20px; color: black;"
            "border: 2px solid black; border-radius: 10px;"
            "background-color: white;"
            "border-image: none;"
            "transition: background-color 0.3s;"  # 使过渡更平滑(optional)  
            "}"
            "QPushButton:hover {"
            "background-color: pink;"  # 鼠标悬停时背景变为粉色  
            "}"
        )

        # 查看全局状态按钮
        self.view_status_btn = QPushButton("查看全局状态", self)
        self.view_status_btn.setGeometry(30, 510, 200, 50)
        self.view_status_btn.clicked.connect(self.view_global_status)
        self.view_status_btn.setStyleSheet(
            "font-size: 20px; color: black;"
            "border: 2px solid black; border-radius: 10px;"
            "background-color: white;"
            "border-image: none;"
            "transition: background-color 0.3s;"  # 使过渡更平滑(optional)  
            "}"
            "QPushButton:hover {"
            "background-color: pink;"  # 鼠标悬停时背景变为粉色  
            "}"
        )

        # 导出账单按钮
        self.export_bill_btn = QPushButton("导出账单", self)
        self.export_bill_btn.setGeometry(220, 20, 200, 50)
        self.export_bill_btn.clicked.connect(self.export_bills)
        self.export_bill_btn.setStyleSheet(
            "font-size: 25px; color: black;"
            "border: 2px solid black; border-radius: 10px;"
            "background-color: white;"
            "border-image: none;"
            "transition: background-color 0.3s;"  # 使过渡更平滑(optional)  
            "}"
            "QPushButton:hover {"
            "background-color: pink;"  # 鼠标悬停时背景变为粉色  
            "}"
        )

        # 导出详单按钮
        self.export_detail_btn = QPushButton("导出详单", self)
        self.export_detail_btn.setGeometry(450, 20, 200, 50)
        self.export_detail_btn.clicked.connect(self.export_details)
        self.export_detail_btn.setStyleSheet(
            "font-size: 25px; color: black;"
            "border: 2px solid black; border-radius: 10px;"
            "background-color: white;"
            "border-image: none;"
            "transition: background-color 0.3s;"  # 使过渡更平滑(optional)  
            "}"
            "QPushButton:hover {"
            "background-color: pink;"  # 鼠标悬停时背景变为粉色  
            "}"
        )

        # 打印调度记录按钮
        self.print_schedule_btn = QPushButton("打印调度记录", self)
        self.print_schedule_btn.setGeometry(500, 510, 200, 50)
        self.print_schedule_btn.clicked.connect(self.print_schedule_log)
        self.print_schedule_btn.setStyleSheet(
            "font-size: 25px; color: black;"
            "border: 2px solid black; border-radius: 10px;"
            "background-color: white;"
            "border-image: none;"
            "transition: background-color 0.3s;"  # 使过渡更平滑(optional)  
            "}"
            "QPushButton:hover {"
            "background-color: pink;"  # 鼠标悬停时背景变为粉色  
            "}"
        )

        # 空调状态表格
        self.table = QTableWidget(self)
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels(['RoomId', 'RoomTemp', 'Power', 'TargetTemp', 'WindSpeed', 'Mode', 'Sweep', 'Cost', 'TotalCost', 'Status', 'TimeSlice'])
        self.table.setGeometry(800, 50, 375, 500)

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
            if d.get("code") == 0:
                QMessageBox.information(self, "成功", d.get("message", "设置成功"))
            else:
                QMessageBox.critical(self, "错误", d.get("message", "设置失败"))
        else:
            QMessageBox.critical(self, "错误", f"设置失败 {res.status_code if res else '无响应'}")

    def view_global_status(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        res = get_json("/aircon/status", headers=headers)
        if res and res.status_code == 200:
            data = res.json()
            if data.get("code") == 0:
                ac_states = data.get("data", [])
                status_info = ""
                for state in ac_states:
                    # 修改 'temperature' 为 'targetTemperature'
                    status_info += (f"房间 {state.get('roomId', '')}:\n"
                                    f"  当前温度: {state.get('roomTemperature', 'N/A')}°C\n"
                                    f"  电源: {state.get('power', 'N/A')}\n"
                                    f"  目标温度: {state.get('targetTemperature', 'N/A')}°C\n"
                                    f"  风速: {state.get('windSpeed', 'N/A')}\n"
                                    f"  模式: {state.get('mode', 'N/A')}\n"
                                    f"  扫风: {state.get('sweep', 'N/A')}\n"
                                    f"  当前费用: {state.get('cost', 'N/A')}元\n"
                                    f"  累计费用: {state.get('totalCost', 'N/A')}元\n"
                                    f"  状态: {state.get('status', 'N/A')}\n\n")
                QMessageBox.information(self, "全局状态", status_info)
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
                        housing_cost = room.get("cost", 0)
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
            
import sys
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 在这里传入 token（这里假设是一个有效的 token 字符串）
    token = "your_token_here"  # 你可以将 token 从其他地方传递进来

    # 创建并显示界面
    ac_manager = AcManagerPanel(token)
    ac_manager.show()

    # 启动事件循环
    sys.exit(app.exec_())
