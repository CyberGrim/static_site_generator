import re
from enum import Enum
from textnode import TextNode, TextType

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
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

def split_nodes_image(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        
        images = extract_markdown_images(node.text)
        if not images:
            new_nodes.append(node)
            continue
        
        text = node.text
        for alt_text, url in images:
            pattern = f"![{alt_text}]({url})"
            if pattern in text:
                parts = text.split(pattern, 1)
                if len(parts) == 2:
                    if parts[0]:
                        new_nodes.append(TextNode(parts[0], TextType.TEXT))
                    new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))
                    text = parts[1]
        
        if text:
            new_nodes.append(TextNode(text, TextType.TEXT))
    
    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        
        links = extract_markdown_links(node.text)
        if not links:
            new_nodes.append(node)
            continue
        
        text = node.text
        for link_text, url in links:
            pattern = f"[{link_text}]({url})"
            if pattern in text:
                parts = text.split(pattern, 1)
                if len(parts) == 2:
                    if parts[0]:
                        new_nodes.append(TextNode(parts[0], TextType.TEXT))
                    if link_text:
                        new_nodes.append(TextNode(link_text, TextType.LINK, url))
                    text = parts[1]
        
        if text:
            new_nodes.append(TextNode(text, TextType.TEXT))
    
    return new_nodes

def text_to_textnodes(text):
    first_node = [TextNode(text, TextType.TEXT)]
    code_nodes = split_nodes_delimiter(first_node, "`", TextType.CODE)
    image_nodes = split_nodes_image(code_nodes)
    link_nodes = split_nodes_link(image_nodes)
    bold_nodes = split_nodes_delimiter(link_nodes, "**", TextType.BOLD)
    final_nodes = split_nodes_delimiter(bold_nodes, "_", TextType.ITALIC)

    return final_nodes

def markdown_to_blocks(markdown):
    blocks = markdown.split('\n\n')
    cleaned_blocks = []
    for block in blocks:
        cleaned = block.strip().strip('\n')
        if cleaned == "":
            continue
        cleaned_blocks.append(cleaned)
    return cleaned_blocks

def block_to_block_type(block):
    lines = block.splitlines()

    # Testing for Headings
    i = 0
    while i < len(block) and block[i] == '#':
        i += 1
    if 1 <= i <= 6 and len(block) > i and block[i] == ' ' and len(block.strip()) > i:
        return BlockType.HEADING
              
    # Testing for Code
    if len(lines) >= 3 and lines[0].startswith('```') and lines[-1].strip() == '```':
        return BlockType.CODE

    # Testing for Quotes
    if all(line.startswith('>') for line in lines):
        return BlockType.QUOTE

    # Testing for Unordered Lists
    if all(line.startswith('- ') for line in lines):
        return BlockType.UNORDERED_LIST
    
    # Testing for Ordered Lists
    expected = 1
    for line in lines:
        if not line.startswith(f'{expected}. '):
            break
        expected += 1
    if expected == len(lines) + 1:
        return BlockType.ORDERED_LIST
    
    # For anything else, there's Mastercard. Or a Paragraph type
    return BlockType.PARAGRAPH