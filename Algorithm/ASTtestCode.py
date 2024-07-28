import ast
from collections import Counter
from difflib import SequenceMatcher

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

    blocks1 = ["\n".join(lines1[i:i+3]) for i in range(0, len(lines1) - 2)]
    blocks2 = ["\n".join(lines2[i:i+3]) for i in range(0, len(lines2) - 2)]

    similar_blocks = []
    used_blocks2 = set()

    for i, block1 in enumerate(blocks1):
        best_match = None
        best_similarity = 0
        for j, block2 in enumerate(blocks2):
            if j in used_blocks2:
                continue
            similarity = calculate_node_similarity(block1, block2)
            if similarity >= threshold and similarity > best_similarity:
                best_similarity = similarity
                best_match = j
        if best_match is not None:
            similar_blocks.append((i, best_match, best_similarity))
            used_blocks2.add(best_match)

    return similar_blocks, lines1, lines2

def try_expand_block(lines1, lines2, block1_start, block2_start, threshold):
    block1_end = block1_start + 3
    block2_end = block2_start + 3

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
            highlighted_lines1[i] = f"\033[93m{lines1[i]}\033[0m"  # Yellow color
        for i in range(block2_idx, block2_idx + length):
            highlighted_lines2[i] = f"\033[93m{lines2[i]}\033[0m"  # Yellow color

    return '\n'.join(highlighted_lines1), '\n'.join(highlighted_lines2)

def main(file1, file2, threshold=0.9):
    content1 = read_file(file1)
    content2 = read_file(file2)

    similar_blocks, lines1, lines2 = find_similar_blocks(content1, content2, threshold)

    extended_blocks = []
    for block1_idx, block2_idx, similarity in similar_blocks:
        length1, length2 = try_expand_block(lines1, lines2, block1_idx, block2_idx, threshold)
        length = min(length1, length2)
        extended_blocks.append((block1_idx, block2_idx, length))

    highlighted_content1, highlighted_content2 = highlight_code(content1, content2, extended_blocks, lines1, lines2)

    print("File 1 with highlighted similar blocks:")
    print(highlighted_content1)
    print("\nFile 2 with highlighted similar blocks:")
    print(highlighted_content2)

if __name__ == "__main__":
    file1 = "file1.py"
    file2 = "file2.py"
    main(file1, file2)
