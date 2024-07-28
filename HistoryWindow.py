import json
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QListWidget

class HistoryWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.initUI()

    def initUI(self):
        self.setWindowTitle('History')
        self.setGeometry(150, 150, 600, 400)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        self.history_list = QListWidget(self)
        layout.addWidget(self.history_list)

        self.load_history()

        self.setCentralWidget(central_widget)

    def load_history(self):
        try:
            with open('history.json', 'r') as file:
                history = json.load(file)
                if self.username in history:
                    for record in history[self.username]:
                        for file in record['compare_files']:
                            self.history_list.addItem(f"{record['timestamp']} - Base: {record['base_file']} - Compare: {file}")
        except FileNotFoundError:
            pass

    def view_history_details(self, item):
        # Implement this method to show the detailed comparison for the selected history record
        pass