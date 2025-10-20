from enum import Enum

class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italix"
    CODE = "code"
    LINKS = "link"
    IMAGES = "image"

class TextNode():
    def __init__(self, text, TextType, url = None):
        self.text = text
        self.text_type = TextType
        self.url = url

    def __eq__(self, node2):
        if self.text == node2.text and self.text_type == node2.text_type and self.url == node2.url:
            return True
        else:
            return False
        
    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"