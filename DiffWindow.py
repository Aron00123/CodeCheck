from PyQt5.QtWidgets import QTextEdit, QHBoxLayout, QWidget, QMainWindow


class DiffWindow(QMainWindow):
    def __init__(self, parent, highlighted_content1: str, highlighted_content2: str):
        super().__init__(parent)
        self.setGeometry(400, 400, 2000, 1000)
        self.setWindowTitle('Code Comparison')

        diff_text_edit1 = QTextEdit(self)
        diff_text_edit1.setHtml(highlighted_content1)
        diff_text_edit1.setReadOnly(True)

        diff_text_edit2 = QTextEdit(self)
        diff_text_edit2.setHtml(highlighted_content2)
        diff_text_edit2.setReadOnly(True)

        layout = QHBoxLayout()
        layout.addWidget(diff_text_edit1)
        layout.addWidget(diff_text_edit2)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.show()
