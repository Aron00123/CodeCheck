import sys
from LoginWindow import LoginWindow
from PyQt5.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()