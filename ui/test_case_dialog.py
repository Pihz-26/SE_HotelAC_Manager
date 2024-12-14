# frontend/test_case_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QMessageBox
from PyQt5.QtCore import Qt

class TestCaseDialog(QDialog):
    def __init__(self, role, parent=None):
        super().__init__(parent)
        self.setWindowTitle("测试用例设置")
        self.role = role
        self.selected_rooms = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        if self.role in ["空调管理", "酒店经理"]:
            label = QLabel("请选择要启动的客房:")
            layout.addWidget(label)
            self.room_list = QListWidget()
            for i in range(1, 6):
                item = QListWidgetItem(f"客房{i}")
                item.setCheckState(Qt.Unchecked)
                self.room_list.addItem(item)
            layout.addWidget(self.room_list)
        elif self.role == "前台服务":
            label = QLabel("请选择要启动的两个客房:")
            layout.addWidget(label)
            self.room_list = QListWidget()
            for i in range(1, 6):
                item = QListWidgetItem(f"客房{i}")
                item.setCheckState(Qt.Unchecked)
                self.room_list.addItem(item)
            layout.addWidget(self.room_list)
        else:
            QMessageBox.critical(self, "错误", "未知角色")
            self.reject()
            return

        start_btn = QPushButton("开始")
        start_btn.clicked.connect(self.start_test_case)
        layout.addWidget(start_btn)

        self.setLayout(layout)

    def start_test_case(self):
        selected = []
        for index in range(self.room_list.count()):
            item = self.room_list.item(index)
            if item.checkState() == Qt.Checked:
                selected.append(item.text())
        if self.role in ["空调管理", "酒店经理"]:
            if not selected:
                QMessageBox.warning(self, "警告", "请至少选择一个客房")
                return
            self.selected_rooms = selected
            self.accept()
        elif self.role == "前台服务":
            if len(selected) != 2:
                QMessageBox.warning(self, "警告", "请准确选择两个客房")
                return
            self.selected_rooms = selected
            self.accept()
