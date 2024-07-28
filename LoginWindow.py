import datetime
from MainWindow import MainWindow
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLineEdit, QLabel, QVBoxLayout, QWidget, QVBoxLayout, QPushButton

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Login')
        self.setGeometry(100, 100, 300, 200)

        self.label = QLabel('Enter your username:', self)
        self.username = QLineEdit(self)
        self.login_button = QPushButton('Login', self)
        self.login_button.clicked.connect(self.handle_login)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.username)
        layout.addWidget(self.login_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def handle_login(self):
        username = self.username.text()
        login_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f'User {username} logged in at {login_time}')
        self.main_window = MainWindow(login_time)
        self.main_window.show()
        self.close()