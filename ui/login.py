# login.py
from PyQt5.QtWidgets import QDialog, QLineEdit, QLabel, QPushButton, QVBoxLayout, QMessageBox
from common import post_json

class LoginDialog(QDialog):
    def __init__(self, role, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{role} 登录")
        self.role = role
        self.token = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 用户名标签和输入框
        self.username_label = QLabel("用户名:", self)
        self.username_label.setStyleSheet("font-size: 18px;")
        layout.addWidget(self.username_label)

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("请输入用户名")
        layout.addWidget(self.username_input)

        # 密码标签和输入框
        self.password_label = QLabel("密码:", self)
        self.password_label.setStyleSheet("font-size: 18px;")
        layout.addWidget(self.password_label)

        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("请输入密码")
        layout.addWidget(self.password_input)

        # 登录按钮
        self.login_btn = QPushButton("登录", self)
        self.login_btn.clicked.connect(self.login)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        # 使用POST进行登录
        res = post_json("/admin/login", {"username": username, "password": password})
        if res and res.status_code == 200:
            data = res.json()
            if data.get("code") == 0:
                server_role = data.get("role")
                if server_role == self.role:
                    self.token = data["token"]
                    QMessageBox.information(self, "成功", "登录成功")
                    self.accept()
                else:
                    QMessageBox.critical(self, "错误", f"角色不匹配: 服务器返回 {server_role}")
            else:
                QMessageBox.critical(self, "错误", data.get("message", "登录失败"))
        else:
            QMessageBox.critical(self, "错误", f"登录失败: HTTP {res.status_code if res else '无响应'}")
