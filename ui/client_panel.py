# frontend/client_panel.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QTimer  # 从QtCore导入QTimer
from common import post_json
from scenario import get_actions_for_room
import json

class ClientPanel(QWidget):
    def __init__(self, room_id, token, scenario_mode="cold"):
        super().__init__()
        self.room_id = room_id
        self.token = token
        self.scenario_mode = scenario_mode
        self.setWindowTitle(f"房间 {room_id} 客户端")
        self.init_ui()
        self.actions = get_actions_for_room(room_id, scenario_mode)
        self.current_step = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.run_step)
        self.timer.start(10000)  # 每10秒模拟1分钟

    def init_ui(self):
        layout = QVBoxLayout()
        self.info_label = QLabel("等待中...")
        layout.addWidget(self.info_label)
        self.setLayout(layout)

    def run_step(self):
        if self.current_step < len(self.actions):
            action = self.actions[self.current_step]
            headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
            data = {**action, "roomId": int(self.room_id)}
            res = post_json("/aircon/control", data, headers=headers)
            if res and res.status_code == 200:
                d = res.json()
                if d.get("code") == 0:
                    self.info_label.setText(f"第{self.current_step + 1}步: 已执行操作 {json.dumps(action, ensure_ascii=False)}")
                else:
                    self.info_label.setText(f"执行失败: {d.get('message','未知错误')}")
            else:
                self.info_label.setText(f"请求失败: {res.status_code if res else '无响应'}")
            self.current_step += 1
        else:
            self.info_label.setText("测试完成")
            self.timer.stop()
