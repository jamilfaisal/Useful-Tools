"""Main entry point for the Hacker News Daily Companion."""

from __future__ import annotations

import logging
import json
from pathlib import Path
from typing import List, Set

from .config import Config, get_config
from .context_markdown import write_context_markdown
from .index_html import story_folder_name, write_index_html
from .hn_api import HackerNewsClient, Story
from .prompt_markdown import write_prompt_markdown
from .recursive_downloader import RecursiveDownloader, DownloadedStory

PROCESSED_STORIES_FILENAME = "processed_stories.json"
LOGGER = logging.getLogger(__name__)


def discover_stories(config: Config | None = None) -> List[Story]:
    """Discover recent stories using the configured lookback and popularity settings."""
    active_config = config or get_config()
    with HackerNewsClient(active_config) as client:
        return client.discover_stories()


def _processed_stories_path(output_dir: Path) -> Path:
    return output_dir / PROCESSED_STORIES_FILENAME


def _load_processed_story_ids(output_dir: Path) -> Set[int]:
    path = _processed_stories_path(output_dir)
    if not path.exists():
        return set()

    try:
        raw_ids = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        LOGGER.warning("Could not read %s; starting with an empty processed-story list.", path)
        return set()

    if not isinstance(raw_ids, list):
        return set()

    processed_ids: Set[int] = set()
    for value in raw_ids:
        try:
            processed_ids.add(int(value))
        except (TypeError, ValueError):
            continue
    return processed_ids


def _save_processed_story_ids(output_dir: Path, processed_ids: Set[int]) -> Path:
    path = _processed_stories_path(output_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(".tmp")
    temp_path.write_text(json.dumps(sorted(processed_ids), indent=2) + "\n", encoding="utf-8")
    temp_path.replace(path)
    return path


def _write_story_outputs(story: DownloadedStory, config: Config) -> Path:
    story_dir = config.output_dir / story_folder_name(story)
    story_dir.mkdir(parents=True, exist_ok=True)
    write_context_markdown(story, story_dir / "context.md")
    write_prompt_markdown(story_dir / "prompt.md")
    return story_dir


def main() -> None:
    """Run the daily Hacker News workflow."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    config = get_config()
    config.output_dir.mkdir(parents=True, exist_ok=True)

    LOGGER.info("Discovering candidate stories...")
    stories = discover_stories(config)
    LOGGER.info("Discovered %s candidate stories.", len(stories))

    processed_story_ids = _load_processed_story_ids(config.output_dir)
    if processed_story_ids:
        stories_to_process = [story for story in stories if story.id not in processed_story_ids]
        skipped = len(stories) - len(stories_to_process)
        LOGGER.info("Skipping %s already-processed stories.", skipped)
    else:
        stories_to_process = stories

    successful_stories: List[Story] = []
    next_processed_ids = set(processed_story_ids)

    with RecursiveDownloader(config=config) as downloader:
        for index, story in enumerate(stories_to_process, start=1):
            score = story.score or 0
            story_title = story.title or "(untitled)"
            LOGGER.info("[%s/%s] Processing %s: %s", index, len(stories_to_process), story.id, story_title)
            try:
                LOGGER.info("  Downloading comment tree and caching items...")
                downloaded_story = downloader.download_story_with_comments(story.id)
                if downloaded_story is None:
                    raise RuntimeError("download returned no story")

                LOGGER.info("  Generating output folder...")
                story_dir = _write_story_outputs(downloaded_story, config)
                LOGGER.info("  Wrote %s", story_dir)

                successful_stories.append(downloaded_story)
                next_processed_ids.add(downloaded_story.id)
                _save_processed_story_ids(config.output_dir, next_processed_ids)
                LOGGER.info("  Done (%s points)", score)
            except Exception as exc:  # pragma: no cover - exercised through orchestration failures
                LOGGER.error("  Failed: %s", exc)
                continue

    LOGGER.info("Generating index.html...")
    index_path = write_index_html(successful_stories, config.output_dir / "index.html", output_dir=config.output_dir)
    LOGGER.info("Wrote %s", index_path)
    LOGGER.info("Finished %s story folder(s).", len(successful_stories))


if __name__ == "__main__":
    main()
