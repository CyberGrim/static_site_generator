import unittest

from textnode import TextType, TextNode
from markdown_parser import split_nodes_delimiter, extract_markdown_images, extract_markdown_links

class TestSplitNodesDelimiter(unittest.TestCase):
    def test_empty_input(self):
        new_nodes = split_nodes_delimiter([], "`", TextType.CODE)
        self.assertEqual(len(new_nodes), 0)
        self.assertEqual(new_nodes, [])
    def test_split_with_delimiters(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[0].text, "This is text with a ")
        self.assertEqual(new_nodes[0].text_type, TextType.TEXT)
        self.assertEqual(new_nodes[1].text, "code block")
        self.assertEqual(new_nodes[1].text_type, TextType.CODE)
        self.assertEqual(new_nodes[2].text, " word")
        self.assertEqual(new_nodes[2].text_type, TextType.TEXT)

    def test_no_delimiters(self):
        node = TextNode("Plain text without delimiters", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(len(new_nodes), 1)
        self.assertEqual(new_nodes[0].text, "Plain text without delimiters")
        self.assertEqual(new_nodes[0].text_type, TextType.TEXT)

    def test_multiple_delimited_sections(self):
        node = TextNode("Start `code1` middle `code2` end", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(len(new_nodes), 5)
        self.assertEqual(new_nodes[0].text, "Start ")
        self.assertEqual(new_nodes[1].text, "code1")
        self.assertEqual(new_nodes[1].text_type, TextType.CODE)
        self.assertEqual(new_nodes[2].text, " middle ")
        self.assertEqual(new_nodes[3].text, "code2")
        self.assertEqual(new_nodes[3].text_type, TextType.CODE)
        self.assertEqual(new_nodes[4].text, " end")

    def test_empty_delimited_section(self):
        node = TextNode("Before `` after", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(len(new_nodes), 2)
        self.assertEqual(new_nodes[0].text, "Before ")
        self.assertEqual(new_nodes[1].text, " after")

    def test_preserve_non_text_nodes(self):
        node1 = TextNode("Already code", TextType.CODE)
        node2 = TextNode("Text with `code` block", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node1, node2], "`", TextType.CODE)
        self.assertEqual(len(new_nodes), 4)
        self.assertEqual(new_nodes[0].text, "Already code")
        self.assertEqual(new_nodes[0].text_type, TextType.CODE)
        self.assertEqual(new_nodes[1].text, "Text with ")
        self.assertEqual(new_nodes[2].text, "code")
        self.assertEqual(new_nodes[3].text, " block")

    def test_invalid_delimiter_pairs(self):
        node = TextNode("Text with `unpaired delimiter", TextType.TEXT)
        with self.assertRaises(Exception) as context:
            split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertTrue("invalid syntax" in str(context.exception).lower())

    def test_bold_text(self):
        node = TextNode("This is **bold** text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[0].text, "This is ")
        self.assertEqual(new_nodes[0].text_type, TextType.TEXT)
        self.assertEqual(new_nodes[1].text, "bold")
        self.assertEqual(new_nodes[1].text_type, TextType.BOLD)
        self.assertEqual(new_nodes[2].text, " text")
        self.assertEqual(new_nodes[2].text_type, TextType.TEXT)

    def test_italic_text(self):
        node = TextNode("This is _italic_ text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[0].text, "This is ")
        self.assertEqual(new_nodes[0].text_type, TextType.TEXT)
        self.assertEqual(new_nodes[1].text, "italic")
        self.assertEqual(new_nodes[1].text_type, TextType.ITALIC)
        self.assertEqual(new_nodes[2].text, " text")
        self.assertEqual(new_nodes[2].text_type, TextType.TEXT)

    def test_mixed_markdown(self):
        node = TextNode("**Bold** and _italic_ and `code`", TextType.TEXT)
        # Test bold first
        bold_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        # Test italic on the result
        italic_nodes = split_nodes_delimiter(bold_nodes, "_", TextType.ITALIC)
        # Finally test code
        final_nodes = split_nodes_delimiter(italic_nodes, "`", TextType.CODE)
        
        self.assertEqual(len(final_nodes), 5)
        expected_types = [TextType.BOLD, TextType.TEXT, TextType.ITALIC, TextType.TEXT, TextType.CODE]
        expected_texts = ["Bold", " and ", "italic", " and ", "code"]
        
        for i, node in enumerate(final_nodes):
            self.assertEqual(node.text_type, expected_types[i])
            self.assertEqual(node.text, expected_texts[i])

    def test_empty_node_list_with_content(self):
        nodes = [TextNode("", TextType.TEXT)]
        new_nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
        self.assertEqual(len(new_nodes), 0)

class TestMarkdownExtraction(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        )
        self.assertEqual(
            matches,
            [
                ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
                ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")
            ]
        )

    def test_single_image(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertEqual(
            matches,
            [("image", "https://i.imgur.com/zjjcJKZ.png")]
        )

    def test_extract_markdown_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        self.assertEqual(
            extract_markdown_links(text),
            [
                ("to boot dev", "https://www.boot.dev"),
                ("to youtube", "https://www.youtube.com/@bootdotdev")
            ]
        )

    def test_single_link(self):
        text = "This is a [link](https://boot.dev) in text"
        self.assertEqual(
            extract_markdown_links(text),
            [("link", "https://boot.dev")]
        )

    def test_no_matches(self):
        self.assertEqual(extract_markdown_images("Plain text"), [])
        self.assertEqual(extract_markdown_links("Plain text"), [])

    def test_links_not_matching_images(self):
        text = "![image](image.jpg) and [link](url)"
        self.assertEqual(extract_markdown_links(text), [("link", "url")])
        
    def test_nested_brackets_safety(self):
        text = "[![img alt](img.jpg)](url)"
        self.assertEqual(extract_markdown_links(text), [])
        self.assertEqual(extract_markdown_images(text), [("img alt", "img.jpg")])

if __name__ == "__main__":
    unittest.main()