# occupant_panel.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox, QHBoxLayout
)
from common import post_json, get_json
from urllib.parse import urlencode

class OccupantPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("住户空调控制面板 (Occupant AC Control)")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 输入房间号
        h1 = QHBoxLayout()
        h1.addWidget(QLabel("房间号："))
        self.room_input = QLineEdit()
        h1.addWidget(self.room_input)
        layout.addLayout(h1)

        # 获取空调状态按钮
        self.get_panel_btn = QPushButton("获取空调状态")
        self.get_panel_btn.clicked.connect(self.get_panel_info)
        layout.addWidget(self.get_panel_btn)

        self.status_label = QLabel("空调面板信息将在这里显示...")
        layout.addWidget(self.status_label)

        # 电源设置
        layout.addWidget(QLabel("电源 (on/off):"))
        self.power_combo = QComboBox()
        self.power_combo.addItems(["on", "off"])
        layout.addWidget(self.power_combo)

        # 目标温度设置
        layout.addWidget(QLabel("目标温度:"))
        self.temp_input = QLineEdit("25")
        layout.addWidget(self.temp_input)

        # 风速设置
        layout.addWidget(QLabel("风速 (低/中/高):"))
        self.wind_combo = QComboBox()
        self.wind_combo.addItems(["低", "中", "高"])
        layout.addWidget(self.wind_combo)

        # 扫风设置
        layout.addWidget(QLabel("扫风 (开/关):"))
        self.sweep_combo = QComboBox()
        self.sweep_combo.addItems(["开", "关"])
        layout.addWidget(self.sweep_combo)

        # 设置空调按钮
        self.set_btn = QPushButton("设置空调")
        self.set_btn.clicked.connect(self.set_ac_control)
        layout.addWidget(self.set_btn)

        self.setLayout(layout)

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
                    self.status_label.setText(info)
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
                QMessageBox.information(self, "成功", "设置成功")
                self.get_panel_info()  # 刷新状态
            else:
                QMessageBox.critical(self, "错误", d.get("message", "设置失败"))
        else:
            QMessageBox.critical(self, "错误", f"设置失败: {res.status_code if res else '无响应'}")
