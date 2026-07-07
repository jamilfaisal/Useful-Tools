"""Unit tests for the Hacker News API client."""

import sqlite3
import tempfile
import unittest
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

import requests
from unittest.mock import patch, MagicMock

from src.hn_api import (
    ItemType,
    HackerNewsItem,
    Story,
    Comment,
    Job,
    Poll,
    PollOption,
    HackerNewsClient,
    is_ask_hn_story,
    is_show_hn_story,
    is_job_item,
    is_poll_item,
    is_story_item,
    is_comment_item,
    get_item_type_name,
    _determine_item_type,
)
from src.config import Config


class TestItemTypeDetection(unittest.TestCase):
    """Tests for item type detection."""

    def test_story_type(self) -> None:
        """Test regular story detection."""
        data = {"type": "story", "id": 1, "title": "A regular story"}
        self.assertEqual(_determine_item_type(data), ItemType.STORY)

    def test_ask_hn_story(self) -> None:
        """Test Ask HN story detection."""
        data = {"type": "story", "id": 1, "title": "Ask HN: What do you think?"}
        self.assertEqual(_determine_item_type(data), ItemType.ASK_HN)

    def test_show_hn_story(self) -> None:
        """Test Show HN story detection."""
        data = {"type": "story", "id": 1, "title": "Show HN: My new project"}
        self.assertEqual(_determine_item_type(data), ItemType.SHOW_HN)

    def test_ask_hn_case_insensitive(self) -> None:
        """Test Ask HN detection is case insensitive."""
        data = {"type": "story", "id": 1, "title": "ask hn: question"}
        self.assertEqual(_determine_item_type(data), ItemType.ASK_HN)

    def test_show_hn_case_insensitive(self) -> None:
        """Test Show HN detection is case insensitive."""
        data = {"type": "story", "id": 1, "title": "SHOW HN: My app"}
        self.assertEqual(_determine_item_type(data), ItemType.SHOW_HN)

    def test_comment_type(self) -> None:
        """Test comment detection."""
        data = {"type": "comment", "id": 1}
        self.assertEqual(_determine_item_type(data), ItemType.COMMENT)

    def test_job_type(self) -> None:
        """Test job detection."""
        data = {"type": "job", "id": 1}
        self.assertEqual(_determine_item_type(data), ItemType.JOB)

    def test_poll_type(self) -> None:
        """Test poll detection."""
        data = {"type": "poll", "id": 1}
        self.assertEqual(_determine_item_type(data), ItemType.POLL)

    def test_poll_option_type(self) -> None:
        """Test poll option detection."""
        data = {"type": "poll_option", "id": 1}
        self.assertEqual(_determine_item_type(data), ItemType.POLL_OPTION)

    def test_unknown_type(self) -> None:
        """Test unknown type for missing or unrecognized type."""
        data = {"id": 1}
        self.assertEqual(_determine_item_type(data), ItemType.UNKNOWN)

        data = {"type": "unknown", "id": 1}
        self.assertEqual(_determine_item_type(data), ItemType.UNKNOWN)


class TestHackerNewsItemFromJSON(unittest.TestCase):
    """Tests for JSON deserialization."""

    def test_story_from_json(self) -> None:
        """Test Story creation from JSON."""
        data = {
            "id": 123,
            "type": "story",
            "title": "Test Story",
            "url": "https://example.com",
            "by": "user1",
            "time": 1234567890,
            "score": 100,
            "descendants": 50,
            "kids": [1, 2, 3],
        }
        story = Story.from_json(data)
        self.assertIsNotNone(story)
        assert isinstance(story, Story)
        self.assertEqual(story.id, 123)
        self.assertEqual(story.title, "Test Story")
        self.assertEqual(story.url, "https://example.com")
        self.assertEqual(story.by, "user1")
        self.assertEqual(story.score, 100)
        self.assertEqual(story.descendants, 50)
        self.assertEqual(story.kids, [1, 2, 3])

    def test_story_missing_fields(self) -> None:
        """Test Story handles missing fields gracefully."""
        data = {"id": 123, "type": "story"}
        story = Story.from_json(data)
        self.assertIsNotNone(story)
        assert isinstance(story, Story)
        self.assertEqual(story.id, 123)
        self.assertIsNone(story.title)
        self.assertIsNone(story.url)
        self.assertEqual(story.kids, [])

    def test_comment_from_json(self) -> None:
        """Test Comment creation from JSON."""
        data = {
            "id": 456,
            "type": "comment",
            "by": "user2",
            "text": "This is a comment",
            "kids": [7, 8],
        }
        comment = Comment.from_json(data)
        self.assertIsNotNone(comment)
        assert isinstance(comment, Comment)
        self.assertEqual(comment.id, 456)
        self.assertEqual(comment.by, "user2")
        self.assertEqual(comment.text, "This is a comment")
        self.assertEqual(comment.kids, [7, 8])

    def test_job_from_json(self) -> None:
        """Test Job creation from JSON."""
        data = {
            "id": 789,
            "type": "job",
            "title": "Job Opening",
            "url": "https://jobs.example.com",
            "by": "employer",
        }
        job = Job.from_json(data)
        self.assertIsNotNone(job)
        assert isinstance(job, Job)
        self.assertEqual(job.id, 789)
        self.assertEqual(job.title, "Job Opening")
        self.assertEqual(job.url, "https://jobs.example.com")

    def test_poll_from_json(self) -> None:
        """Test Poll creation from JSON."""
        data = {
            "id": 100,
            "type": "poll",
            "title": "Favorite language?",
            "parts": [1, 2, 3],
        }
        poll = Poll.from_json(data)
        self.assertIsNotNone(poll)
        assert isinstance(poll, Poll)
        self.assertEqual(poll.id, 100)
        self.assertEqual(poll.title, "Favorite language?")
        self.assertEqual(poll.parts, [1, 2, 3])

    def test_poll_option_from_json(self) -> None:
        """Test PollOption creation from JSON."""
        data = {
            "id": 101,
            "type": "poll_option",
            "poll": 100,
            "text": "Python",
            "score": 50,
        }
        option = PollOption.from_json(data)
        self.assertIsNotNone(option)
        assert isinstance(option, PollOption)
        self.assertEqual(option.id, 101)
        self.assertEqual(option.poll, 100)
        self.assertEqual(option.text, "Python")

    def test_base_item_from_json(self) -> None:
        """Test base HackerNewsItem factory method."""
        data = {
            "id": 123,
            "type": "story",
            "title": "Test Story",
        }
        item = HackerNewsItem.from_json(data)
        self.assertIsNotNone(item)
        self.assertIsInstance(item, Story)
            assert isinstance(item, Story)

    def test_base_item_none_data(self) -> None:
        """Test base item handles None data."""
        item = HackerNewsItem.from_json(None)
        self.assertIsNone(item)


class TestHelperFunctions(unittest.TestCase):
    """Tests for helper functions."""

    def test_is_ask_hn_story(self) -> None:
        """Test Ask HN detection helper."""
        ask_story = Story(id=1, item_type=ItemType.ASK_HN)
        regular_story = Story(id=2, item_type=ItemType.STORY)
        self.assertTrue(is_ask_hn_story(ask_story))
        self.assertFalse(is_ask_hn_story(regular_story))

    def test_is_show_hn_story(self) -> None:
        """Test Show HN detection helper."""
        show_story = Story(id=1, item_type=ItemType.SHOW_HN)
        regular_story = Story(id=2, item_type=ItemType.STORY)
        self.assertTrue(is_show_hn_story(show_story))
        self.assertFalse(is_show_hn_story(regular_story))

    def test_is_job_item(self) -> None:
        """Test job detection helper."""
        job = Job(id=1, item_type=ItemType.JOB)
        story = Story(id=2, item_type=ItemType.STORY)
        self.assertTrue(is_job_item(job))
        self.assertFalse(is_job_item(story))

    def test_is_poll_item(self) -> None:
        """Test poll detection helper."""
        poll = Poll(id=1, item_type=ItemType.POLL)
        story = Story(id=2, item_type=ItemType.STORY)
        self.assertTrue(is_poll_item(poll))
        self.assertFalse(is_poll_item(story))

    def test_is_story_item(self) -> None:
        """Test story detection helper includes Ask HN and Show HN."""
        story = Story(id=1, item_type=ItemType.STORY)
        ask_story = Story(id=2, item_type=ItemType.ASK_HN)
        show_story = Story(id=3, item_type=ItemType.SHOW_HN)
        job = Job(id=4, item_type=ItemType.JOB)

        self.assertTrue(is_story_item(story))
        self.assertTrue(is_story_item(ask_story))
        self.assertTrue(is_story_item(show_story))
        self.assertFalse(is_story_item(job))

    def test_is_comment_item(self) -> None:
        """Test comment detection helper."""
        comment = Comment(id=1, item_type=ItemType.COMMENT)
        story = Story(id=2, item_type=ItemType.STORY)
        self.assertTrue(is_comment_item(comment))
        self.assertFalse(is_comment_item(story))

    def test_get_item_type_name(self) -> None:
        """Test item type name helper."""
        story = Story(id=1, item_type=ItemType.STORY)
        self.assertEqual(get_item_type_name(story), "story")


class TestHackerNewsClient(unittest.TestCase):
    """Tests for the Hacker News client."""

    def test_client_initialization(self) -> None:
        """Test client can be initialized."""
        client = HackerNewsClient()
        self.assertIsNotNone(client.config)
        self.assertIsNotNone(client._session)
        client.close()

    @patch("src.hn_api.requests.Session")
    def test_get_newest_story_ids(self, mock_session_class) -> None:
        """Test fetching newest story IDs."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = [1, 2, 3, 4, 5]
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        client = HackerNewsClient()
        ids = client.get_newest_story_ids()

        self.assertEqual(ids, [1, 2, 3, 4, 5])
        client.close()

    @patch("src.hn_api.requests.Session")
    def test_get_top_story_ids(self, mock_session_class) -> None:
        """Test fetching top story IDs."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = [10, 20, 30]
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        client = HackerNewsClient()
        ids = client.get_top_story_ids()

        self.assertEqual(ids, [10, 20, 30])
        client.close()

    @patch("src.hn_api.requests.Session")
    def test_get_item(self, mock_session_class) -> None:
        """Test fetching an item."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": 123,
            "type": "story",
            "title": "Test Story",
        }
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        client = HackerNewsClient()
        item = client.get_item(123)

        self.assertIsInstance(item, Story)
        assert isinstance(item, Story)
        self.assertEqual(item.id, 123)
        self.assertEqual(item.title, "Test Story")
        client.close()

    @patch("src.hn_api.requests.Session")
    def test_get_item_uses_cache_without_http(self, mock_session_class) -> None:
        """Test cached items are returned without another API call."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / "cache.db"
            client = HackerNewsClient(config=Config(cache_db_path=cache_path))
            try:
                client.cache.save_item(
                    {
                        "id": 321,
                        "type": "story",
                        "title": "Cached Story",
                        "kids": [],
                    }
                )

                item = client.get_item(321)

                self.assertIsInstance(item, Story)
                self.assertEqual(item.id, 321)
                self.assertEqual(item.title, "Cached Story")
                mock_session.get.assert_not_called()

                with closing(sqlite3.connect(cache_path)) as connection:
                    row = connection.execute(
                        "SELECT raw_json, downloaded_at FROM items WHERE id = ?",
                        (321,),
                    ).fetchone()

                self.assertIsNotNone(row)
                self.assertIn('"title": "Cached Story"', row[0])
                self.assertTrue(row[1])
            finally:
                client.close()

    def test_discover_stories_filters_by_age_popularity_and_type(self) -> None:
        """Test story discovery applies date, type, and score filters."""
        fixed_now = datetime(2026, 7, 7, tzinfo=timezone.utc)
        recent_time = int(datetime(2026, 7, 6, tzinfo=timezone.utc).timestamp())
        old_time = int(datetime(2026, 7, 3, tzinfo=timezone.utc).timestamp())

        with tempfile.TemporaryDirectory() as temp_dir:
            client = HackerNewsClient(
                config=Config(
                    days_to_look_back=2,
                    minimum_score=100,
                    cache_db_path=Path(temp_dir) / "cache.db",
                )
            )
            try:
                setattr(client, "get_newest_story_ids", MagicMock(return_value=[2, 3, 4, 5, 6, 7, 1]))
                setattr(client, "get_item", MagicMock(
                    side_effect=[
                        Story(id=2, item_type=ItemType.JOB, title="Job", time=recent_time, score=999),
                        Story(id=3, item_type=ItemType.STORY, title="Too Small", time=recent_time, score=40),
                        Story(id=4, item_type=ItemType.ASK_HN, title="Ask HN: Help", time=recent_time, score=150),
                        Story(id=5, item_type=ItemType.SHOW_HN, title="Show HN: Project", time=recent_time, score=220),
                        Story(id=6, item_type=ItemType.STORY, title="Deleted", time=recent_time, score=800,
                              deleted=True),
                        Story(id=7, item_type=ItemType.STORY, title="Best Story", time=recent_time, score=300),
                        Story(id=1, item_type=ItemType.STORY, title="Old Story", time=old_time, score=400),
                    ]
                ))

                with patch("src.hn_api.datetime") as mock_datetime:
                    mock_datetime.now.return_value = fixed_now
                    stories = client.discover_stories()

                self.assertEqual([story.id for story in stories], [7, 5, 4])
                self.assertEqual([story.score for story in stories], [300, 220, 150])
            finally:
                client.close()

    def test_discover_stories_can_use_top_percent(self) -> None:
        """Test story discovery can keep the top percentage by score."""
        with tempfile.TemporaryDirectory() as temp_dir:
            recent_time = int(datetime(2026, 7, 6, tzinfo=timezone.utc).timestamp())
            client = HackerNewsClient(
                config=Config(
                    days_to_look_back=3,
                    top_percent_by_score=50.0,
                    cache_db_path=Path(temp_dir) / "cache.db",
                )
            )
            try:
                setattr(client, "get_newest_story_ids", MagicMock(return_value=[10, 11, 12, 13]))
                setattr(client, "get_item", MagicMock(
                    side_effect=[
                        Story(id=10, item_type=ItemType.STORY, title="One", time=recent_time, score=10),
                        Story(id=11, item_type=ItemType.SHOW_HN, title="Two", time=recent_time, score=40),
                        Story(id=12, item_type=ItemType.ASK_HN, title="Three", time=recent_time, score=20),
                        Story(id=13, item_type=ItemType.STORY, title="Four", time=recent_time, score=30),
                    ]
                ))

                with patch("src.hn_api.datetime") as mock_datetime:
                    mock_datetime.now.return_value = datetime(2026, 7, 7, tzinfo=timezone.utc)
                    stories = client.discover_stories()

                self.assertEqual([story.id for story in stories], [11, 13])
            finally:
                client.close()

    @patch("src.hn_api.requests.Session")
    def test_retry_on_timeout(self, mock_session_class) -> None:
        """Test retry logic on timeout."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = [1, 2, 3]
        mock_response.raise_for_status = MagicMock()

        # First call times out, second succeeds
        mock_session.get.side_effect = [
            requests.exceptions.Timeout("Connection timed out"),
            mock_response,
        ]
        mock_session_class.return_value = mock_session

        client = HackerNewsClient()
        ids = client.get_newest_story_ids()

        self.assertEqual(ids, [1, 2, 3])
        self.assertEqual(mock_session.get.call_count, 2)
        client.close()

    @patch("src.hn_api.requests.Session")
    def test_retry_on_connection_error(self, mock_session_class) -> None:
        """Test retry logic on connection error."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = [1, 2, 3]
        mock_response.raise_for_status = MagicMock()

        # First call fails, second succeeds
        mock_session.get.side_effect = [
            requests.exceptions.ConnectionError("Connection failed"),
            mock_response,
        ]
        mock_session_class.return_value = mock_session

        client = HackerNewsClient()
        ids = client.get_newest_story_ids()

        self.assertEqual(ids, [1, 2, 3])
        self.assertEqual(mock_session.get.call_count, 2)
        client.close()

    @patch("src.hn_api.requests.Session")
    def test_context_manager(self, mock_session_class) -> None:
        """Test client works as context manager."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = [1, 2, 3]
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        with HackerNewsClient() as client:
            ids = client.get_newest_story_ids()
            self.assertEqual(ids, [1, 2, 3])

        mock_session.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
