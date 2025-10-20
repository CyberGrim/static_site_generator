import unittest

from htmlnode import HTMLNode, LeafNode

class TestHTMLNode(unittest.TestCase):
    def test_url_eq(self):
        node = HTMLNode(tag="a", value="test",props={"href": "https://www.google.com","target": "_blank"})
        self.assertEqual(node.props_to_html(), f" href=\"https://www.google.com\" target=\"_blank\"")

    def test_url_not_eq(self):
        node = HTMLNode(tag="a", value="test",props={"href": "https://www.google.com","target": "_blank"})
        self.assertNotEqual(node.props_to_html(), f" href=\"https://www.google.com\" target=\"_parent\"")

    def test_image_eq(self):
        node = HTMLNode(tag="a", value="test",props={"src": "https://www.google.com/test.jpg","alt": "This is a test"})
        self.assertEqual(node.props_to_html(), f" src=\"https://www.google.com/test.jpg\" alt=\"This is a test\"")

    def test_image_not_eq(self):
        node = HTMLNode(tag="a", value="test",props={"src": "https://www.google.com","alt": "This is a test"})
        self.assertNotEqual(node.props_to_html(), f" href=\"https://www.google.com\" target=\"_parent\"")

class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "This is a paragraph!")
        self.assertEqual(node.to_html(), "<p>This is a paragraph!</p>")

    def test_leaf_to_html_b(self):
        node = LeafNode("b", "This is bold!")
        self.assertEqual(node.to_html(), "<b>This is bold!</b>")

    def test_leaf_to_html_i(self):
        node = LeafNode("i", "This is italic!")
        self.assertEqual(node.to_html(), "<i>This is italic!</i>")

if __name__ == "__main__":
    unittest.main()