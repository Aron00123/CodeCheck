import sys
import os
import ast
from difflib import SequenceMatcher
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QLabel, QVBoxLayout, QWidget, QFileDialog, QListWidget, QTextEdit

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
        print(f'User {username} logged in')
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Code Duplication Checker')
        self.setGeometry(100, 100, 800, 600)

        self.import_button = QPushButton('Import Code Files', self)
        self.import_button.clicked.connect(self.import_files)
        self.import_button.move(50, 50)

        self.result_list = QListWidget(self)
        self.result_list.move(50, 100)
        self.result_list.resize(700, 400)
        self.result_list.itemClicked.connect(self.view_details)

        self.statusBar().showMessage('Ready')

    def import_files(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Import Code Files", "", "Python Files (*.py);;All Files (*)", options=options)
        if len(files) >= 2:
            self.check_duplication(files)
        else:
            self.statusBar().showMessage('Please select at least 2 files')

    def check_duplication(self, files):
        duplicates = []
        for i in range(len(files)):
            for j in range(i + 1, len(files)):
                content1 = read_file(files[i])
                content2 = read_file(files[j])
                overall_similarity = calculate_overall_similarity(content1.splitlines(), content2.splitlines())
                # if overall_similarity > 0.8:  # Assuming 80% similarity as duplicate
                #     duplicates.append((files[i], files[j], overall_similarity))
                duplicates.append((files[i], files[j], overall_similarity))
        self.display_results(duplicates)

    def display_results(self, duplicates):
        self.result_list.clear()
        print(duplicates)
        for file1, file2, similarity in duplicates:
            self.result_list.addItem(f'{file1} and {file2} are {similarity * 100:.2f}% similar')

    def view_details(self, item):
        files = item.text().split(' and ')
        file1, file2 = files[0], files[1].split(' ')[0]
        content1 = read_file(file1)
        content2 = read_file(file2)
        similar_blocks, lines1, lines2 = find_similar_blocks(content1, content2)
        extended_blocks = []
        for block1_idx, block2_idx, similarity in similar_blocks:
            length1, length2 = try_expand_block(lines1, lines2, block1_idx, block2_idx, 0.9)
            length = min(length1, length2)
            extended_blocks.append((block1_idx, block2_idx, length))
        highlighted_content1, highlighted_content2 = highlight_code(content1, content2, extended_blocks, lines1, lines2)
        self.show_diff(highlighted_content1, highlighted_content2)

    def show_diff(self, highlighted_content1, highlighted_content2):
        diff_window = QMainWindow(self)
        diff_window.setWindowTitle('Code Comparison')
        diff_window.setGeometry(150, 150, 600, 400)

        diff_text_edit1 = QTextEdit(diff_window)
        diff_text_edit1.setHtml(highlighted_content1)
        diff_text_edit1.setReadOnly(True)

        diff_text_edit2 = QTextEdit(diff_window)
        diff_text_edit2.setHtml(highlighted_content2)
        diff_text_edit2.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(diff_text_edit1)
        layout.addWidget(diff_text_edit2)
        container = QWidget()
        container.setLayout(layout)
        diff_window.setCentralWidget(container)

        diff_window.show()

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def node_to_string(node):
    return ast.dump(node)

def calculate_node_similarity(block1, block2):
    return SequenceMatcher(None, block1, block2).ratio()

def find_similar_blocks(content1, content2, threshold=0.9):
    lines1 = content1.splitlines()
    lines2 = content2.splitlines()

    similar_blocks = []
    used_blocks2 = set()

    for i, line1 in enumerate(lines1):
        best_match = None
        best_similarity = 0
        for j, line2 in enumerate(lines2):
            if j in used_blocks2:
                continue
            similarity = calculate_node_similarity(line1, line2)
            if similarity >= threshold and similarity > best_similarity:
                best_similarity = similarity
                best_match = j
        if best_match is not None:
            similar_blocks.append((i, best_match, best_similarity))
            used_blocks2.add(best_match)

    return similar_blocks, lines1, lines2

def try_expand_block(lines1, lines2, block1_start, block2_start, threshold):
    block1_end = block1_start + 1
    block2_end = block2_start + 1

    while block1_end < len(lines1) and block2_end < len(lines2):
        block1 = "\n".join(lines1[block1_start:block1_end + 1])
        block2 = "\n".join(lines2[block2_start:block2_end + 1])

        similarity = calculate_node_similarity(block1, block2)
        if similarity >= threshold:
            block1_end += 1
            block2_end += 1
        else:
            break

    return block1_end - block1_start, block2_end - block2_start

def highlight_code(content1, content2, similar_blocks, lines1, lines2):
    highlighted_lines1 = lines1[:]
    highlighted_lines2 = lines2[:]

    for block1_idx, block2_idx, length in similar_blocks:
        for i in range(block1_idx, block1_idx + length):
            highlighted_lines1[i] = f'<span style="background-color: yellow">{lines1[i]}</span>'
        for i in range(block2_idx, block2_idx + length):
            highlighted_lines2[i] = f'<span style="background-color: yellow">{lines2[i]}</span>'

    return '<br>'.join(highlighted_lines1), '<br>'.join(highlighted_lines2)

def calculate_overall_similarity(lines1, lines2):
    similarities = []

    for line1 in lines1:
        best_similarity = 0
        for line2 in lines2:
            similarity = calculate_node_similarity(line1, line2)
            if similarity > best_similarity:
                best_similarity = similarity
        similarities.append(best_similarity)

    return sum(similarities) / len(similarities)

def main():
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()