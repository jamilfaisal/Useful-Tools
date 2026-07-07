"""Deterministic markdown rendering for Hacker News story context."""

from __future__ import annotations

from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from textwrap import fill
from typing import Iterable, List, Optional

from .recursive_downloader import DownloadedComment, DownloadedStory


DEFAULT_WRAP_WIDTH = 88


def render_context_markdown(story: DownloadedStory, wrap_width: int = DEFAULT_WRAP_WIDTH) -> str:
    """Render a downloaded story and its comment tree as markdown."""
    sections: List[str] = [f"# {story.title or f'Hacker News Story {story.id}'}", ""]
    sections.extend(
        [
            "## Metadata",
            _render_metadata_line("Story ID", str(story.id), wrap_width),
            _render_metadata_line("Author", story.by or "(unknown)", wrap_width),
            _render_metadata_line("Posted", _format_timestamp(story.time), wrap_width),
            _render_metadata_line(
                "Score",
                str(story.score if story.score is not None else 0),
                wrap_width,
            ),
            _render_metadata_line(
                "HN comment count",
                str(story.descendants if story.descendants is not None else _count_comments(story.comments)),
                wrap_width,
            ),
            _render_metadata_line("Story URL", story.url or "(none)", wrap_width),
            _render_metadata_line("HN discussion URL", _story_discussion_url(story.id), wrap_width),
            _render_metadata_line("Type", story.item_type.value, wrap_width),
            "",
            "## Story Text",
        ]
    )

    story_text = _html_to_markdown(story.text, wrap_width=wrap_width)
    if story_text:
        sections.append(story_text)
    else:
        sections.append("_No story text._")

    sections.extend(["", "## Comments"])
    if story.comments:
        sections.append(_render_comment_tree(story.comments, wrap_width=wrap_width))
    else:
        sections.append("_No comments._")

    return "\n".join(sections).rstrip() + "\n"


def write_context_markdown(
    story: DownloadedStory,
    output_path: str | Path,
    wrap_width: int = DEFAULT_WRAP_WIDTH,
) -> Path:
    """Write the rendered markdown to disk and return the file path."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_context_markdown(story, wrap_width=wrap_width), encoding="utf-8")
    return path


def _render_metadata_line(label: str, value: str, wrap_width: int) -> str:
    rendered = f"- {label}: {value}"
    return fill(rendered, width=wrap_width, subsequent_indent="  ")


def _story_discussion_url(story_id: int) -> str:
    return f"https://news.ycombinator.com/item?id={story_id}"


def _format_timestamp(timestamp: Optional[int]) -> str:
    if timestamp is None:
        return "(unknown)"
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def _count_comments(comments: Iterable[DownloadedComment]) -> int:
    total = 0
    for comment in comments:
        if comment.deleted or comment.dead:
            continue
        total += 1 + _count_comments(comment.children)
    return total


def _render_comment_tree(comments: Iterable[DownloadedComment], wrap_width: int, depth: int = 0) -> str:
    rendered_comments: List[str] = []
    for comment in comments:
        if comment.deleted or comment.dead:
            continue
        rendered_comments.append(_render_comment(comment, wrap_width=wrap_width, depth=depth))
    return "\n\n".join(rendered_comments)


def _render_comment(comment: DownloadedComment, wrap_width: int, depth: int) -> str:
    indent = "  " * depth
    header = f"{indent}- **{comment.by or '(unknown)'}** · {_format_timestamp(comment.time)}"
    body = _html_to_markdown(comment.text, wrap_width=wrap_width, base_indent=indent + "  ")
    children = _render_comment_tree(comment.children, wrap_width=wrap_width, depth=depth + 1)

    parts = [header]
    if body:
        parts.append(body)
    if children:
        if body:
            parts.append("")
        parts.append(children)
    return "\n".join(parts)


def _html_to_markdown(html_text: Optional[str], wrap_width: int, base_indent: str = "") -> str:
    if not html_text:
        return ""

    parser = _SimpleMarkdownHTMLParser()
    parser.feed(html_text)
    parser.close()
    markdown = parser.get_markdown()
    return _wrap_markdown(markdown, wrap_width=wrap_width, base_indent=base_indent)


def _wrap_markdown(markdown: str, wrap_width: int, base_indent: str = "") -> str:
    lines = markdown.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    output: List[str] = []
    paragraph: List[str] = []
    in_code_block = False

    def flush_paragraph() -> None:
        if not paragraph:
            return
        text = " ".join(part.strip() for part in paragraph if part.strip()).strip()
        paragraph.clear()
        if not text:
            return
        output.append(
            fill(
                text,
                width=wrap_width,
                initial_indent=base_indent,
                subsequent_indent=base_indent,
                break_long_words=False,
                break_on_hyphens=False,
            )
        )

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        if stripped == "```":
            flush_paragraph()
            output.append(f"{base_indent}```" if base_indent else "```")
            in_code_block = not in_code_block
            continue

        if in_code_block:
            output.append(f"{base_indent}{line}" if line else "")
            continue

        if not stripped:
            flush_paragraph()
            if output and output[-1] != "":
                output.append("")
            continue

        if stripped.startswith(("- ", "* ")) or (len(stripped) >= 4 and stripped[0].isdigit() and stripped[1:3] == ". "):
            flush_paragraph()
            output.append(f"{base_indent}{stripped}" if base_indent else stripped)
            continue

        paragraph.append(stripped)

    flush_paragraph()

    while output and output[-1] == "":
        output.pop()

    return "\n".join(output)


class _SimpleMarkdownHTMLParser(HTMLParser):
    """Small HTML-to-markdown converter for Hacker News item text."""

    def __init__(self) -> None:
        super().__init__()
        self._parts: List[str] = []
        self._link_stack: List[Optional[str]] = []
        self._list_stack: List[dict[str, object]] = []
        self._in_pre = False

    def get_markdown(self) -> str:
        text = "".join(self._parts)
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n")
        return text.strip()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        attr_map = {key: value for key, value in attrs}

        if tag in {"p", "div", "section"}:
            self._append_block_break()
        elif tag == "br":
            self._parts.append("\n")
        elif tag in {"strong", "b"}:
            self._parts.append("**")
        elif tag in {"em", "i"}:
            self._parts.append("*")
        elif tag == "code" and not self._in_pre:
            self._parts.append("`")
        elif tag == "pre":
            self._append_block_break()
            self._parts.append("```\n")
            self._in_pre = True
        elif tag == "a":
            self._link_stack.append(attr_map.get("href"))
            self._parts.append("[")
        elif tag in {"ul", "ol"}:
            self._append_block_break()
            self._list_stack.append({"tag": tag, "index": 0})
        elif tag == "li":
            self._append_block_break()
            indent = "  " * max(0, len(self._list_stack) - 1)
            bullet = "- "
            if self._list_stack:
                current = self._list_stack[-1]
                if current["tag"] == "ol":
                    current["index"] = int(current["index"]) + 1
                    bullet = f"{current['index']}. "
            self._parts.append(f"{indent}{bullet}")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"strong", "b"}:
            self._parts.append("**")
        elif tag in {"em", "i"}:
            self._parts.append("*")
        elif tag == "code" and not self._in_pre:
            self._parts.append("`")
        elif tag == "pre":
            self._parts.append("\n```\n")
            self._in_pre = False
        elif tag == "a":
            href = self._link_stack.pop() if self._link_stack else None
            if href:
                self._parts.append(f"]({href})")
            else:
                self._parts.append("]")
        elif tag in {"p", "div", "section"}:
            self._parts.append("\n\n")
        elif tag in {"ul", "ol"}:
            if self._list_stack:
                self._list_stack.pop()
            self._parts.append("\n\n")
        elif tag == "li":
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._in_pre:
            self._parts.append(data)
            return
        self._parts.append(unescape(data))

    def _append_block_break(self) -> None:
        if not self._parts:
            return
        if not self._parts[-1].endswith("\n\n"):
            self._parts.append("\n\n")