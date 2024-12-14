# frontend/login.py
from PyQt5.QtWidgets import QDialog,QWidget, QLineEdit, QLabel, QPushButton, QVBoxLayout, QMessageBox
from common import post_json

class LoginDialog(QDialog):
    def __init__(self, role, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{role} 登录")
        self.setGeometry(700, 200, 800, 597)
        self.role = role
        self.token = None
        # 背景层
        self.background_widget = QLabel(self)
        self.background_widget.setGeometry(0, 0, 800, 597)
        self.background_widget.setStyleSheet("border-image: url('image/登录.png');")

        # 控件层
        self.widget_layer = QWidget(self)
        self.widget_layer.setGeometry(0, 0, 800, 597)

        self.init_ui()

    def init_ui(self):

        # 用户名标签和输入框
        self.username_label = QLabel("用户名:", self)
        self.username_label.setGeometry(520, 110,200, 60)  # 设置位置 (x, y) 和大小 (width, height)
        self.username_label.setStyleSheet("font-size: 35px; color: black;border-image:none")

        self.username_input = QLineEdit(self)
        self.username_input.setGeometry(520, 180, 200, 50)  # 设置输入框的位置和大小
        self.username_input.setStyleSheet("""  
                    QLineEdit {  
                        border: 2px solid gray;  
                        border-radius: 10px;   
                        padding: 5px;  
                        background-color: #f9f9f9;  
                        font-size: 25px; 
                        border-image:none 
                    }  
                    QLineEdit:focus {  
                        border: 2px solid #4682B4; 
                        border-image:none 
                    }  
                """)

        # 密码标签和输入框
        self.password_label = QLabel("密码:", self)
        self.password_label.setGeometry(520, 245, 200, 60)  # 设置位置和大小
        self.password_label.setStyleSheet("font-size: 35px; color: black;border-image:none")

        self.password_input = QLineEdit(self)
        self.password_input.setGeometry(520, 310, 200, 50)  # 设置输入框的位置和大小
        self.password_input.setEchoMode(QLineEdit.Password)  # 密码模式
        self.password_input.setStyleSheet("""  
                    QLineEdit {  
                        border: 2px solid gray;  
                        border-radius: 10px;   
                        padding: 5px;  
                        background-color: #f9f9f9;  
                        font-size: 25px; 
                        border-image:none 
                    }  
                    QLineEdit:focus {  
                        border: 2px solid #4682B4; 
                        border-image:none 
                    }  
                """)

        # 登录按钮
        self.login_btn = QPushButton("登录", self)
        self.login_btn.setGeometry(500, 405,180, 55)  # 设置按钮的位置和大小
        self.login_btn.clicked.connect(self.login)  # 将按钮和登录逻辑绑定
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

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        if not username or not password:
            QMessageBox.critical(self, "错误", "用户名和密码不能为空")
            return
        # 使用POST进行登录
        res = post_json("/admin/login", {"username": username, "password": password})
        if res and res.status_code == 200:
            data = res.json()
            if data.get("code") == 0:
                server_role = data.get("role")
                if server_role == self.role:
                    self.token = data.get("token")
                    QMessageBox.information(self, "成功", "登录成功")
                    self.accept()
                else:
                    QMessageBox.critical(self, "错误", f"角色不匹配: 服务器返回 {server_role}")
            else:
                QMessageBox.critical(self, "错误", data.get("message", "登录失败"))
        else:
            QMessageBox.critical(self, "错误", f"登录失败: {res.status_code if res else '无响应'}")
