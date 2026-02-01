"""CSV export functionality."""

import csv
from datetime import datetime
from pathlib import Path
from typing import List

from ..config import config
from ..scraper.profile_parser import ProfileData
from ..utils.logger import get_logger

logger = get_logger()


class CSVExporter:
    """Export profile data to CSV files."""

    HEADERS = [
        "first_name",
        "last_name",
        "full_name",
        "headline",
        "current_company",
        "location",
        "profile_url",
        "is_open_to_work",
        "scraped_at",
    ]

    @classmethod
    def export(
        cls,
        profiles: List[ProfileData],
        filename: str = None,
        output_dir: Path = None,
    ) -> Path:
        """
        Export profiles to CSV file.

        Args:
            profiles: List of ProfileData objects
            filename: Output filename (auto-generated if not provided)
            output_dir: Output directory (default: config.OUTPUT_DIR)

        Returns:
            Path to the created CSV file
        """
        output_dir = output_dir or config.get_output_dir()

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"linkedin_opentowork_{timestamp}.csv"

        filepath = output_dir / filename

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=cls.HEADERS)
            writer.writeheader()

            for profile in profiles:
                writer.writerow(profile.to_dict())

        logger.info(f"Exported {len(profiles)} profiles to {filepath}")
        return filepath

    @classmethod
    def append(cls, profile: ProfileData, filepath: Path) -> None:
        """
        Append a single profile to an existing CSV file.

        Args:
            profile: ProfileData object
            filepath: Path to existing CSV file
        """
        file_exists = filepath.exists()

        with open(filepath, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=cls.HEADERS)

            if not file_exists:
                writer.writeheader()

            writer.writerow(profile.to_dict())
