import ctypes
import sys
from LoginWindow import LoginWindow
from PyQt5.QtWidgets import QApplication

def main():
    # 为程序设置独立的 ID，让任务栏图标能够正常显示
    # https://stackoverflow.com/a/1552105/20025220
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('codecheck')
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()