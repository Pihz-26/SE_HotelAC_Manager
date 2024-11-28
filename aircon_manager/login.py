# login.py
import sys
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
import requests
from request_body import AdminLoginRequest

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("管理员登录")
        self.setFixedSize(300, 150)
        self.admin_token = ""

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("用户名")
        layout.addWidget(self.username_edit)

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("密码")
        self.password_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_edit)

        login_button = QPushButton("登录")
        login_button.clicked.connect(self.login)
        layout.addWidget(login_button)

        self.setLayout(layout)

    def login(self):
        username = self.username_edit.text()
        password = self.password_edit.text()

        if not username or not password:
            QMessageBox.warning(self, "输入错误", "请输入用户名和密码")
            return

        login_data = AdminLoginRequest(username=username, password=password)
        url = "http://127.0.0.1:8000/admin/login"

        try:
            response = requests.post(url, json=login_data.dict())
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "网络错误", str(e))
            return

        data = response.json()
        if data.get("code") == 0:
            self.admin_token = data.get("token", "")
            QMessageBox.information(self, "成功", "登录成功")
            self.accept()
        else:
            QMessageBox.warning(self, "登录失败", data.get("message", "未知错误"))
