import json
import os
from PyQt5.QtWidgets import QDialog, QPushButton, QLineEdit, QLabel, QVBoxLayout, QVBoxLayout, QPushButton, QMessageBox

USER_DATA_FILE = 'user_data.json'

def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_user_data(user_data):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(user_data, file, indent=4)

class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Register')

        layout = QVBoxLayout()

        self.label_username = QLabel('Enter new username:     ', self)
        self.username = QLineEdit(self)
        self.label_password = QLabel('Enter new password:     ', self)
        self.password = QLineEdit(self)
        self.password.setEchoMode(QLineEdit.Password)

        self.register_button = QPushButton('Register', self)
        self.register_button.clicked.connect(self.handle_register)

        layout.addWidget(self.label_username)
        layout.addWidget(self.username)
        layout.addWidget(self.label_password)
        layout.addWidget(self.password)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    def handle_register(self):
        username = self.username.text().strip()
        password = self.password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, 'Error', 'Username and password cannot be empty')
            return

        user_data = load_user_data()
        if username in user_data:
            QMessageBox.warning(self, 'Error', 'Username already exists')
            return

        user_data[username] = password
        save_user_data(user_data)
        QMessageBox.information(self, 'Success', 'User registered successfully')
        self.accept()