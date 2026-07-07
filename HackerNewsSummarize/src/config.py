"""Configuration settings for the Hacker News Daily Companion."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    """Configuration settings for the application."""

    # Number of days to look back for stories
    days_to_look_back: int = 1

    # Minimum score threshold for stories (set to 0 to disable)
    minimum_score: int = 0

    # Use percentage-based filtering (top X% by score)
    # Set to 0 to disable, otherwise use with minimum_score=0
    top_percent_by_score: float = 0.0

    # Output directory for generated files
    output_dir: Path = Path("output")

    # Cache database path
    cache_db_path: Path = Path("output") / "cache.db"

    # Hacker News API base URL
    hn_api_base_url: str = "https://hacker-news.firebaseio.com/v0"

    # Request timeout in seconds
    request_timeout: int = 30


def get_config() -> Config:
    """Get the default configuration."""
    return Config()
