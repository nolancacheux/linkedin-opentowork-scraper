"""Configuration management."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""

    # Delay settings
    MIN_DELAY: float = float(os.getenv("MIN_DELAY", "2"))
    MAX_DELAY: float = float(os.getenv("MAX_DELAY", "5"))
    SCROLL_PAUSE: float = float(os.getenv("SCROLL_PAUSE", "1"))
    LONG_PAUSE_INTERVAL: int = int(os.getenv("LONG_PAUSE_INTERVAL", "50"))
    LONG_PAUSE_DURATION: float = float(os.getenv("LONG_PAUSE_DURATION", "30"))

    # Safety limits
    MAX_PROFILES_PER_SESSION: int = int(os.getenv("MAX_PROFILES_PER_SESSION", "500"))

    # Browser
    CHROME_USER_DATA_DIR: str = os.getenv("CHROME_USER_DATA_DIR", "")

    # LinkedIn URLs
    LINKEDIN_BASE_URL: str = "https://www.linkedin.com"
    LINKEDIN_SEARCH_URL: str = "https://www.linkedin.com/search/results/people/"

    # Output
    OUTPUT_DIR: Path = Path("output")

    @classmethod
    def get_output_dir(cls) -> Path:
        """Get output directory, creating it if necessary."""
        cls.OUTPUT_DIR.mkdir(exist_ok=True)
        return cls.OUTPUT_DIR


config = Config()
