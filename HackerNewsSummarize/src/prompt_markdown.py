"""Template-driven prompt generation for Hacker News analysis."""

from __future__ import annotations

from pathlib import Path

DEFAULT_PROMPT_TEMPLATE_PATH = Path(__file__).with_name("prompt_template.md")


def render_prompt_markdown(template_path: str | Path | None = None) -> str:
    """Render the reusable ChatGPT prompt from a markdown template."""
    path = Path(template_path) if template_path is not None else DEFAULT_PROMPT_TEMPLATE_PATH
    return path.read_text(encoding="utf-8")


def write_prompt_markdown(
        output_path: str | Path,
        template_path: str | Path | None = None,
) -> Path:
    """Write the rendered prompt markdown to disk and return the file path."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_prompt_markdown(template_path=template_path), encoding="utf-8")
    return path
