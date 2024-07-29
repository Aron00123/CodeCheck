import json
import ast
from difflib import SequenceMatcher
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QListWidget, QTextEdit

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
        self.history_list.itemClicked.connect(self.view_history_details)
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
        record = item.text().split(' - ')
        base_file = record[1].split(': ')[1]
        compare_file = record[2].split(': ')[1]
        content1 = read_file(base_file)
        content2 = read_file(compare_file)
        similar_blocks, lines1, lines2 = find_similar_blocks(content1, content2)
        extended_blocks = []
        for block1_idx, block2_idx, similarity in similar_blocks:
            length1, length2 = try_expand_block(lines1, lines2, block1_idx, block2_idx, 0.9)
            length = min(length1, length2)
            extended_blocks.append((block1_idx, block2_idx, length))
        highlighted_content1, highlighted_content2 = highlight_code(extended_blocks, lines1, lines2)
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

def highlight_code(similar_blocks, lines1, lines2):
    highlighted_lines1 = lines1[:]
    highlighted_lines2 = lines2[:]

    for block1_idx, block2_idx, length in similar_blocks:
        for i in range(block1_idx, block1_idx + length):
            highlighted_lines1[i] = f'<span style="background-color: yellow">{lines1[i]}</span>'
        for i in range(block2_idx, block2_idx + length):
            highlighted_lines2[i] = f'<span style="background-color: yellow">{lines2[i]}</span>'

    return '<br>'.join(highlighted_lines1), '<br>'.join(highlighted_lines2)