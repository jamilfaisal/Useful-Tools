import unittest

from src.context_markdown import render_context_markdown
from src.hn_api import ItemType
from src.recursive_downloader import DownloadedComment, DownloadedStory


class TestContextMarkdown(unittest.TestCase):
    def test_render_context_markdown_preserves_tree_and_cleans_html(self):
        story = DownloadedStory(
            id=42,
            item_type=ItemType.ASK_HN,
            by="story_author",
            time=1712345678,
            title="Ask HN: Thread title",
            text="<p>Hello <a href=\"https://example.com\">world</a>.</p><p>Second paragraph.</p>",
            url="https://news.ycombinator.com",
            score=123,
            descendants=3,
            comments=[
                DownloadedComment(
                    id=100,
                    item_type=ItemType.COMMENT,
                    by="alice",
                    time=1712345700,
                    text="<p>First reply with <strong>bold</strong> text.</p>",
                    children=[
                        DownloadedComment(
                            id=101,
                            item_type=ItemType.COMMENT,
                            by="bob",
                            time=1712345800,
                            text="<p>Nested reply.</p>",
                            children=[],
                        ),
                        DownloadedComment(
                            id=102,
                            item_type=ItemType.COMMENT,
                            by="deleted_user",
                            time=1712345900,
                            text="<p>Should not appear.</p>",
                            deleted=True,
                            children=[],
                        ),
                    ],
                ),
                DownloadedComment(
                    id=103,
                    item_type=ItemType.COMMENT,
                    by="carol",
                    time=1712346000,
                    text="<pre><code>print('hi')</code></pre>",
                    children=[],
                ),
                DownloadedComment(
                    id=104,
                    item_type=ItemType.COMMENT,
                    by="dead_user",
                    time=1712346100,
                    text="<p>Should also not appear.</p>",
                    dead=True,
                    children=[],
                ),
            ],
        )

        markdown = render_context_markdown(story, wrap_width=72)

        expected = """# Ask HN: Thread title

## Metadata
- Story ID: 42
- Author: story_author
- Posted: 2024-04-05 19:34:38 UTC
- Score: 123
- HN comment count: 3
- Story URL: https://news.ycombinator.com
- HN discussion URL: https://news.ycombinator.com/item?id=42
- Type: ask_hn

## Story Text
Hello [world](https://example.com).

Second paragraph.

## Comments
- **alice** · 2024-04-05 19:35:00 UTC
  First reply with **bold** text.

  - **bob** · 2024-04-05 19:36:40 UTC
    Nested reply.

- **carol** · 2024-04-05 19:40:00 UTC
  ```
  print('hi')
  ```
"""

        self.assertEqual(markdown, expected)


if __name__ == "__main__":
    unittest.main()
