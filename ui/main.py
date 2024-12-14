# main.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QComboBox, QPushButton, QVBoxLayout,
    QMessageBox, QDialog, QCheckBox, QHBoxLayout
)
from login import LoginDialog
from ac_manager_panel import AcManagerPanel
from manager_panel import ManagerPanel
from front_desk_panel import FrontDeskPanel
from occupant_panel import OccupantPanel
from client_panel import ClientPanel

class TestCaseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("运行测试用例")
        self.selected_mode = None
        self.selected_rooms = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 选择模式：服务器端或客户端
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("选择模式:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["服务器端", "客户端"])
        mode_layout.addWidget(self.mode_combo)
        layout.addLayout(mode_layout)

        # 选择房间
        layout.addWidget(QLabel("选择要启动的客房:"))
        self.room_checkboxes = []
        for i in range(1, 6):
            checkbox = QCheckBox(f"客房{i}")
            self.room_checkboxes.append(checkbox)
            layout.addWidget(checkbox)

        # 确认按钮
        run_btn = QPushButton("运行")
        run_btn.clicked.connect(self.run_test_case)
        layout.addWidget(run_btn)

        self.setLayout(layout)

    def run_test_case(self):
        mode = self.mode_combo.currentText()
        selected_rooms = [cb.text() for cb in self.room_checkboxes if cb.isChecked()]

        if mode == "服务器端":
            if not selected_rooms:
                QMessageBox.critical(self, "错误", "请选择至少一个客房作为服务器端")
                return
            # 这里假设服务器端启动相应的客房功能
            for room in selected_rooms:
                room_id = int(room.replace("客房", ""))
                self.parent().start_server_room(room_id)
        elif mode == "客户端":
            if len(selected_rooms) != 2:
                QMessageBox.critical(self, "错误", "客户端模式必须选择两个客房")
                return
            for room in selected_rooms:
                room_id = int(room.replace("客房", ""))
                self.parent().start_client_room(room_id)
        else:
            QMessageBox.critical(self, "错误", "未知模式")
            return

        QMessageBox.information(self, "成功", "测试用例已启动")
        self.accept()

class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("系统主入口")
        self.init_ui()
        self.server_clients = {}
        self.client_windows = {}

    def init_ui(self):
        layout = QVBoxLayout()

        # 角色选择部分（需要登录）
        layout.addWidget(QLabel("请选择需要登录的角色："))
        self.role_combo = QComboBox()
        # 这里放置需要登录的角色：空调管理, 经理, 前台服务
        self.role_combo.addItems(["空调管理", "酒店经理", "前台服务"])
        layout.addWidget(self.role_combo)

        login_btn = QPushButton("登录")
        login_btn.clicked.connect(self.login_role)
        layout.addWidget(login_btn)

        # occupant 无需登录进入
        occupant_btn = QPushButton("进入住户空调控制面板 (无需登录)")
        occupant_btn.clicked.connect(self.open_occupant_panel)
        layout.addWidget(occupant_btn)

        # 启动房间客户端(如需测试)
        start_clients_btn = QPushButton("启动房间客户端")
        start_clients_btn.clicked.connect(self.start_clients)
        layout.addWidget(start_clients_btn)

        # 运行测试用例
        test_case_btn = QPushButton("运行测试用例")
        test_case_btn.clicked.connect(self.run_test_case)
        layout.addWidget(test_case_btn)

        self.setLayout(layout)

    def login_role(self):
        role = self.role_combo.currentText()
        dlg = LoginDialog(role=role)
        if dlg.exec_():
            token = dlg.token
            print(token)
            if role == "空调管理":
                self.ac_manager_window = AcManagerPanel(token)
                self.ac_manager_window.show()
            elif role == "酒店经理":
                self.manager_window = ManagerPanel(token)
                self.manager_window.show()
            elif role == "前台服务":
                self.front_desk_window = FrontDeskPanel(token)
                self.front_desk_window.show()
            else:
                QMessageBox.critical(self, "错误", "未知角色")

    def open_occupant_panel(self):
        # occupant无需登录
        self.occupant_window = OccupantPanel()
        self.occupant_window.show()

    def start_clients(self):
        # 当作为客户端时，可启动两个房间的客户端进行测试
        # 如果后端要求权限，请先用相应角色登录获取token，这里简化为使用空token
        token = ""
        for room_id in [1, 2]:
            if room_id not in self.client_windows:
                self.client_windows[room_id] = ClientPanel(room_id=room_id, token=token, scenario_mode="cold")
                self.client_windows[room_id].show()

    def run_test_case(self):
        dlg = TestCaseDialog(self)
        dlg.exec_()

    def start_server_room(self, room_id):
        # 作为服务器端启动某个房间的功能
        # 这里可以根据实际需求启动相关功能
        if room_id not in self.server_clients:
            self.server_clients[room_id] = ClientPanel(room_id=room_id, token="", scenario_mode="cold")
            self.server_clients[room_id].show()

    def start_client_room(self, room_id):
        # 作为客户端启动某个房间的功能
        if room_id not in self.client_windows:
            self.client_windows[room_id] = ClientPanel(room_id=room_id, token="", scenario_mode="cold")
            self.client_windows[room_id].show()

def main():
    app = QApplication(sys.argv)
    w = MainApp()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
