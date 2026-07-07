"""Recursive story downloader that preserves Hacker News reply structure."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .config import Config, get_config
from .hn_api import HackerNewsClient, Story, Comment, HackerNewsItem, ItemType


@dataclass
class DownloadedComment(Comment):
    children: list[DownloadedComment] = field(default_factory=list)


@dataclass
class DownloadedStory(Story):
    comments: list[DownloadedComment] = field(default_factory=list)


class RecursiveDownloader:
    def __init__(self, config: Optional[Config] = None, client: Optional[HackerNewsClient] = None) -> None:
        self._owns_client = client is None
        self.client = client or HackerNewsClient(config or get_config())
        self.downloaded_ids: set[int] = set()

    @staticmethod
    def _copy_comment(comment: Comment, parent_id: Optional[int]) -> DownloadedComment:
        return DownloadedComment(
            id=comment.id,
            deleted=comment.deleted,
            dead=comment.dead,
            item_type=comment.item_type,
            by=comment.by,
            time=comment.time,
            text=comment.text,
            kids=list(comment.kids),
            parent=parent_id,
        )

    @staticmethod
    def _copy_story(story: Story) -> DownloadedStory:
        return DownloadedStory(
            id=story.id,
            deleted=story.deleted,
            dead=story.dead,
            item_type=story.item_type,
            by=story.by,
            time=story.time,
            text=story.text,
            kids=list(story.kids),
            title=story.title,
            url=story.url,
            score=story.score,
            descendants=story.descendants,
        )

    def _fetch_item_recursive(self, item_id: int, parent_id: Optional[int] = None) -> Optional[HackerNewsItem]:
        if item_id in self.downloaded_ids:
            return None

        item = self.client.get_item(item_id)
        if not item or item.deleted or item.dead or item.item_type == ItemType.JOB:
            return None

        self.downloaded_ids.add(item_id)

        if isinstance(item, Comment):
            downloaded_comment = self._copy_comment(item, parent_id)
            for kid_id in item.kids:
                child_comment = self._fetch_item_recursive(kid_id, item.id)
                if isinstance(child_comment, DownloadedComment):
                    downloaded_comment.children.append(child_comment)
            return downloaded_comment

        if isinstance(item, Story):
            downloaded_story = self._copy_story(item)
            for kid_id in item.kids:
                comment = self._fetch_item_recursive(kid_id, item.id)
                if isinstance(comment, DownloadedComment):
                    downloaded_story.comments.append(comment)
            return downloaded_story

        return None

    def download_story_with_comments(self, story_id: int) -> Optional[DownloadedStory]:
        self.downloaded_ids.clear()
        story = self._fetch_item_recursive(story_id)
        if isinstance(story, DownloadedStory):
            return story
        return None

    def close(self) -> None:
        if self._owns_client:
            self.client.close()

    def __enter__(self) -> "RecursiveDownloader":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
