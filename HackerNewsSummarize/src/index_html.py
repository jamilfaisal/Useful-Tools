"""Static HTML index rendering for Hacker News story output."""

from __future__ import annotations

import re
from html import escape
from pathlib import Path
from typing import Iterable

from .hn_api import Story


def render_index_html(stories: Iterable[Story], output_dir: str | Path = Path("output")) -> str:
    """Render a responsive static HTML index for a collection of stories."""
    cards = [_render_story_card(story) for story in stories]
    story_label = "story" if len(cards) == 1 else "stories"

    if cards:
        cards_html = "\n".join(cards)
    else:
        cards_html = (
            '<section class="empty-state">'
            "<h2>No stories yet</h2>"
            "<p>Run the daily workflow to populate this index.</p>"
            "</section>"
        )

    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1">',
            "  <title>Hacker News Index</title>",
            "  <style>",
            "    :root {",
            "      color-scheme: dark;",
            "      --bg: #0b1020;",
            "      --bg-elevated: #11172a;",
            "      --bg-card: rgba(17, 23, 42, 0.92);",
            "      --border: rgba(148, 163, 184, 0.18);",
            "      --text: #e2e8f0;",
            "      --muted: #94a3b8;",
            "      --accent: #f59e0b;",
            "      --accent-soft: rgba(245, 158, 11, 0.16);",
            "      --shadow: 0 24px 60px rgba(2, 6, 23, 0.45);",
            "    }",
            "    * { box-sizing: border-box; }",
            "    body {",
            "      margin: 0;",
            "      min-height: 100vh;",
            "      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;",
            "      background:",
            "        radial-gradient(circle at top, rgba(245, 158, 11, 0.16), transparent 36%),",
            "        linear-gradient(180deg, #080c18 0%, #0b1020 45%, #070b14 100%);",
            "      color: var(--text);",
            "    }",
            "    .shell {",
            "      width: min(1120px, calc(100% - 2rem));",
            "      margin: 0 auto;",
            "      padding: 2rem 0 3rem;",
            "    }",
            "    header {",
            "      display: flex;",
            "      flex-wrap: wrap;",
            "      gap: 1rem;",
            "      align-items: end;",
            "      justify-content: space-between;",
            "      margin-bottom: 1.75rem;",
            "      padding: 1.25rem 1.25rem 1rem;",
            "      border: 1px solid var(--border);",
            "      border-radius: 24px;",
            "      background: linear-gradient(180deg, rgba(17, 23, 42, 0.88), rgba(17, 23, 42, 0.68));",
            "      box-shadow: var(--shadow);",
            "      backdrop-filter: blur(10px);",
            "    }",
            "    h1 {",
            "      margin: 0 0 0.35rem;",
            "      font-size: clamp(1.7rem, 3vw, 2.75rem);",
            "      line-height: 1.05;",
            "      letter-spacing: -0.04em;",
            "    }",
            "    .lede {",
            "      margin: 0;",
            "      color: var(--muted);",
            "      max-width: 60ch;",
            "    }",
            "    .count {",
            "      margin: 0;",
            "      color: var(--muted);",
            "      font-size: 0.95rem;",
            "      white-space: nowrap;",
            "    }",
            "    .grid {",
            "      display: grid;",
            "      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));",
            "      gap: 1rem;",
            "    }",
            "    .card {",
            "      display: flex;",
            "      flex-direction: column;",
            "      gap: 1rem;",
            "      padding: 1.15rem;",
            "      border: 1px solid var(--border);",
            "      border-radius: 22px;",
            "      background: var(--bg-card);",
            "      box-shadow: var(--shadow);",
            "      backdrop-filter: blur(10px);",
            "    }",
            "    .story-title {",
            "      margin: 0;",
            "      font-size: 1.12rem;",
            "      line-height: 1.35;",
            "      letter-spacing: -0.02em;",
            "    }",
            "    .story-title a {",
            "      color: var(--text);",
            "      text-decoration: none;",
            "    }",
            "    .story-title a:hover {",
            "      color: #fff;",
            "    }",
            "    .meta {",
            "      display: flex;",
            "      flex-wrap: wrap;",
            "      gap: 0.55rem;",
            "      color: var(--muted);",
            "      font-size: 0.94rem;",
            "    }",
            "    .badge {",
            "      display: inline-flex;",
            "      align-items: center;",
            "      gap: 0.4rem;",
            "      padding: 0.35rem 0.65rem;",
            "      border-radius: 999px;",
            "      background: var(--accent-soft);",
            "      color: #fcd34d;",
            "      border: 1px solid rgba(245, 158, 11, 0.22);",
            "    }",
            "    .links {",
            "      display: flex;",
            "      flex-wrap: wrap;",
            "      gap: 0.65rem;",
            "      margin-top: auto;",
            "    }",
            "    .links a {",
            "      display: inline-flex;",
            "      align-items: center;",
            "      justify-content: center;",
            "      padding: 0.6rem 0.85rem;",
            "      border-radius: 12px;",
            "      background: rgba(148, 163, 184, 0.08);",
            "      border: 1px solid rgba(148, 163, 184, 0.14);",
            "      color: var(--text);",
            "      text-decoration: none;",
            "      font-size: 0.92rem;",
            "    }",
            "    .links a:hover {",
            "      border-color: rgba(245, 158, 11, 0.55);",
            "      background: rgba(245, 158, 11, 0.12);",
            "    }",
            "    .empty-state {",
            "      padding: 3rem 1.5rem;",
            "      border: 1px dashed var(--border);",
            "      border-radius: 22px;",
            "      background: rgba(17, 23, 42, 0.7);",
            "      text-align: center;",
            "      color: var(--muted);",
            "    }",
            "    .empty-state h2 {",
            "      margin: 0 0 0.5rem;",
            "      color: var(--text);",
            "    }",
            "    @media (max-width: 640px) {",
            "      .shell { width: min(100% - 1rem, 1120px); padding-top: 0.5rem; }",
            "      header { padding: 1rem; border-radius: 20px; }",
            "      .card { border-radius: 18px; }",
            "    }",
            "  </style>",
            "</head>",
            "<body>",
            '  <main class="shell">',
            "    <header>",
            "      <div>",
            "        <h1>Hacker News Index</h1>",
            "        <p class=\"lede\">A static overview of the most relevant stories, with direct links to the article, discussion, and saved folder.</p>",
            "      </div>",
            f'      <p class="count">{len(cards)} {story_label}</p>',
            "    </header>",
            '    <section class="grid">',
            cards_html,
            "    </section>",
            "  </main>",
            "</body>",
            "</html>",
        ]
    )


def write_index_html(
        stories: Iterable[Story],
        output_path: str | Path,
        output_dir: str | Path = Path("output"),
) -> Path:
    """Write the rendered HTML index to disk and return the file path."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_index_html(stories, output_dir=output_dir), encoding="utf-8")
    return path


def story_folder_name(story: Story) -> str:
    """Create a stable folder name for a story output directory."""
    raw_title = (story.title or "").strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", raw_title).strip("-")
    if not slug:
        slug = "story"
    return f"{story.id}-{slug}"


def _render_story_card(story: Story) -> str:
    title = escape(story.title or f"Hacker News Story {story.id}")
    article_url = story.url or f"https://news.ycombinator.com/item?id={story.id}"
    hn_url = f"https://news.ycombinator.com/item?id={story.id}"
    folder_url = f"{story_folder_name(story)}/"
    score = story.score if story.score is not None else 0
    comment_count = story.descendants if story.descendants is not None else 0

    return "\n".join(
        [
            '      <article class="card">',
            f'        <h2 class="story-title"><a href="{escape(article_url, quote=True)}" target="_blank" rel="noreferrer">{title}</a></h2>',
            '        <div class="meta">',
            f'          <span class="badge">{score} points</span>',
            f'          <span>{comment_count} comments</span>',
            "        </div>",
            '        <div class="links">',
            f'          <a href="{escape(article_url, quote=True)}" target="_blank" rel="noreferrer">Article</a>',
            f'          <a href="{escape(hn_url, quote=True)}" target="_blank" rel="noreferrer">Hacker News</a>',
            f'          <a href="{escape(folder_url, quote=True)}">Folder</a>',
            "        </div>",
            "      </article>",
        ]
    )
