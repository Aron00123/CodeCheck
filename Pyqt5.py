import ctypes
import sys
import platform

from PyQt5 import QtWidgets, QtCore

from LoginWindow import LoginWindow
from PyQt5.QtWidgets import QApplication

def main():
    # QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    # QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    # 为程序设置独立的 ID，让任务栏图标能够正常显示
    # https://stackoverflow.com/a/1552105/20025220
    if platform.system() == 'Windows':
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('codecheck')

    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()