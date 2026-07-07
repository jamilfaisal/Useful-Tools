import tempfile
import unittest
from pathlib import Path

from src.hn_api import Story
from src.index_html import render_index_html, story_folder_name, write_index_html


class TestIndexHtml(unittest.TestCase):
    def test_render_index_html_includes_required_story_links(self):
        story = Story(
            id=42,
            title="Ask HN: Thread title",
            url="https://example.com/article",
            score=123,
            descendants=7,
        )

        html = render_index_html([story])

        self.assertIn("<!doctype html>", html)
        self.assertIn("color-scheme: dark", html)
        self.assertIn("Ask HN: Thread title", html)
        self.assertIn("123 points", html)
        self.assertIn("7 comments", html)
        self.assertIn('href="https://example.com/article"', html)
        self.assertIn('href="https://news.ycombinator.com/item?id=42"', html)
        self.assertIn(f'href="{story_folder_name(story)}/"', html)

    def test_write_index_html_writes_output_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output" / "index.html"
            story = Story(id=7, title="Sample story", score=10, descendants=0)

            written_path = write_index_html([story], output_path)

            self.assertEqual(written_path, output_path)
            self.assertIn("Sample story", output_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
