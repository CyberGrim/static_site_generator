import re
from textnode import TextNode, TextType

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for node in old_nodes:
        if node.text_type is not TextType.TEXT:
            new_nodes.append(node)
            continue
        node_parts = node.text.split(delimiter)
        if len(node_parts) % 2 == 0:
            raise Exception("The markdown used has invalid syntax")
        for i, part in enumerate(node_parts):
            current_type = text_type if i % 2 == 1 else TextType.TEXT
            if part:
                new_nodes.append(TextNode(part, current_type, None))

    return new_nodes

def extract_markdown_images(text):
    return re.findall(r'!\[([^\[\]]*)\]\(([^()]*)\)', text)

def extract_markdown_links(text):
    return re.findall(r'(?<!\!)\[(?!\!\[)([^\[\]]*)\]\(([^()]*)\)', text)