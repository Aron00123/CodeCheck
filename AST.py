import ast
import astor
from difflib import SequenceMatcher

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def normalize_variable_names(node):
    """
    Normalize variable names in the AST to generic names like var1, var2, etc.
    """
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

    for i, block1 in enumerate(blocks1):
        best_match = None
        best_similarity = 0
        for j, block2 in enumerate(blocks2):
            if j in used_blocks2:
                continue
            similarity = ast_similarity(block1, block2)
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

    for block1_idx, block2_idx, _ in similar_blocks:
        block1 = blocks1[block1_idx]
        block2 = blocks2[block2_idx]

        for i in range(block1.lineno - 1, block1.end_lineno):
            if not lines1[i].strip().startswith("#"):
                highlighted_lines1[i] = f"\033[93m{lines1[i]}\033[0m"  # Yellow color

        for i in range(block2.lineno - 1, block2.end_lineno):
            if not lines2[i].strip().startswith("#"):
                highlighted_lines2[i] = f"\033[93m{lines2[i]}\033[0m"  # Yellow color

    return '\n'.join(highlighted_lines1), '\n'.join(highlighted_lines2)

def calculate_overall_similarity(blocks1, blocks2):
    similarities = []

    for block1 in blocks1:
        best_similarity = 0
        for block2 in blocks2:
            similarity = ast_similarity(block1, block2)
            if similarity > best_similarity:
                best_similarity = similarity
        similarities.append(best_similarity)

    return sum(similarities) / len(similarities)

def main(file1, file2, threshold=0.9):
    content1 = read_file(file1)
    content2 = read_file(file2)

    similar_blocks, blocks1, blocks2 = find_similar_blocks(content1, content2, threshold)

    overall_similarity = calculate_overall_similarity(blocks1, blocks2)
    print(f"The overall similarity between the two files is: {overall_similarity:.2%}\n")

    highlighted_content1, highlighted_content2 = highlight_code(content1, content2, similar_blocks, blocks1, blocks2)

    print("File 1 with highlighted similar blocks:")
    print(highlighted_content1)
    print("\nFile 2 with highlighted similar blocks:")
    print(highlighted_content2)

if __name__ == "__main__":
    test_files = [
        ("file1.py", "file2.py"),
        ("file1.py", "file3.py"),
        ("file1.py", "file4.py"),
        ("file1.py", "file5.py"),
        ("file1.py", "file6.py"),
        ("file7.py", "file8.py"),
    ]

    for file1, file2 in test_files:
        print(f"Comparing {file1} and {file2}:")
        main(file1, file2)