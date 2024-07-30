import json
import ast
import astor
from difflib import SequenceMatcher

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QListWidget, QTextEdit, QListWidgetItem, QLabel

import Constants
from DiffWindow import DiffWindow


class HistoryWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.initUI()

    def initUI(self):
        self.setMinimumHeight(400)
        self.setWindowTitle('History')
        self.setWindowIcon(QIcon("icon.png"))

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        layout.addWidget(QLabel('Timestamp | Base | Compare | Similarity                                                                                    '))

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
                        similarity = f'{record['similarity'] * 100:.2f}%'
                        item = QListWidgetItem(
                            f"{record['timestamp']} | {record['base_file']} | {record['compare_file']} | {similarity}",
                            self.history_list
                        )
                        if record['similarity'] > Constants.SUS_THRESHOLD:
                            item.setBackground(Qt.red)
        except FileNotFoundError:
            pass

    def view_history_details(self, item):
        # 'Timestamp | Base | Compare | Similarity'
        record = item.text().split(' | ')
        base_file = record[1]
        compare_file = record[2]
        content1 = read_file(base_file)
        content2 = read_file(compare_file)
        similar_blocks, lines1, lines2 = find_similar_blocks(content1, content2)
        highlighted_content1, highlighted_content2 = highlight_code(content1, content2, similar_blocks, lines1, lines2)
        self.show_diff(highlighted_content1, highlighted_content2)

    def show_diff(self, highlighted_content1, highlighted_content2):
        DiffWindow(self, highlighted_content1, highlighted_content2)

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def normalize_variable_names(node):
    class VariableNameNormalizer(ast.NodeTransformer):
        def __init__(self):
            self.variable_map = {}
            self.counter = 0

        def get_new_name(self, original_name):
            if original_name not in self.variable_map:
                self.counter += 1
                self.variable_map[original_name] = f"var{self.counter}"
            return self.variable_map[original_name]

        def visit_Name(self, node):
            if isinstance(node.ctx, ast.Store) or isinstance(node.ctx, ast.Load):
                new_name = self.get_new_name(node.id)
                return ast.copy_location(ast.Name(id=new_name, ctx=node.ctx), node)
            return node

        def visit_arg(self, node):
            new_name = self.get_new_name(node.arg)
            return ast.copy_location(ast.arg(arg=new_name, annotation=node.annotation), node)

    return VariableNameNormalizer().visit(node)

def node_to_string(node):
    return astor.to_source(node)

def calculate_node_similarity(block1, block2):
    return SequenceMatcher(None, block1, block2).ratio()

def ast_similarity(node1, node2):
    normalized_node1 = normalize_variable_names(node1)
    normalized_node2 = normalize_variable_names(node2)
    return calculate_node_similarity(node_to_string(normalized_node1), node_to_string(normalized_node2))

def find_similar_blocks(content1, content2, threshold=0.9):
    tree1 = ast.parse(content1)
    tree2 = ast.parse(content2)

    blocks1 = [node for node in ast.walk(tree1) if isinstance(node, ast.stmt)]
    blocks2 = [node for node in ast.walk(tree2) if isinstance(node, ast.stmt)]

    similar_blocks = []
    used_blocks2 = set()

    for i, line1 in enumerate(blocks1):
        best_match = None
        best_similarity = 0
        for j, line2 in enumerate(blocks2):
            if j in used_blocks2:
                continue
            similarity = ast_similarity(line1, line2)
            if similarity >= threshold and similarity > best_similarity:
                best_similarity = similarity
                best_match = j
        if best_match is not None:
            similar_blocks.append((i, best_match, best_similarity))
            used_blocks2.add(best_match)

    return similar_blocks, blocks1, blocks2

def highlight_code(content1, content2, similar_blocks, blocks1, blocks2):
    lines1 = content1.splitlines()
    lines2 = content2.splitlines()
    highlighted_lines1 = lines1[:]
    highlighted_lines2 = lines2[:]

    for block1_idx, block2_idx, length in similar_blocks:
        block1 = blocks1[block1_idx]
        block2 = blocks2[block2_idx]

        for i in range(block1.lineno - 1, block1.end_lineno):
            if not lines1[i].strip().startswith("#"):
                highlighted_lines1[i] = f'<span style="background-color: yellow">{lines1[i]}</span>'
        for i in range(block2.lineno - 1, block2.end_lineno):
            if not lines2[i].strip().startswith("#"):
                highlighted_lines2[i] = f'<span style="background-color: yellow">{lines2[i]}</span>'

    return '<br>'.join(highlighted_lines1), '<br>'.join(highlighted_lines2)