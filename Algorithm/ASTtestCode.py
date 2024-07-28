import ast
from collections import Counter
from difflib import SequenceMatcher

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def ast_nodes(file_content):
    tree = ast.parse(file_content)
    return [node for node in ast.walk(tree)]

def node_to_string(node):
    return ast.dump(node)

def node_features(node):
    """Extract features from a node, including type, attributes, and fields."""
    features = {
        'type': type(node).__name__,
        'attributes': [],
        'fields': []
    }

    for attr in dir(node):
        if not attr.startswith('_'):
            attr_value = getattr(node, attr, None)
            if isinstance(attr_value, (str, int, float, bool)):
                features['attributes'].append((attr, attr_value))

    for field, value in ast.iter_fields(node):
        if isinstance(value, (str, int, float, bool)):
            features['fields'].append((field, value))

    return features

def calculate_similarity(nodes1, nodes2):
    features1 = [node_features(node) for node in nodes1]
    features2 = [node_features(node) for node in nodes2]

    type_counter1 = Counter(feature['type'] for feature in features1)
    type_counter2 = Counter(feature['type'] for feature in features2)

    attr_counter1 = Counter((feature['type'], tuple(feature['attributes'])) for feature in features1)
    attr_counter2 = Counter((feature['type'], tuple(feature['attributes'])) for feature in features2)

    field_counter1 = Counter((feature['type'], tuple(feature['fields'])) for feature in features1)
    field_counter2 = Counter((feature['type'], tuple(feature['fields'])) for feature in features2)

    type_similarity = calculate_counter_similarity(type_counter1, type_counter2)
    attr_similarity = calculate_counter_similarity(attr_counter1, attr_counter2)
    field_similarity = calculate_counter_similarity(field_counter1, field_counter2)

    return (type_similarity + attr_similarity + field_similarity) / 3

def calculate_counter_similarity(counter1, counter2):
    intersection = sum((counter1 & counter2).values())
    union = sum((counter1 | counter2).values())

    return intersection / union if union > 0 else 0

def find_similar_blocks(nodes1, nodes2, threshold=0.9):
    blocks1 = [node_to_string(node) for node in nodes1]
    blocks2 = [node_to_string(node) for node in nodes2]

    similar_blocks = []
    used_pairs = set()

    for i, block1 in enumerate(blocks1):
        for j, block2 in enumerate(blocks2):
            similarity = calculate_node_similarity(block1, block2)
            if similarity >= threshold and (i, j) not in used_pairs:
                similar_blocks.append((i, j, similarity))
                used_pairs.add((i, j))

    return similar_blocks

def calculate_node_similarity(block1, block2):
    return SequenceMatcher(None, block1, block2).ratio()

def get_code_block(file_content, node):
    return ast.get_source_segment(file_content, node)

def highlight_code(content, nodes, similar_blocks):
    lines = content.splitlines()
    highlighted_lines = []
    for i, line in enumerate(lines):
        highlighted_lines.append(line)

    for start, end in similar_blocks:
        for i in range(start, end + 1):
            highlighted_lines[i] = f"\033[93m{lines[i]}\033[0m"  # Yellow color

    return '\n'.join(highlighted_lines)

def main(file1, file2, threshold=0.9):
    content1 = read_file(file1)
    content2 = read_file(file2)

    nodes1 = ast_nodes(content1)
    nodes2 = ast_nodes(content2)

    similarity = calculate_similarity(nodes1, nodes2)
    print(f"The similarity between the two files is: {similarity:.2%}\n")

    similar_blocks = find_similar_blocks(nodes1, nodes2, threshold)

    blocks1 = []
    blocks2 = []
    for start1, start2, _ in similar_blocks:
        node1, node2 = nodes1[start1], nodes2[start2]
        if hasattr(node1, 'lineno') and hasattr(node1, 'end_lineno'):
            blocks1.append((node1.lineno - 1, node1.end_lineno - 1))
        if hasattr(node2, 'lineno') and hasattr(node2, 'end_lineno'):
            blocks2.append((node2.lineno - 1, node2.end_lineno - 1))

    print("File 1 with highlighted similar blocks:")
    print(highlight_code(content1, nodes1, blocks1))
    print("\nFile 2 with highlighted similar blocks:")
    print(highlight_code(content2, nodes2, blocks2))

if __name__ == "__main__":
    file1 = "file1.py"
    file2 = "file2.py"
    main(file1, file2)
