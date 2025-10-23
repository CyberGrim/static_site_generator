import unittest
from textnode import TextNode, TextType
from markdown_parser import (
    split_nodes_delimiter, 
    extract_markdown_images, 
    extract_markdown_links,
    split_nodes_image,
    split_nodes_link
)


class TestSplitNodesDelimiter(unittest.TestCase):
    """Test cases for split_nodes_delimiter function."""
    
    def test_empty_input(self):
        """Test empty input list."""
        new_nodes = split_nodes_delimiter([], "`", TextType.CODE)
        self.assertEqual(len(new_nodes), 0)
        self.assertEqual(new_nodes, [])

    def test_split_with_delimiters(self):
        """Test basic delimiter splitting."""
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
        """Test text without delimiters."""
        node = TextNode("Plain text without delimiters", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(len(new_nodes), 1)
        self.assertEqual(new_nodes[0].text, "Plain text without delimiters")
        self.assertEqual(new_nodes[0].text_type, TextType.TEXT)

    def test_multiple_delimited_sections(self):
        """Test multiple delimited sections."""
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
        """Test empty delimited section."""
        node = TextNode("Before `` after", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(len(new_nodes), 2)
        self.assertEqual(new_nodes[0].text, "Before ")
        self.assertEqual(new_nodes[1].text, " after")

    def test_preserve_non_text_nodes(self):
        """Test that non-TEXT nodes are preserved."""
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
        """Test invalid delimiter pairs raise exception."""
        node = TextNode("Text with `unpaired delimiter", TextType.TEXT)
        with self.assertRaises(Exception) as context:
            split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertTrue("invalid syntax" in str(context.exception).lower())

    def test_bold_text(self):
        """Test bold text delimiter."""
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
        """Test italic text delimiter."""
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
        """Test mixed markdown processing."""
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
        """Test empty node list."""
        nodes = [TextNode("", TextType.TEXT)]
        new_nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
        self.assertEqual(len(new_nodes), 0)


class TestMarkdownExtraction(unittest.TestCase):
    """Test cases for markdown extraction functions."""
    
    def test_extract_markdown_images(self):
        """Test extracting multiple images."""
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
        """Test extracting single image."""
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertEqual(
            matches,
            [("image", "https://i.imgur.com/zjjcJKZ.png")]
        )

    def test_extract_markdown_links(self):
        """Test extracting multiple links."""
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        self.assertEqual(
            extract_markdown_links(text),
            [
                ("to boot dev", "https://www.boot.dev"),
                ("to youtube", "https://www.youtube.com/@bootdotdev")
            ]
        )

    def test_single_link(self):
        """Test extracting single link."""
        text = "This is a [link](https://boot.dev) in text"
        self.assertEqual(
            extract_markdown_links(text),
            [("link", "https://boot.dev")]
        )

    def test_no_matches(self):
        """Test text with no matches."""
        self.assertEqual(extract_markdown_images("Plain text"), [])
        self.assertEqual(extract_markdown_links("Plain text"), [])

    def test_links_not_matching_images(self):
        """Test that links don't match image patterns."""
        text = "![image](image.jpg) and [link](url)"
        self.assertEqual(extract_markdown_links(text), [("link", "url")])
        
    def test_nested_brackets_safety(self):
        """Test nested brackets are handled correctly."""
        text = "[![img alt](img.jpg)](url)"
        self.assertEqual(extract_markdown_links(text), [])
        self.assertEqual(extract_markdown_images(text), [("img alt", "img.jpg")])

    def test_special_characters_in_alt_text(self):
        """Test special characters in alt text."""
        text = "![alt with <>&\"'](url)"
        matches = extract_markdown_images(text)
        self.assertEqual(matches, [("alt with <>&\"'", "url")])

    def test_special_characters_in_urls(self):
        """Test special characters in URLs."""
        text = "![alt](url?param=value&other=123)"
        matches = extract_markdown_images(text)
        self.assertEqual(matches, [("alt", "url?param=value&other=123")])

    def test_empty_alt_text(self):
        """Test empty alt text."""
        text = "![](url)"
        matches = extract_markdown_images(text)
        self.assertEqual(matches, [("", "url")])

    def test_empty_url(self):
        """Test empty URL."""
        text = "![alt]()"
        matches = extract_markdown_images(text)
        self.assertEqual(matches, [("alt", "")])


class TestSplitNodesImage(unittest.TestCase):
    """Test cases for split_nodes_image function."""
    
    def test_single_image(self):
        """Test single image conversion."""
        node = TextNode("Text ![img](url) more", TextType.TEXT)
        result = split_nodes_image([node])
        expected = [
            TextNode("Text ", TextType.TEXT),
            TextNode("img", TextType.IMAGE, "url"),
            TextNode(" more", TextType.TEXT)
        ]
        self.assertEqual(result, expected)

    def test_multiple_images_with_text_between(self):
        """Test multiple images with text between them."""
        node = TextNode("Start ![img1](url1) middle ![img2](url2) end", TextType.TEXT)
        result = split_nodes_image([node])
        expected = [
            TextNode("Start ", TextType.TEXT),
            TextNode("img1", TextType.IMAGE, "url1"),
            TextNode(" middle ", TextType.TEXT),
            TextNode("img2", TextType.IMAGE, "url2"),
            TextNode(" end", TextType.TEXT)
        ]
        self.assertEqual(result, expected)

    def test_image_at_start(self):
        """Test image at the very beginning."""
        node = TextNode("![start](start.jpg) some text", TextType.TEXT)
        result = split_nodes_image([node])
        expected = [
            TextNode("start", TextType.IMAGE, "start.jpg"),
            TextNode(" some text", TextType.TEXT)
        ]
        self.assertEqual(result, expected)

    def test_image_at_end(self):
        """Test image at the very end."""
        node = TextNode("some text ![end](end.jpg)", TextType.TEXT)
        result = split_nodes_image([node])
        expected = [
            TextNode("some text ", TextType.TEXT),
            TextNode("end", TextType.IMAGE, "end.jpg")
        ]
        self.assertEqual(result, expected)

    def test_adjacent_images(self):
        """Test adjacent images with no text between."""
        node = TextNode("![img1](url1)![img2](url2)", TextType.TEXT)
        result = split_nodes_image([node])
        expected = [
            TextNode("img1", TextType.IMAGE, "url1"),
            TextNode("img2", TextType.IMAGE, "url2")
        ]
        self.assertEqual(result, expected)

    def test_image_with_no_surrounding_text(self):
        """Test image with no surrounding text."""
        node = TextNode("![only](only.jpg)", TextType.TEXT)
        result = split_nodes_image([node])
        expected = [
            TextNode("only", TextType.IMAGE, "only.jpg")
        ]
        self.assertEqual(result, expected)

    def test_no_images_at_all(self):
        """Test text with no images."""
        node = TextNode("Just plain text with no images", TextType.TEXT)
        result = split_nodes_image([node])
        expected = [node]
        self.assertEqual(result, expected)

    def test_duplicate_images(self):
        """Test handling of duplicate image patterns."""
        node = TextNode("First ![same](url) middle ![same](url) last", TextType.TEXT)
        result = split_nodes_image([node])
        expected = [
            TextNode("First ", TextType.TEXT),
            TextNode("same", TextType.IMAGE, "url"),
            TextNode(" middle ", TextType.TEXT),
            TextNode("same", TextType.IMAGE, "url"),
            TextNode(" last", TextType.TEXT)
        ]
        self.assertEqual(result, expected)

    def test_non_text_nodes_passed_through(self):
        """Test that non-TEXT nodes are passed through unchanged."""
        node = TextNode("Bold text", TextType.BOLD)
        result = split_nodes_image([node])
        expected = [node]
        self.assertEqual(result, expected)

    def test_empty_text_node(self):
        """Test empty text node."""
        node = TextNode("", TextType.TEXT)
        result = split_nodes_image([node])
        expected = [node]
        self.assertEqual(result, expected)

    def test_special_characters_in_alt_text(self):
        """Test special characters in alt text."""
        node = TextNode("![alt with <>&\"'](url)", TextType.TEXT)
        result = split_nodes_image([node])
        expected = [
            TextNode("alt with <>&\"'", TextType.IMAGE, "url")
        ]
        self.assertEqual(result, expected)

    def test_special_characters_in_urls(self):
        """Test special characters in URLs."""
        node = TextNode("![alt](url?param=value&other=123)", TextType.TEXT)
        result = split_nodes_image([node])
        expected = [
            TextNode("alt", TextType.IMAGE, "url?param=value&other=123")
        ]
        self.assertEqual(result, expected)

    def test_no_empty_nodes_created(self):
        """Test that no empty TextNodes are created."""
        test_cases = [
            "![img](url)",  # Only image
            "![img1](url1)![img2](url2)",  # Adjacent images
            "![img](url) text",  # Image at start
            "text ![img](url)",  # Image at end
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                node = TextNode(text, TextType.TEXT)
                result = split_nodes_image([node])
                
                # Check that no empty text nodes are created
                for n in result:
                    if n.text_type == TextType.TEXT:
                        self.assertTrue(len(n.text) > 0, f"Empty TextNode found for text: {text}")

    def test_order_independence(self):
        """Test that processing works regardless of extraction order."""
        text = "![first](url1) middle ![second](url2)"
        node = TextNode(text, TextType.TEXT)
        result = split_nodes_image([node])
        
        # Should process in text order, not extraction order
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].text_type, TextType.IMAGE)
        self.assertEqual(result[0].text, "first")
        self.assertEqual(result[1].text_type, TextType.TEXT)
        self.assertEqual(result[1].text, " middle ")
        self.assertEqual(result[2].text_type, TextType.IMAGE)
        self.assertEqual(result[2].text, "second")

    def test_mixed_content_with_links(self):
        """Test that links are preserved during image processing."""
        text = "Text ![img](img.jpg) with [link](url.com) content"
        node = TextNode(text, TextType.TEXT)
        result = split_nodes_image([node])
        
        # Check that link markdown is preserved in text nodes
        text_nodes = [n for n in result if n.text_type == TextType.TEXT]
        self.assertTrue(any("[link](url.com)" in n.text for n in text_nodes))


class TestSplitNodesLink(unittest.TestCase):
    """Test cases for split_nodes_link function."""
    
    def test_single_link(self):
        """Test single link conversion."""
        node = TextNode("Text [link](url) more", TextType.TEXT)
        result = split_nodes_link([node])
        expected = [
            TextNode("Text ", TextType.TEXT),
            TextNode("link", TextType.LINK, "url"),
            TextNode(" more", TextType.TEXT)
        ]
        self.assertEqual(result, expected)

    def test_multiple_links_with_text_between(self):
        """Test multiple links with text between them."""
        node = TextNode("Start [link1](url1) middle [link2](url2) end", TextType.TEXT)
        result = split_nodes_link([node])
        expected = [
            TextNode("Start ", TextType.TEXT),
            TextNode("link1", TextType.LINK, "url1"),
            TextNode(" middle ", TextType.TEXT),
            TextNode("link2", TextType.LINK, "url2"),
            TextNode(" end", TextType.TEXT)
        ]
        self.assertEqual(result, expected)

    def test_link_at_start(self):
        """Test link at the very beginning."""
        node = TextNode("[start](start.com) some text", TextType.TEXT)
        result = split_nodes_link([node])
        expected = [
            TextNode("start", TextType.LINK, "start.com"),
            TextNode(" some text", TextType.TEXT)
        ]
        self.assertEqual(result, expected)

    def test_link_at_end(self):
        """Test link at the very end."""
        node = TextNode("some text [end](end.com)", TextType.TEXT)
        result = split_nodes_link([node])
        expected = [
            TextNode("some text ", TextType.TEXT),
            TextNode("end", TextType.LINK, "end.com")
        ]
        self.assertEqual(result, expected)

    def test_adjacent_links(self):
        """Test adjacent links with no text between."""
        node = TextNode("[link1](url1)[link2](url2)", TextType.TEXT)
        result = split_nodes_link([node])
        expected = [
            TextNode("link1", TextType.LINK, "url1"),
            TextNode("link2", TextType.LINK, "url2")
        ]
        self.assertEqual(result, expected)

    def test_link_with_no_surrounding_text(self):
        """Test link with no surrounding text."""
        node = TextNode("[only](only.com)", TextType.TEXT)
        result = split_nodes_link([node])
        expected = [
            TextNode("only", TextType.LINK, "only.com")
        ]
        self.assertEqual(result, expected)

    def test_no_links_at_all(self):
        """Test text with no links."""
        node = TextNode("Just plain text with no links", TextType.TEXT)
        result = split_nodes_link([node])
        expected = [node]
        self.assertEqual(result, expected)

    def test_duplicate_links(self):
        """Test handling of duplicate link patterns."""
        node = TextNode("First [same](url) middle [same](url) last", TextType.TEXT)
        result = split_nodes_link([node])
        expected = [
            TextNode("First ", TextType.TEXT),
            TextNode("same", TextType.LINK, "url"),
            TextNode(" middle ", TextType.TEXT),
            TextNode("same", TextType.LINK, "url"),
            TextNode(" last", TextType.TEXT)
        ]
        self.assertEqual(result, expected)

    def test_non_text_nodes_passed_through(self):
        """Test that non-TEXT nodes are passed through unchanged."""
        node = TextNode("Bold text", TextType.BOLD)
        result = split_nodes_link([node])
        expected = [node]
        self.assertEqual(result, expected)

    def test_empty_text_node(self):
        """Test empty text node."""
        node = TextNode("", TextType.TEXT)
        result = split_nodes_link([node])
        expected = [node]
        self.assertEqual(result, expected)

    def test_special_characters_in_link_text(self):
        """Test special characters in link text."""
        node = TextNode("[link with <>&\"'](url)", TextType.TEXT)
        result = split_nodes_link([node])
        expected = [
            TextNode("link with <>&\"'", TextType.LINK, "url")
        ]
        self.assertEqual(result, expected)

    def test_special_characters_in_urls(self):
        """Test special characters in URLs."""
        node = TextNode("[link](url?param=value&other=123)", TextType.TEXT)
        result = split_nodes_link([node])
        expected = [
            TextNode("link", TextType.LINK, "url?param=value&other=123")
        ]
        self.assertEqual(result, expected)

    def test_no_empty_nodes_created(self):
        """Test that no empty TextNodes are created."""
        test_cases = [
            "[link](url)",  # Only link
            "[link1](url1)[link2](url2)",  # Adjacent links
            "[link](url) text",  # Link at start
            "text [link](url)",  # Link at end
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                node = TextNode(text, TextType.TEXT)
                result = split_nodes_link([node])
                
                # Check that no empty text nodes are created
                for n in result:
                    if n.text_type == TextType.TEXT:
                        self.assertTrue(len(n.text) > 0, f"Empty TextNode found for text: {text}")

    def test_order_independence(self):
        """Test that processing works regardless of extraction order."""
        text = "[first](url1) middle [second](url2)"
        node = TextNode(text, TextType.TEXT)
        result = split_nodes_link([node])
        
        # Should process in text order, not extraction order
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].text_type, TextType.LINK)
        self.assertEqual(result[0].text, "first")
        self.assertEqual(result[1].text_type, TextType.TEXT)
        self.assertEqual(result[1].text, " middle ")
        self.assertEqual(result[2].text_type, TextType.LINK)
        self.assertEqual(result[2].text, "second")


class TestMixedContentProcessing(unittest.TestCase):
    """Test cases for processing mixed content with both images and links."""
    
    def test_mixed_content_processing_order(self):
        """Test that mixed content is processed correctly in sequence."""
        text = "Start ![img](img.jpg) with [link](url.com) and ![img2](img2.jpg) end"
        node = TextNode(text, TextType.TEXT)
        
        # First process images
        image_result = split_nodes_image([node])
        
        # Then process links
        final_result = split_nodes_link(image_result)
        
        # Should have: Start, img, " with ", link, " and ", img2, " end"
        expected_types = [
            TextType.TEXT, TextType.IMAGE, TextType.TEXT, 
            TextType.LINK, TextType.TEXT, TextType.IMAGE, TextType.TEXT
        ]
        actual_types = [n.text_type for n in final_result]
        self.assertEqual(actual_types, expected_types)

    def test_links_untouched_by_image_processing(self):
        """Test that links remain untouched when processing images."""
        text = "Text ![img](img.jpg) with [link](url.com) content"
        node = TextNode(text, TextType.TEXT)
        
        # Process images first
        image_result = split_nodes_image([node])
        
        # Check that link markdown is preserved in text nodes
        text_nodes = [n for n in image_result if n.text_type == TextType.TEXT]
        self.assertTrue(any("[link](url.com)" in n.text for n in text_nodes))
        
        # Process links on the result
        final_result = split_nodes_link(image_result)
        
        # Should have: "Text ", img, " with ", link, " content"
        expected_types = [TextType.TEXT, TextType.IMAGE, TextType.TEXT, TextType.LINK, TextType.TEXT]
        actual_types = [n.text_type for n in final_result]
        self.assertEqual(actual_types, expected_types)

    def test_complex_mixed_content(self):
        """Test complex content with multiple images and links."""
        text = "![img1](url1) text [link1](url1) ![img2](url2) [link2](url2) end"
        node = TextNode(text, TextType.TEXT)
        
        # Process images first
        image_result = split_nodes_image([node])
        
        # Then process links
        final_result = split_nodes_link(image_result)
        
        # Should have: img1, " text ", link1, " ", img2, " ", link2, " end"
        expected_types = [
            TextType.IMAGE, TextType.TEXT, TextType.LINK, 
            TextType.TEXT, TextType.IMAGE, TextType.TEXT, 
            TextType.LINK, TextType.TEXT
        ]
        actual_types = [n.text_type for n in final_result]
        self.assertEqual(actual_types, expected_types)


if __name__ == "__main__":
    unittest.main()