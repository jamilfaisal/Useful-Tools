"""Hacker News API client for fetching stories, comments, and other items."""

import logging
import math
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional, List, Any, Callable, cast

import requests
from requests.exceptions import RequestException

from .cache import SQLiteCache
from .config import get_config, Config

LOGGER = logging.getLogger(__name__)


class ItemType(Enum):
    """Types of Hacker News items."""
    STORY = "story"
    COMMENT = "comment"
    JOB = "job"
    POLL = "poll"
    POLL_OPTION = "poll_option"
    ASK_HN = "ask_hn"
    SHOW_HN = "show_hn"
    UNKNOWN = "unknown"


@dataclass
class HackerNewsItem:
    """Base class for all Hacker News items."""
    id: int
    deleted: bool = False
    dead: bool = False
    item_type: ItemType = ItemType.UNKNOWN
    by: Optional[str] = None
    time: Optional[int] = None
    text: Optional[str] = None
    kids: List[int] = field(default_factory=list)

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "HackerNewsItem | None":
        """Create an item from JSON data, handling missing fields safely."""
        if not data:
            return None

        item_type = _determine_item_type(data)

        factories = {
            ItemType.STORY: Story.from_json,
            ItemType.ASK_HN: Story.from_json,
            ItemType.SHOW_HN: Story.from_json,
            ItemType.COMMENT: Comment.from_json,
            ItemType.JOB: Job.from_json,
            ItemType.POLL: Poll.from_json,
            ItemType.POLL_OPTION: PollOption.from_json,
        }

        factory = cast(Callable[[dict[str, Any]], Optional[HackerNewsItem]], factories.get(item_type))
        if factory is not None:
            return factory(data)

        return cls(**_base_item_kwargs(data, item_type))


def _base_item_kwargs(data: dict[str, Any], item_type: ItemType) -> dict[str, Any]:
    return {
        "id": data.get("id", 0),
        "deleted": data.get("deleted", False),
        "dead": data.get("dead", False),
        "item_type": item_type,
        "by": data.get("by"),
        "time": data.get("time"),
        "text": data.get("text"),
        "kids": list(data.get("kids") or []),
    }


def _determine_item_type(data: dict[str, Any]) -> ItemType:
    """Determine the item type from JSON data."""
    if not data:
        return ItemType.UNKNOWN

    type_str = data.get("type", "")

    # Check for Ask HN and Show HN in title
    title = data.get("title", "") or ""
    title_lower = title.lower()

    if type_str == "story":
        if title_lower.startswith("ask hn:"):
            return ItemType.ASK_HN
        elif title_lower.startswith("show hn:"):
            return ItemType.SHOW_HN
        return ItemType.STORY
    elif type_str == "comment":
        return ItemType.COMMENT
    elif type_str == "job":
        return ItemType.JOB
    elif type_str == "poll":
        return ItemType.POLL
    elif type_str == "poll_option":
        return ItemType.POLL_OPTION

    return ItemType.UNKNOWN


@dataclass
class Story(HackerNewsItem):
    """A Hacker News story."""
    title: Optional[str] = None
    url: Optional[str] = None
    score: Optional[int] = None
    descendants: Optional[int] = None

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "Story | None":
        """Create a Story from JSON data."""
        if not data:
            return None

        return cls(
            **_base_item_kwargs(data, _determine_item_type(data)),
            title=data.get("title"),
            url=data.get("url"),
            score=data.get("score"),
            descendants=data.get("descendants"),
        )


@dataclass
class Comment(HackerNewsItem):
    """A Hacker News comment."""
    parent: Optional[int] = None

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "Comment | None":
        """Create a Comment from JSON data."""
        if not data:
            return None

        return cls(
            **_base_item_kwargs(data, ItemType.COMMENT),
            parent=data.get("parent"),
        )


@dataclass
class Job(HackerNewsItem):
    """A Hacker News job posting."""
    title: Optional[str] = None
    url: Optional[str] = None
    score: Optional[int] = None

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "Job | None":
        """Create a Job from JSON data."""
        if not data:
            return None

        return cls(
            **_base_item_kwargs(data, ItemType.JOB),
            title=data.get("title"),
            url=data.get("url"),
            score=data.get("score"),
        )


@dataclass
class Poll(HackerNewsItem):
    """A Hacker News poll."""
    title: Optional[str] = None
    score: Optional[int] = None
    parts: List[int] = field(default_factory=list)

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "Poll | None":
        """Create a Poll from JSON data."""
        if not data:
            return None

        return cls(
            **_base_item_kwargs(data, ItemType.POLL),
            title=data.get("title"),
            score=data.get("score"),
            parts=data.get("parts", []),
        )


@dataclass
class PollOption(HackerNewsItem):
    """A Hacker News poll option."""
    poll: Optional[int] = None
    score: Optional[int] = None

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "PollOption | None":
        """Create a PollOption from JSON data."""
        if not data:
            return None

        return cls(
            **_base_item_kwargs(data, ItemType.POLL_OPTION),
            poll=data.get("poll"),
            score=data.get("score"),
        )


class HackerNewsClient:
    """Client for interacting with the Hacker News Firebase API."""

    MAX_RETRIES = 3
    RETRY_DELAY = 1.0  # seconds

    def __init__(self, config: Optional[Config] = None) -> None:
        """Initialize the client with optional configuration."""
        self.config = config or get_config()
        self._session = requests.Session()
        self.cache = SQLiteCache(self.config.cache_db_path)

    def _make_request(self, endpoint: str) -> Optional[Any]:
        """Make a request to the API with retry logic and timeout."""
        url = f"{self.config.hn_api_base_url}/{endpoint}.json"

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                response = self._session.get(url, timeout=self.config.request_timeout)
                response.raise_for_status()
                return response.json()
            except (RequestException, ValueError) as exc:
                if attempt < self.MAX_RETRIES:
                    LOGGER.debug("Request failed for %s (%s/%s): %s", url, attempt, self.MAX_RETRIES, exc)
                    time.sleep(self.RETRY_DELAY * attempt)
                    continue
                LOGGER.warning("Request failed for %s after %s attempts: %s", url, self.MAX_RETRIES, exc)
                return None

        return None

    def get_newest_story_ids(self) -> List[int]:
        """Fetch IDs of the newest stories."""
        data = self._make_request("newstories")
        if isinstance(data, list):
            return [item for item in data if isinstance(item, int)]
        return []

    def get_top_story_ids(self) -> List[int]:
        """Fetch IDs of the top stories."""
        data = self._make_request("topstories")
        if isinstance(data, list):
            return [item for item in data if isinstance(item, int)]
        return []

    def discover_stories(
            self,
            days_to_look_back: Optional[int] = None,
            minimum_score: Optional[int] = None,
            top_percent_by_score: Optional[float] = None,
    ) -> List[Story]:
        """Discover recent stories sorted by score descending."""
        if days_to_look_back is not None:
            days = days_to_look_back
        else:
            days = self.config.days_to_look_back

        minimum: int = minimum_score if minimum_score is not None else self.config.minimum_score
        top_percent: float = (
            top_percent_by_score if top_percent_by_score is not None else self.config.top_percent_by_score
        )

        if days < 0:
            raise ValueError("days_to_look_back must be greater than or equal to 0")
        if minimum < 0:
            raise ValueError("minimum_score must be greater than or equal to 0")
        if top_percent < 0 or top_percent > 100:
            raise ValueError("top_percent_by_score must be between 0 and 100")
        if minimum and top_percent:
            raise ValueError("Use either minimum_score or top_percent_by_score, not both")

        cutoff_time = None
        if days > 0:
            cutoff_time = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp())

        discovered_stories: List[Story] = []
        for story_id in self.get_newest_story_ids():
            item = self.get_item(story_id)
            if not isinstance(item, Story):
                continue
            if item.deleted or item.dead:
                continue
            if not is_story_item(item):
                continue
            if cutoff_time is not None:
                if item.time is None:
                    continue
                if item.time < cutoff_time:
                    break
            discovered_stories.append(item)

        filtered_stories = self._filter_discovered_stories_by_popularity(
            discovered_stories,
            minimum_score=minimum,
            top_percent_by_score=top_percent,
        )
        return sorted(filtered_stories, key=self._story_sort_key, reverse=True)

    def get_item(self, item_id: int, parent_id: Optional[int] = None) -> Optional[HackerNewsItem]:
        """Fetch an individual item by ID, using cache if available."""
        cached_item = self.cache.get_item(item_id)
        if cached_item:
            return HackerNewsItem.from_json(cached_item)

        data = self._make_request(f"item/{item_id}")
        if data:
            if data.get("type") == "comment" and parent_id is not None:
                data["parent"] = parent_id
            self.cache.save_item(data)
            return HackerNewsItem.from_json(data)
        return None

    def get_story(self, story_id: int) -> Optional[Story]:
        """Fetch a story by ID."""
        item = self.get_item(story_id)
        if isinstance(item, Story):
            return item
        return None

    def get_comment(self, comment_id: int) -> Optional[Comment]:
        """Fetch a comment by ID."""
        item = self.get_item(comment_id)
        if isinstance(item, Comment):
            return item
        return None

    def get_job(self, job_id: int) -> Optional[Job]:
        """Fetch a job by ID."""
        item = self.get_item(job_id)
        if isinstance(item, Job):
            return item
        return None

    def get_poll(self, poll_id: int) -> Optional[Poll]:
        """Fetch a poll by ID."""
        item = self.get_item(poll_id)
        if isinstance(item, Poll):
            return item
        return None

    def get_poll_option(self, option_id: int) -> Optional[PollOption]:
        """Fetch a poll option by ID."""
        item = self.get_item(option_id)
        if isinstance(item, PollOption):
            return item
        return None

    def close(self) -> None:
        """Close the HTTP session."""
        self._session.close()

    @staticmethod
    def _story_sort_key(story: Story) -> tuple[int, int, int]:
        return (story.score or 0, story.time or 0, story.id)

    def _filter_discovered_stories_by_popularity(
            self,
            stories: List[Story],
            *,
            minimum_score: int,
            top_percent_by_score: float,
    ) -> List[Story]:
        if top_percent_by_score > 0:
            ranked_stories = sorted(stories, key=self._story_sort_key, reverse=True)
            number_to_keep = max(1, math.ceil(len(ranked_stories) * (top_percent_by_score / 100.0)))
            return ranked_stories[:number_to_keep]

        if minimum_score > 0:
            return [story for story in stories if (story.score or 0) >= minimum_score]

        return stories

    def __enter__(self) -> "HackerNewsClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()


# Unit-testable helper functions

def is_ask_hn_story(story: Story) -> bool:
    """Check if a story is an Ask HN post."""
    return story.item_type == ItemType.ASK_HN


def is_show_hn_story(story: Story) -> bool:
    """Check if a story is a Show HN post."""
    return story.item_type == ItemType.SHOW_HN


def is_job_item(item: HackerNewsItem) -> bool:
    """Check if an item is a job posting."""
    return item.item_type == ItemType.JOB


def is_poll_item(item: HackerNewsItem) -> bool:
    """Check if an item is a poll."""
    return item.item_type == ItemType.POLL


def is_story_item(item: HackerNewsItem) -> bool:
    """Check if an item is a story (including Ask HN and Show HN)."""
    return item.item_type in (ItemType.STORY, ItemType.ASK_HN, ItemType.SHOW_HN)


def is_comment_item(item: HackerNewsItem) -> bool:
    """Check if an item is a comment."""
    return item.item_type == ItemType.COMMENT


def get_item_type_name(item: HackerNewsItem) -> str:
    """Get a human-readable name for the item type."""
    return item.item_type.value
