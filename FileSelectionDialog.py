from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget, QDialog, QScrollArea, QVBoxLayout, QHBoxLayout, QDialog, \
    QRadioButton, QCheckBox, QPushButton, QSizePolicy


class FileSelectionDialog(QDialog):
    def __init__(self, files, parent=None):
        super().__init__(parent)
        self.files = files
        self.selected_base_files = []  # Changed to list for multiple selections
        self.selected_compare_files = []

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Select Files for Comparison')
        self.setWindowIcon(QIcon("icon.png"))

        layout = QVBoxLayout()

        scroll_area = QScrollArea(self)
        scroll_content = QWidget()
        scroll_layout = QHBoxLayout(scroll_content)

        self.base_file_buttons = []
        self.compare_file_buttons = []

        base_file_layout = QVBoxLayout()
        compare_file_layout = QVBoxLayout()

        for file in self.files:
            base_check = QCheckBox(file)  # Changed to QCheckBox
            base_check.stateChanged.connect(self.on_base_file_selected)  # Changed to stateChanged
            self.base_file_buttons.append(base_check)
            base_file_layout.addWidget(base_check)

            compare_check = QCheckBox(file)
            compare_check.stateChanged.connect(self.on_compare_file_selected)
            self.compare_file_buttons.append(compare_check)
            compare_file_layout.addWidget(compare_check)

        scroll_layout.addLayout(base_file_layout)
        scroll_layout.addLayout(compare_file_layout)

        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True)

        layout.addWidget(scroll_area)

        ok_button = QPushButton('                                                                OK                                                                ', self)
        ok_button.clicked.connect(self.on_ok)
        layout.addWidget(ok_button)

        self.setLayout(layout)

    def on_base_file_selected(self):
        check_box = self.sender()
        if check_box.isChecked():
            self.selected_base_files.append(check_box.text())
        else:
            self.selected_base_files.remove(check_box.text())

    def on_compare_file_selected(self):
        check_box = self.sender()
        if check_box.isChecked():
            self.selected_compare_files.append(check_box.text())
        else:
            self.selected_compare_files.remove(check_box.text())

    def on_ok(self):
        self.accept()