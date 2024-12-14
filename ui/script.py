import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QComboBox, QPushButton, QVBoxLayout,
    QMessageBox, QDialog, QCheckBox, QHBoxLayout
)
from main import *


def create_ui(number):
    w = MainApp()
    w.setWindowTitle(f"空调管理系统 - 窗口 {number}")
    w.occupant_btn.click()
    w.occupant_window.room_input.setText(str(2000+number))
    if number == 1:
        w.occupant_window.process1_btn.click()
    elif number == 2: 
        w.occupant_window.process2_btn.click()
    elif number == 3:
        w.occupant_window.process3_btn.click()    
    elif number == 4:
        w.occupant_window.process4_btn.click()
    elif number == 5:
        w.occupant_window.process5_btn.click()
    
    print(number)
    return w
    
  
def create_uis():
    app = QApplication(sys.argv)
    windows = []
    for i in range(5):
        window = create_ui(i+1)
        windows.append(window)
        
    sys.exit(app.exec_())

    
        
    


create_uis()

    