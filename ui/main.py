# frontend/main.py
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QComboBox, QPushButton, QVBoxLayout,
                             QMessageBox)
from login import LoginDialog
from ac_manager_panel import AcManagerPanel
from manager_panel import ManagerPanel
from front_desk_panel import FrontDeskPanel
from occupant_panel import OccupantPanel
from client_panel import ClientPanel
from test_case_dialog import TestCaseDialog

class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("系统主入口")
        self.setGeometry(250, 100, 1400, 850)

        # 背景层
        self.background_widget = QLabel(self)
        self.background_widget.setGeometry(0, 0, 1400, 850)
        self.background_widget.setStyleSheet("border-image: url('image/首页背景6.png');")

        # 控件层
        self.widget_layer = QWidget(self)
        self.widget_layer.setGeometry(0, 0, 1400, 850)

        self.init_ui()
        self.token = None  # 全局Token

    def init_ui(self):
        # 设置角色选择标签
        self.role_label = QLabel("请选择需要登录的角色：", self)
        self.role_label.setGeometry(890, 230,300, 30)  # 设置位置 (x, y) 和大小 (宽, 高)
        self.role_label.setStyleSheet("font-size: 30px; color: black;border-image:none")

        # 设置角色选择下拉框
        self.role_combo = QComboBox(self)
        self.role_combo.addItems(["空调管理", "酒店经理", "前台服务"])
        self.role_combo.setGeometry(960, 280, 200, 50)  # 设置位置和大小
        self.role_combo.setStyleSheet("""  
                    QComboBox {  
                        font-size: 30px;  
                        border: 2px solid gray;  
                        border-radius: 8px;  
                        padding: 5px;  
                        background-color: #ffffff;  
                        border-image:none
                    }  
                    QComboBox QAbstractItemView {  
                        font-size: 25px;  
                        border-image:none
                    }  
                """)

        # 登录按钮
        self.login_btn = QPushButton("登录", self)
        self.login_btn.setGeometry(960, 370, 180, 55)  # 设置位置和大小
        self.login_btn.clicked.connect(self.login_role)
        # 样式表，用 :hover 改变背景
        self.login_btn.setStyleSheet(
            "font-size: 30px; color: black;"
            "border: 2px solid black; border-radius: 10px;"
            "background-color: white;"
            "border-image: none;"
            "transition: background-color 0.3s;"  # 使过渡更平滑(optional)  
            "}"
            "QPushButton:hover {"
            "background-color: pink;"  # 鼠标悬停时背景变为粉色  
            "}"
        )


        # 进入住户空调控制面板按钮
        self.occupant_btn = QPushButton("进入住户空调控制面板", self)
        self.occupant_btn.setGeometry(960, 455, 250, 55)  # 设置位置和大小
        self.occupant_btn.clicked.connect(self.open_occupant_panel)
        self.occupant_btn.setStyleSheet(
            "font-size: 23px; color: black;"
            "border: 2px solid black; border-radius: 10px;"
            "background-color: white;"
            "border-image: none;"
            "transition: background-color 0.3s;"  # 使过渡更平滑(optional)  
            "}"
            "QPushButton:hover {"
            "background-color: pink;"  # 鼠标悬停时背景变为粉色  
            "}"
        )

        # 启动房间客户端按钮
        self.start_clients_btn = QPushButton("启动房间客户端", self)
        self.start_clients_btn.setGeometry(960, 535, 200, 50)  # 设置位置和大小
        self.start_clients_btn.clicked.connect(self.start_clients)
        self.start_clients_btn.setStyleSheet(
            "font-size: 23px; color: black;"
            "border: 2px solid black; border-radius: 10px;"
            "background-color: white;"
            "border-image: none;"
            "transition: background-color 0.3s;"  # 使过渡更平滑(optional)  
            "}"
            "QPushButton:hover {"
            "background-color: pink;"  # 鼠标悬停时背景变为粉色  
            "}"
        )

    def login_role(self):
        role = self.role_combo.currentText()
        dlg = LoginDialog(role=role)
        if dlg.exec_():
            token = dlg.token
            self.token = token
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
        # 使用ac_manager的Token来认证
        if not self.token:
            QMessageBox.warning(self, "警告", "请先以空调管理或酒店经理角色登录以获取权限")
            return
        self.client1 = ClientPanel(room_id=1, token=self.token, scenario_mode="cold")
        self.client1.show()
        self.client2 = ClientPanel(room_id=2, token=self.token, scenario_mode="cold")
        self.client2.show()

    def open_test_case_dialog(self):
        role = self.role_combo.currentText()
        dlg = TestCaseDialog(role=role, parent=self)
        if dlg.exec_():
            selected_rooms = dlg.selected_rooms
            if role in ["空调管理", "酒店经理"]:
                # 作为服务器端，启动选择的房间
                for room in selected_rooms:
                    room_number = int(room.replace("客房", ""))
                    self.server_client = ClientPanel(room_id=room_number, token=self.token, scenario_mode="cold")
                    self.server_client.show()
                QMessageBox.information(self, "测试用例", "服务器端已启动所选客房")
            elif role == "前台服务":
                # 作为客户端，启动选择的两个房间
                for room in selected_rooms:
                    room_number = int(room.replace("客房", ""))
                    self.client = ClientPanel(room_id=room_number, token=self.token, scenario_mode="cold")
                    self.client.show()
                QMessageBox.information(self, "测试用例", "客户端已启动所选客房")
            else:
                QMessageBox.critical(self, "错误", "未知角色")

def main():
    app = QApplication(sys.argv)
    w = MainApp()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

