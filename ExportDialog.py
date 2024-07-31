from PyQt5.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QDialogButtonBox


class FileSelectionDialog2(QDialog):
    def __init__(self, files, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Select Files to Export')
        self.layout = QVBoxLayout(self)
        self.checkboxes = []

        for file in files:
            checkbox = QCheckBox(file, self)
            self.layout.addWidget(checkbox)
            self.checkboxes.append(checkbox)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def preselect_files(self, files_to_preselect: set):
        for checkbox in self.checkboxes:
            if checkbox.text() in files_to_preselect:
                checkbox.setChecked(True)

    def selected_files(self):
        return [checkbox.text() for checkbox in self.checkboxes if checkbox.isChecked()]
