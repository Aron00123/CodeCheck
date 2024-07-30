import datetime

from PyQt5.QtGui import QIcon

from RegisterDialog import load_user_data
from MainWindow import MainWindow
from RegisterDialog import RegisterDialog
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLineEdit, QLabel, QVBoxLayout, QWidget, QVBoxLayout, QPushButton, QMessageBox

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # setGeometry(x, y, w, h)
        # 其中 (x, y) 是窗口的左上角坐标（不包括窗框！）
        self.setGeometry(200, 200, 500, 0)
        self.setWindowTitle('Login')
        self.setWindowIcon(QIcon("icon.png"))

        layout = QVBoxLayout()

        self.label_username = QLabel('Enter your username:', self)
        self.username = QLineEdit(self)
        self.label_password = QLabel('Enter your password:', self)
        self.password = QLineEdit(self)
        self.password.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton('Login', self)
        self.login_button.clicked.connect(self.handle_login)

        self.register_button = QPushButton('Register', self)
        self.register_button.clicked.connect(self.handle_register)

        layout.addWidget(self.label_username)
        layout.addWidget(self.username)
        layout.addWidget(self.label_password)
        layout.addWidget(self.password)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def handle_login(self):
        username = self.username.text().strip()
        password = self.password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, 'Error', 'Username and password cannot be empty')
            return

        user_data = load_user_data()
        if username in user_data and user_data[username] == password:
            login_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f'User {username} logged in at {login_time}')
            self.main_window = MainWindow(username, login_time)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(self, 'Error', 'Invalid username or password')

    def handle_register(self):
        dialog = RegisterDialog(self)
        dialog.exec_()