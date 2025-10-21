import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode

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

    def test_props_to_html_empty(self):
        node = HTMLNode(tag="div")
        self.assertEqual(node.props_to_html(), "")

    def test_to_html_not_implemented(self):
        node = HTMLNode(tag="div")
        with self.assertRaises(NotImplementedError):
            node.to_html()

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

    def test_leaf_no_tag_returns_value(self):
        node = LeafNode(None, "Plain text")
        self.assertEqual(node.to_html(), "Plain text")

    def test_leaf_with_props(self):
        node = LeafNode("a", "Click me", {"href": "https://example.com"})
        self.assertEqual(node.to_html(), '<a href="https://example.com">Click me</a>')

    def test_leaf_raises_when_no_value(self):
        node = LeafNode("p", "")
        with self.assertRaises(ValueError):
            node.to_html()

class TestParentNode(unittest.TestCase):
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_parent_with_props(self):
        child_node = LeafNode("p", "child")
        parent_node = ParentNode("div", [child_node], {"class": "wrapper", "id": "main"})
        self.assertEqual(
            parent_node.to_html(),
            '<div class="wrapper" id="main"><p>child</p></div>'
        )

    def test_parent_raises_no_tag(self):
        child_node = LeafNode("p", "child")
        with self.assertRaises(ValueError):
            ParentNode("", [child_node]).to_html()

    def test_parent_raises_no_children(self):
        with self.assertRaises(ValueError):
            ParentNode("div", []).to_html()

if __name__ == "__main__":
    unittest.main()