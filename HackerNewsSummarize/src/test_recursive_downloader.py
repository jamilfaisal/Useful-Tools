import unittest
from unittest.mock import MagicMock, patch
from src.recursive_downloader import RecursiveDownloader, DownloadedStory, DownloadedComment
from src.hn_api import HackerNewsItem, ItemType, Story, Comment


class TestRecursiveDownloader(unittest.TestCase):

    def setUp(self):
        self.mock_client = MagicMock()
        self.downloader = RecursiveDownloader()
        self.downloader.client = self.mock_client

    def test_download_story_with_no_comments(self) -> None:
        story_id = 123
        mock_story = Story(id=story_id, item_type=ItemType.STORY, kids=[])
        self.mock_client.get_item.return_value = mock_story

        downloaded_story = self.downloader.download_story_with_comments(story_id)

        self.assertIsNotNone(downloaded_story)
        assert isinstance(downloaded_story, DownloadedStory)
        self.assertEqual(downloaded_story.id, story_id)
        self.assertEqual(len(downloaded_story.comments), 0)
        self.mock_client.get_item.assert_called_once_with(story_id)

    def test_download_story_with_single_level_comments(self) -> None:
        story_id = 100
        comment_id_1 = 101
        comment_id_2 = 102

        mock_story = Story(id=story_id, item_type=ItemType.STORY, kids=[comment_id_1, comment_id_2])
        mock_comment_1 = Comment(id=comment_id_1, item_type=ItemType.COMMENT, by="user1", text="Comment 1")
        mock_comment_2 = Comment(id=comment_id_2, item_type=ItemType.COMMENT, by="user2", text="Comment 2")

        self.mock_client.get_item.side_effect = [
            mock_story, mock_comment_1, mock_comment_2
        ]

        downloaded_story = self.downloader.download_story_with_comments(story_id)

        self.assertIsNotNone(downloaded_story)
        assert isinstance(downloaded_story, DownloadedStory)
        self.assertEqual(downloaded_story.id, story_id)
        self.assertEqual(len(downloaded_story.comments), 2)

        self.assertEqual(downloaded_story.comments[0].id, comment_id_1)
        self.assertEqual(downloaded_story.comments[0].by, "user1")
        self.assertEqual(downloaded_story.comments[0].text, "Comment 1")
        self.assertEqual(downloaded_story.comments[0].parent, story_id)

        self.assertEqual(downloaded_story.comments[1].id, comment_id_2)
        self.assertEqual(downloaded_story.comments[1].by, "user2")
        self.assertEqual(downloaded_story.comments[1].text, "Comment 2")
        self.assertEqual(downloaded_story.comments[1].parent, story_id)

        self.assertEqual(self.mock_client.get_item.call_count, 3)
        self.mock_client.get_item.assert_any_call(story_id)
        self.mock_client.get_item.assert_any_call(comment_id_1)
        self.mock_client.get_item.assert_any_call(comment_id_2)

    def test_download_story_with_nested_comments(self) -> None:
        story_id = 200
        comment_id_a = 201
        comment_id_b = 202
        comment_id_c = 203

        mock_story = Story(id=story_id, item_type=ItemType.STORY, kids=[comment_id_a])
        mock_comment_a = Comment(id=comment_id_a, item_type=ItemType.COMMENT, kids=[comment_id_b])
        mock_comment_b = Comment(id=comment_id_b, item_type=ItemType.COMMENT, kids=[comment_id_c])
        mock_comment_c = Comment(id=comment_id_c, item_type=ItemType.COMMENT, kids=[])

        self.mock_client.get_item.side_effect = [
            mock_story, mock_comment_a, mock_comment_b, mock_comment_c
        ]

        downloaded_story = self.downloader.download_story_with_comments(story_id)

        self.assertIsNotNone(downloaded_story)
        assert isinstance(downloaded_story, DownloadedStory)
        self.assertEqual(downloaded_story.id, story_id)
        self.assertEqual(len(downloaded_story.comments), 1)

        comment_a = downloaded_story.comments[0]
        self.assertEqual(comment_a.id, comment_id_a)
        self.assertEqual(comment_a.parent, story_id)
        self.assertEqual(len(comment_a.children), 1)

        comment_b = comment_a.children[0]
        self.assertEqual(comment_b.id, comment_id_b)
        self.assertEqual(comment_b.parent, comment_id_a)
        self.assertEqual(len(comment_b.children), 1)

        comment_c = comment_b.children[0]
        self.assertEqual(comment_c.id, comment_id_c)
        self.assertEqual(comment_c.parent, comment_id_b)
        self.assertEqual(len(comment_c.children), 0)

        self.assertEqual(self.mock_client.get_item.call_count, 4)

    def test_ignore_deleted_items(self) -> None:
        story_id = 300
        comment_id_deleted = 301
        comment_id_valid = 302

        mock_story = Story(id=story_id, item_type=ItemType.STORY, kids=[comment_id_deleted, comment_id_valid])
        mock_comment_deleted = Comment(id=comment_id_deleted, item_type=ItemType.COMMENT, deleted=True)
        mock_comment_valid = Comment(id=comment_id_valid, item_type=ItemType.COMMENT)

        self.mock_client.get_item.side_effect = [
            mock_story, mock_comment_deleted, mock_comment_valid
        ]

        downloaded_story = self.downloader.download_story_with_comments(story_id)

        self.assertIsNotNone(downloaded_story)
        assert isinstance(downloaded_story, DownloadedStory)
        self.assertEqual(len(downloaded_story.comments), 1)
        self.assertEqual(downloaded_story.comments[0].id, comment_id_valid)
        self.assertEqual(downloaded_story.comments[0].parent, story_id)

    def test_avoid_duplicate_downloads(self) -> None:
        story_id = 400
        comment_id_1 = 401

        mock_story = Story(id=story_id, item_type=ItemType.STORY, kids=[comment_id_1, comment_id_1])  # Duplicate kid ID
        mock_comment_1 = Comment(id=comment_id_1, item_type=ItemType.COMMENT)

        self.mock_client.get_item.side_effect = [
            mock_story, mock_comment_1  # Only one call for comment_id_1
        ]

        downloaded_story = self.downloader.download_story_with_comments(story_id)

        self.assertIsNotNone(downloaded_story)
        assert isinstance(downloaded_story, DownloadedStory)
        self.assertEqual(len(downloaded_story.comments), 1)
        self.assertEqual(downloaded_story.comments[0].id, comment_id_1)

        # Ensure get_item was only called once for comment_id_1
        self.assertEqual(self.mock_client.get_item.call_count, 2)
        self.mock_client.get_item.assert_any_call(story_id)
        self.mock_client.get_item.assert_any_call(comment_id_1)

    def test_ignore_dead_items(self) -> None:
        story_id = 500
        comment_id_dead = 501
        comment_id_valid = 502

        mock_story = Story(id=story_id, item_type=ItemType.STORY, kids=[comment_id_dead, comment_id_valid])
        mock_comment_dead = None  # Simulate a dead item (API returns None)
        mock_comment_valid = Comment(id=comment_id_valid, item_type=ItemType.COMMENT)

        self.mock_client.get_item.side_effect = [
            mock_story, mock_comment_dead, mock_comment_valid
        ]

        downloaded_story = self.downloader.download_story_with_comments(story_id)

        self.assertIsNotNone(downloaded_story)
        assert isinstance(downloaded_story, DownloadedStory)
        self.assertEqual(len(downloaded_story.comments), 1)
        self.assertEqual(downloaded_story.comments[0].id, comment_id_valid)
        self.assertEqual(downloaded_story.comments[0].parent, story_id)

    def test_ignore_dead_flagged_items(self) -> None:
        story_id = 505
        comment_id_dead = 506
        comment_id_valid = 507

        mock_story = Story(id=story_id, item_type=ItemType.STORY, kids=[comment_id_dead, comment_id_valid])
        mock_comment_dead = Comment(id=comment_id_dead, item_type=ItemType.COMMENT, dead=True)
        mock_comment_valid = Comment(id=comment_id_valid, item_type=ItemType.COMMENT)

        self.mock_client.get_item.side_effect = [
            mock_story, mock_comment_dead, mock_comment_valid
        ]

        downloaded_story = self.downloader.download_story_with_comments(story_id)

        self.assertIsNotNone(downloaded_story)
        assert isinstance(downloaded_story, DownloadedStory)
        self.assertEqual(len(downloaded_story.comments), 1)
        self.assertEqual(downloaded_story.comments[0].id, comment_id_valid)

    def test_retain_author_timestamp_id_parent_text_children(self) -> None:
        story_id = 600
        comment_id_1 = 601
        comment_id_2 = 602

        mock_story = Story(id=story_id, item_type=ItemType.STORY, by="story_author", time=1678886400, text="Story text",
                           kids=[comment_id_1])
        mock_comment_1 = Comment(id=comment_id_1, item_type=ItemType.COMMENT, by="comment_author_1", time=1678886500,
                                 text="Comment 1 text", kids=[comment_id_2])
        mock_comment_2 = Comment(id=comment_id_2, item_type=ItemType.COMMENT, by="comment_author_2", time=1678886600,
                                 text="Comment 2 text", kids=[])

        self.mock_client.get_item.side_effect = [
            mock_story, mock_comment_1, mock_comment_2
        ]

        downloaded_story = self.downloader.download_story_with_comments(story_id)

        self.assertIsNotNone(downloaded_story)
        assert isinstance(downloaded_story, DownloadedStory)
        self.assertEqual(downloaded_story.id, story_id)
        self.assertEqual(downloaded_story.by, "story_author")
        self.assertEqual(downloaded_story.time, 1678886400)
        self.assertEqual(downloaded_story.text, "Story text")
        self.assertEqual(len(downloaded_story.comments), 1)

        comment_1 = downloaded_story.comments[0]
        self.assertEqual(comment_1.id, comment_id_1)
        self.assertEqual(comment_1.by, "comment_author_1")
        self.assertEqual(comment_1.time, 1678886500)
        self.assertEqual(comment_1.text, "Comment 1 text")
        self.assertEqual(comment_1.parent, story_id)
        self.assertEqual(len(comment_1.children), 1)

        comment_2 = comment_1.children[0]
        self.assertEqual(comment_2.id, comment_id_2)
        self.assertEqual(comment_2.by, "comment_author_2")
        self.assertEqual(comment_2.time, 1678886600)
        self.assertEqual(comment_2.text, "Comment 2 text")
        self.assertEqual(comment_2.parent, comment_id_1)
        self.assertEqual(len(comment_2.children), 0)

    def test_handle_api_none_response_for_story(self) -> None:
        story_id = 700
        self.mock_client.get_item.return_value = None

        downloaded_story = self.downloader.download_story_with_comments(story_id)
        self.assertIsNone(downloaded_story)
        self.mock_client.get_item.assert_called_once_with(story_id)

    def test_ignore_job_items(self) -> None:
        story_id = 800
        job_id = 801
        comment_id = 802

        mock_story = Story(id=story_id, item_type=ItemType.STORY, kids=[job_id, comment_id])
        mock_job = HackerNewsItem(id=job_id, item_type=ItemType.JOB)
        mock_comment = Comment(id=comment_id, item_type=ItemType.COMMENT)

        self.mock_client.get_item.side_effect = [
            mock_story, mock_job, mock_comment
        ]

        downloaded_story = self.downloader.download_story_with_comments(story_id)

        self.assertIsNotNone(downloaded_story)
        assert isinstance(downloaded_story, DownloadedStory)
        self.assertEqual(len(downloaded_story.comments), 1)
        self.assertEqual(downloaded_story.comments[0].id, comment_id)


if __name__ == '__main__':
    unittest.main()
