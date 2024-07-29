import ast
import astor
import json
import datetime
from difflib import SequenceMatcher
from FileSelectionDialog import FileSelectionDialog
from HistoryWindow import HistoryWindow
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QFileDialog, QListWidget, QTextEdit, QVBoxLayout, QPushButton

class MainWindow(QMainWindow):
    def __init__(self, username, login_time):
        super().__init__()
        self.username = username
        self.login_time = login_time
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Code Duplication Checker')
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        self.import_button = QPushButton('Import Code Files', self)
        self.import_button.clicked.connect(self.import_files)
        layout.addWidget(self.import_button)

        self.history_button = QPushButton('History', self)
        self.history_button.clicked.connect(self.show_history)
        layout.addWidget(self.history_button)

        self.login_time_label = QLabel(f'Login Time: {self.login_time}', self)
        layout.addWidget(self.login_time_label)

        self.result_list = QListWidget(self)
        self.result_list.itemClicked.connect(self.view_details)
        layout.addWidget(self.result_list)

        self.setCentralWidget(central_widget)

        self.statusBar().showMessage('Ready')

    def import_files(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Import Code Files", "", "Python Files (*.py);;All Files (*)", options=options)
        if len(files) >= 2:
            dialog = FileSelectionDialog(files, self)
            if dialog.exec_():
                base_file = dialog.selected_base_file
                compare_files = dialog.selected_compare_files
                if base_file and compare_files:
                    duplicates = []
                    self.compare_files(base_file, compare_files, duplicates)
                    self.display_results(duplicates)
        else:
            self.statusBar().showMessage('Please select at least 2 files')

    def compare_files(self, base_file, compare_files, duplicates):
        content1 = read_file(base_file)
        for compare_file in compare_files:
            content2 = read_file(compare_file)
            overall_similarity = calculate_overall_similarity(content1.splitlines(), content2.splitlines())
            duplicates.append((base_file, compare_file, overall_similarity))
        save_history(self.username, base_file, compare_files)

    def display_results(self, duplicates):
        self.result_list.clear()
        for file1, file2, similarity in duplicates:
            self.result_list.addItem(f'{file1} and {file2} are {similarity * 100:.2f}% similar')

    def view_details(self, item):
        files = item.text().split(' and ')
        file1, file2 = files[0], files[1].split(' ')[0]
        content1 = read_file(file1)
        content2 = read_file(file2)
        similar_blocks, lines1, lines2 = find_similar_blocks(content1, content2)
        highlighted_content1, highlighted_content2 = highlight_code(content1, content2, similar_blocks, lines1, lines2)
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
    
    def show_history(self):
        self.history_window = HistoryWindow(self.username)
        self.history_window.show()

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

def save_history(username, base_file, compare_files):
    history = {}
    try:
        with open('history.json', 'r') as file:
            history = json.load(file)
    except FileNotFoundError:
        pass
    
    if username not in history:
        history[username] = []
    
    history[username].append({
        'base_file': base_file,
        'compare_files': compare_files,
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    
    with open('history.json', 'w') as file:
        json.dump(history, file)